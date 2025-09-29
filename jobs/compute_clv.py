"""Compute closing-line value (CLV) deltas between entries and closing lines."""

from __future__ import annotations

import argparse
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

from utils.odds import american_to_decimal, implied_from_decimal, logit

DEFAULT_DB = Path("storage/odds.db")
DEFAULT_LINE_TOLERANCE = float(os.getenv("CLV_LINE_TOLERANCE", 0.5))


@dataclass
class CLVSummary:
    matched: int
    total_edges: int
    coverage: float
    delta_prob_mean: float
    beat_close_rate: float


def _load_table(con: sqlite3.Connection, query: str) -> pd.DataFrame:
    try:
        return pd.read_sql(query, con)
    except Exception:
        return pd.DataFrame()


def _prepare_edges(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()
    working["side"] = working.get("odds_side", "").astype(str).str.lower()
    working["line_entry"] = pd.to_numeric(working.get("line"), errors="coerce")
    working["entry_odds"] = pd.to_numeric(working.get("odds"), errors="coerce")
    working["entry_prob_fair"] = pd.to_numeric(working.get("fair_prob"), errors="coerce")
    if "entry_prob_fair" in working:
        working["entry_prob_fair"] = working["entry_prob_fair"].where(
            working["entry_prob_fair"].notna()
        )
    fallback = pd.to_numeric(working.get("implied_prob"), errors="coerce")
    working["entry_prob_fair"] = working["entry_prob_fair"].fillna(fallback)
    working["book_entry"] = working.get("book")
    working = working.drop(
        columns=["line", "odds", "fair_prob", "implied_prob", "book"], errors="ignore"
    )
    return working


def _prepare_closings(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()
    working["side"] = working.get("side", "").astype(str).str.lower()
    working["line_close"] = pd.to_numeric(working.get("line"), errors="coerce")
    working["close_odds"] = pd.to_numeric(working.get("odds_american"), errors="coerce")
    working["close_prob_fair"] = pd.to_numeric(working.get("fair_prob_close"), errors="coerce")
    working["close_prob_fair"] = working["close_prob_fair"].where(
        working["close_prob_fair"].notna()
    )
    fallback = pd.to_numeric(working.get("implied_prob"), errors="coerce")
    working["close_prob_fair"] = working["close_prob_fair"].fillna(fallback)
    working["ts_close"] = pd.to_datetime(working.get("ts_close"), errors="coerce", utc=True)
    working["book_close"] = working.get("book")
    working = working.drop(
        columns=["line", "book", "odds_american", "fair_prob_close", "implied_prob"],
        errors="ignore",
    )
    return working


def price_is_better(entry_odds: Optional[float], close_odds: Optional[float]) -> Optional[int]:
    """Return 1 if entry odds are strictly better than closing odds, else 0/None."""

    if entry_odds is None or close_odds is None:
        return None
    try:
        entry_val = float(entry_odds)
        close_val = float(close_odds)
        if np.isnan(entry_val) or np.isnan(close_val):
            return None
        entry_decimal = american_to_decimal(int(entry_val))
        close_decimal = american_to_decimal(int(close_val))
    except Exception:
        return None
    epsilon = 1e-9
    return 1 if (entry_decimal - close_decimal) >= -epsilon else 0


def _match_edges_with_closing(
    edges: pd.DataFrame,
    closings: pd.DataFrame,
    tolerance: float,
) -> pd.DataFrame:
    if edges.empty or closings.empty:
        return pd.DataFrame()

    primary = closings[closings.get("is_primary", 0) == 1]
    if primary.empty:
        primary = closings

    merged = edges.merge(primary, on=["event_id", "market", "side"], suffixes=("_entry", "_close"))
    merged["line_diff"] = (merged["line_entry"] - merged["line_close"]).abs()
    merged = merged[merged["line_diff"] <= tolerance]
    if merged.empty:
        return merged

    merged = merged.sort_values(["edge_id", "line_diff", "ts_close"])
    result = merged.groupby("edge_id", as_index=False, sort=False).first().reset_index(drop=True)
    if "book_close" not in result.columns and "book_y" in result.columns:
        result["book_close"] = result["book_y"]
    if "book_entry" not in result.columns and "book_x" in result.columns:
        result["book_entry"] = result["book_x"]
    return result


def _compute_clv_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    working = df.copy()

    def _delta_prob(row: pd.Series) -> Optional[float]:
        entry = row.get("entry_prob_fair")
        close = row.get("close_prob_fair")
        if pd.isna(entry) or pd.isna(close):
            return None
        return float(close - entry)

    def _delta_logit(row: pd.Series) -> Optional[float]:
        entry = row.get("entry_prob_fair")
        close = row.get("close_prob_fair")
        if pd.isna(entry) or pd.isna(close):
            return None
        if not 0 < float(entry) < 1 or not 0 < float(close) < 1:
            return None
        try:
            return float(logit(close) - logit(entry))
        except ValueError:
            return None

    working["delta_prob"] = working.apply(_delta_prob, axis=1)
    working["delta_logit"] = working.apply(_delta_logit, axis=1)
    working["clv_cents"] = working["close_odds"].fillna(0) - working["entry_odds"].fillna(0)
    working["beat_close"] = working.apply(
        lambda row: price_is_better(row.get("entry_odds"), row.get("close_odds")),
        axis=1,
    )
    working["match_tolerance"] = working["line_diff"]
    return working


def run(database_path: Path, line_tolerance: float = DEFAULT_LINE_TOLERANCE) -> CLVSummary:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(database_path)
    con.execute("PRAGMA journal_mode=WAL;")

    edges = _load_table(
        con,
        """
        SELECT edge_id, event_id, market, odds_side, line, odds,
               fair_prob, implied_prob, book
        FROM edges
        """,
    )
    closings = _load_table(
        con,
        """
        SELECT event_id, market, side, line, book, odds_american,
               implied_prob, fair_prob_close, ts_close, is_primary
        FROM closing_lines
        """,
    )

    edges = _prepare_edges(edges)
    closings = _prepare_closings(closings)

    if edges.empty or closings.empty:
        print("No edges or closing lines available; skipping CLV computation.")
        return CLVSummary(
            matched=0,
            total_edges=len(edges),
            coverage=0.0,
            delta_prob_mean=float("nan"),
            beat_close_rate=float("nan"),
        )

    matched = _match_edges_with_closing(edges, closings, line_tolerance)
    matched = _compute_clv_rows(matched)
    if matched.empty:
        print("No matching closing lines within tolerance; nothing to log.")
        return CLVSummary(
            matched=0,
            total_edges=len(edges),
            coverage=0.0,
            delta_prob_mean=float("nan"),
            beat_close_rate=float("nan"),
        )

    payload = []
    for _, row in matched.iterrows():
        payload.append(
            (
                row.get("edge_id"),
                None,
                row.get("event_id"),
                row.get("market"),
                row.get("side"),
                row.get("line_entry"),
                row.get("entry_odds"),
                row.get("close_odds"),
                row.get("entry_prob_fair"),
                row.get("close_prob_fair"),
                row.get("delta_prob"),
                row.get("delta_logit"),
                row.get("clv_cents"),
                row.get("beat_close"),
                row.get("book_close"),
                row.get("match_tolerance"),
            )
        )

    cur = con.cursor()
    for edge_id, *_ in payload:
        cur.execute("DELETE FROM clv_log WHERE edge_id = ?", (edge_id,))

    cur.executemany(
        """
        INSERT INTO clv_log (
            edge_id, bet_id, event_id, market, side, line,
            entry_odds, close_odds, entry_prob_fair, close_prob_fair,
            delta_prob, delta_logit, clv_cents, beat_close,
            primary_book, match_tolerance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        payload,
    )
    con.commit()

    matched_count = len(matched)
    total_edges = len(edges)
    coverage = matched_count / total_edges if total_edges else 0.0
    delta_prob_mean = (
        float(matched["delta_prob"].dropna().mean())
        if not matched["delta_prob"].dropna().empty
        else float("nan")
    )
    beats = matched["beat_close"].dropna()
    beat_rate = float(beats.mean()) if not beats.empty else float("nan")

    summary = CLVSummary(
        matched=matched_count,
        total_edges=total_edges,
        coverage=coverage,
        delta_prob_mean=delta_prob_mean,
        beat_close_rate=beat_rate,
    )

    print(
        "CLV summary → matched={matched}/{total} ({coverage:.1%}) | mean Δprob={dp:.4f} | beat_close={beat:.1%}".format(
            matched=summary.matched,
            total=summary.total_edges,
            coverage=summary.coverage,
            dp=summary.delta_prob_mean if not np.isnan(summary.delta_prob_mean) else float("nan"),
            beat=summary.beat_close_rate if not np.isnan(summary.beat_close_rate) else float("nan"),
        )
    )

    con.close()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute CLV deltas compared to closing lines.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument(
        "--line-tolerance",
        type=float,
        default=DEFAULT_LINE_TOLERANCE,
        help="Maximum absolute difference in line for matching closes",
    )
    args = parser.parse_args()

    run(args.db, args.line_tolerance)


if __name__ == "__main__":
    main()

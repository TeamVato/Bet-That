"""Explain why a given Streamlit table is empty by inspecting applied filters."""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd


@dataclass
class Filters:
    seasons: Sequence[int]
    odds_min: int
    odds_max: int
    ev_min: float
    hide_stale: bool
    best_priced_only: bool
    pos: Optional[str] = None
    book: Optional[str] = None


def _as_bool(val: object) -> bool:
    """Return False for NA/None, otherwise bool(val)."""
    if pd.isna(val):
        return False
    return bool(val)


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path, timeout=5.0)
    con.row_factory = sqlite3.Row
    return con


def _table_exists(con: sqlite3.Connection, name: str) -> bool:
    cur = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;",
        (name,),
    )
    return cur.fetchone() is not None


def _count_scalar(con: sqlite3.Connection, sql: str) -> int:
    cur = con.execute(sql)
    row = cur.fetchone()
    return int(row[0] if row and row[0] is not None else 0)


def coverage_checks(con: sqlite3.Connection) -> Dict[str, int]:
    """Return lightweight counts for optional tables to surface diagnostics."""
    out: Dict[str, int] = {}
    if _table_exists(con, "weather"):
        out["weather_rows"] = _count_scalar(con, "SELECT COUNT(*) FROM weather;")
    if _table_exists(con, "injuries"):
        out["injury_rows"] = _count_scalar(con, "SELECT COUNT(*) FROM injuries;")
    if _table_exists(con, "odds_csv_raw"):
        out["odds_rows"] = _count_scalar(con, "SELECT COUNT(*) FROM odds_csv_raw;")
    if _table_exists(con, "current_best_lines"):
        out["best_rows"] = _count_scalar(con, "SELECT COUNT(*) FROM current_best_lines;")
        out["best_stale"] = _count_scalar(
            con,
            "SELECT COUNT(*) FROM current_best_lines WHERE COALESCE(stale,0)=1;",
        )
    return out


def stepwise_drop(edges_all: pd.DataFrame, filters: Filters) -> List[Tuple[str, int, str]]:
    """Apply each filter sequentially and record row drops with hints."""
    report: List[Tuple[str, int, str]] = []
    working = edges_all.copy()

    def note(label: str, before: int, after: int, hint: str) -> None:
        removed = max(0, before - after)
        if removed > 0:
            report.append((label, removed, hint))

    if working.empty:
        report.append(
            (
                "No edges available",
                0,
                "Import odds and recompute edges (./BetThat or make edges).",
            )
        )
        return report

    # Position (tab context)
    if filters.pos:
        before = len(working)
        working = working[working.get("pos").fillna("") == filters.pos]
        note(
            f"Position filter ({filters.pos})",
            before,
            len(working),
            "Switch to another position tab or ingest broader markets.",
        )

    # Sportsbook (tab context)
    if filters.book:
        before = len(working)
        working = working[working.get("book").fillna("") == filters.book]
        note(
            f"Sportsbook filter ({filters.book})",
            before,
            len(working),
            "Clear the sportsbook picker or load more odds for that book.",
        )

    # Season filter
    if filters.seasons:
        before = len(working)
        season_col = working.get("season")
        if season_col is not None:
            working = working[season_col.isin(filters.seasons)]
        note(
            "Season filter",
            before,
            len(working),
            "Add more seasons in the sidebar or ensure season columns were inferred.",
        )

    # Odds range
    odds_series = working.get("odds")
    if odds_series is not None:
        before = len(working)
        working = working[odds_series.between(filters.odds_min, filters.odds_max, inclusive="both")]
        note("Odds range filter", before, len(working), "Widen the odds slider range.")

    # EV threshold
    ev_series = working.get("ev_per_dollar")
    if ev_series is not None:
        before = len(working)
        working = working[ev_series >= filters.ev_min]
        note("EV threshold", before, len(working), "Lower the EV minimum in the sidebar.")

    # Hide stale
    if filters.hide_stale:
        before = len(working)
        stale_col = working.get("stale")
        if stale_col is None:
            stale_col = working.get("is_stale")
        if stale_col is not None:
            working = working[stale_col.fillna(0).astype(int) == 0]
        note(
            "Hide stale",
            before,
            len(working),
            "Uncheck ‘Hide stale lines’ or import fresh odds.",
        )

    # Best priced only
    if filters.best_priced_only:
        before = len(working)
        best_col = working.get("best_priced")
        if best_col is None:
            best_col = working.get("is_best")
        if best_col is not None:
            working = working[best_col.fillna(0).astype(int) == 1]
        note(
            "Best-priced only",
            before,
            len(working),
            "Uncheck ‘Show only best-priced edges’ or inspect line shopping.",
        )

    # Join diagnostics (informational only)
    def_code_series = edges_all.get("opponent_def_code")
    if def_code_series is not None:
        missing_def = int(
            (
                def_code_series.isna()
                | (def_code_series.astype(str).str.strip() == "")
            ).sum()
        )
        if missing_def:
            report.append(
                (
                    "Missing opponent_def_code",
                    missing_def,
                    "Run `python jobs/build_defense_ratings.py` then recompute edges.",
                )
            )
    tier_series = edges_all.get("def_tier")
    if tier_series is not None:
        missing_tier = int(
            (
                tier_series.isna()
                | (tier_series.astype(str).str.strip() == "")
            ).sum()
        )
        if missing_tier:
            report.append(
                (
                    "Missing defense tier",
                    missing_tier,
                    "Verify `defense_ratings` coverage for the selected seasons.",
                )
            )

    return report


def format_hints(
    report: Sequence[Tuple[str, int, str]],
    max_items: int = 6,
) -> List[str]:
    """Format drop reasons into human-readable bullet strings."""
    ranked = sorted(report, key=lambda item: (-item[1], item[0]))[:max_items]
    if not ranked:
        return [
            "• No filter stood out; widen filters or rerun odds ingestion for fresh data.",
        ]
    bullets: List[str] = []
    for label, removed, hint in ranked:
        qty = "1 row" if removed == 1 else f"{removed} rows"
        suffix = f" — Fix: {hint}" if hint else ""
        bullets.append(f"• {label} removed {qty}{suffix}")
    return bullets


def explain_empty(
    edges_all: pd.DataFrame,
    filters: Filters,
    database_path: os.PathLike[str] | str,
) -> Dict[str, List[str]]:
    """Return tip bullets and optional coverage extras explaining emptiness."""
    report = stepwise_drop(edges_all, filters)
    tips = format_hints(report)
    extras: List[str] = []
    try:
        with _connect(str(database_path)) as con:
            coverage = coverage_checks(con)
    except Exception:
        coverage = {}
    if coverage:
        extras.append("Coverage: " + ", ".join(f"{k}={v}" for k, v in sorted(coverage.items())))
    return {"tips": tips, "extras": extras}


__all__ = ["Filters", "explain_empty", "format_hints", "stepwise_drop"]

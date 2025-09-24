"""Edge computation by combining model projections with sportsbook odds."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.stats import norm

from engine import odds_math


@dataclass
class EdgeEngineConfig:
    database_path: Path
    export_dir: Path = Path("storage/exports")
    kelly_cap: float = 0.05


class EdgeEngine:
    """Compute edges for QB prop markets."""

    def __init__(self, config: EdgeEngineConfig) -> None:
        self.config = config
        self.config.export_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_dataframe(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        merged = props_df.merge(
            projections_df,
            on=["event_id", "player"],
            how="left",
            suffixes=("_props", "_proj"),
        )
        merged["mu"] = merged["mu"].fillna(merged["line"])
        merged["sigma"] = merged["sigma"].fillna(55.0)
        merged["sigma"] = merged["sigma"].clip(lower=35.0)
        return merged

    def compute_edges(self, props_df: pd.DataFrame, projections_df: pd.DataFrame) -> pd.DataFrame:
        df = self._prepare_dataframe(props_df, projections_df)
        rows = []
        for _, row in df.iterrows():
            if pd.isna(row.get("over_odds")) or pd.isna(row.get("under_odds")):
                continue
            mu = float(row.get("mu"))
            sigma = float(row.get("sigma"))
            line = float(row.get("line"))
            if sigma <= 0:
                sigma = 55.0
            distribution = norm(loc=mu, scale=sigma)
            p_over = float(1 - distribution.cdf(line))
            p_under = float(1 - p_over)
            vig_probs = odds_math.no_vig_two_way(
                int(row.get("over_odds")),
                int(row.get("under_odds")),
                labels=("over", "under"),
            )
            ev_over = odds_math.ev_per_dollar(p_over, int(row.get("over_odds")))
            ev_under = odds_math.ev_per_dollar(p_under, int(row.get("under_odds")))
            kelly_over = min(
                self.config.kelly_cap,
                odds_math.kelly_fraction(p_over, int(row.get("over_odds"))),
            )
            kelly_under = min(
                self.config.kelly_cap,
                odds_math.kelly_fraction(p_under, int(row.get("under_odds"))),
            )
            if ev_over >= ev_under:
                best_side = "over"
                best_odds = int(row.get("over_odds"))
                model_p = p_over
                ev = ev_over
                kelly = kelly_over
            else:
                best_side = "under"
                best_odds = int(row.get("under_odds"))
                model_p = p_under
                ev = ev_under
                kelly = kelly_under
            strategy = "AltQB" if abs(line - mu) >= 10 else "BaselineQB"
            rows.append(
                {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "event_id": row.get("event_id"),
                    "book": row.get("book"),
                    "player": row.get("player"),
                    "market": row.get("market"),
                    "line": line,
                    "odds_side": best_side,
                    "odds": best_odds,
                    "model_p": model_p,
                    "ev_per_dollar": ev,
                    "kelly_frac": kelly,
                    "strategy_tag": strategy,
                    "mu": mu,
                    "sigma": sigma,
                    "p_over": p_over,
                    "p_under": p_under,
                    "vig_p_over": vig_probs["over"],
                    "vig_p_under": vig_probs["under"],
                }
            )
        edges_df = pd.DataFrame(rows)
        return edges_df

    def persist_edges(self, edges_df: pd.DataFrame) -> None:
        if edges_df.empty:
            print("No edges to persist.")
            return
        with sqlite3.connect(self.config.database_path) as conn:
            cursor = conn.cursor()
            for row in edges_df.to_dict("records"):
                cursor.execute(
                    """
                    INSERT INTO edges (
                        created_at, event_id, book, player, market, line, odds_side, odds,
                        model_p, ev_per_dollar, kelly_frac, strategy_tag
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["created_at"],
                        row["event_id"],
                        row["book"],
                        row["player"],
                        row["market"],
                        row["line"],
                        row["odds_side"],
                        row["odds"],
                        row["model_p"],
                        row["ev_per_dollar"],
                        row["kelly_frac"],
                        row["strategy_tag"],
                    ),
                )
            conn.commit()
        print(f"Inserted {len(edges_df)} edges into the database")

    def export(self, edges_df: pd.DataFrame) -> None:
        if edges_df.empty:
            print("No edges to export.")
            return
        csv_path = self.config.export_dir / "edges_latest.csv"
        parquet_path = self.config.export_dir / "edges_latest.parquet"
        edges_df.to_csv(csv_path, index=False)
        try:
            edges_df.to_parquet(parquet_path, index=False)
        except Exception as exc:
            print(f"Failed to write parquet export: {exc}")
        print(f"Exports written to {csv_path} and {parquet_path}")

"""Utilities for line shopping across sportsbooks."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from adapters.odds.the_odds_api import compute_current_best_lines


def load_snapshots(database_path: Path) -> pd.DataFrame:
    with sqlite3.connect(database_path) as conn:
        return pd.read_sql_query("SELECT * FROM odds_snapshots", conn)


def update_best_lines(database_path: Path) -> pd.DataFrame:
    df = load_snapshots(database_path)
    best = compute_current_best_lines(df)
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        for row in best.to_dict("records"):
            cursor.execute(
                """
                INSERT OR REPLACE INTO current_best_lines (
                    event_id, market_key, outcome, best_book, best_price, best_points, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["event_id"],
                    row["market_key"],
                    row["outcome"],
                    row["best_book"],
                    int(row["best_price"]),
                    row.get("best_points"),
                    row.get("fetched_at"),
                ),
            )
        conn.commit()
    return best


def export_line_shop(best_df: pd.DataFrame, export_dir: Path = Path("storage/exports")) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / "line_shopping.csv"
    best_df.to_csv(path, index=False)
    return path

"""CSV-based odds provider for QB passing props."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from adapters.odds.base import OddsAdapter

DEFAULT_CSV_PATH = Path("storage/sample_odds_qb_yards.csv")


class CsvQBPropsAdapter(OddsAdapter):
    """Load QB prop odds from a local CSV file."""

    def __init__(self, csv_path: Optional[Path] = None) -> None:
        self.csv_path = csv_path or DEFAULT_CSV_PATH

    def fetch(self, *_, **__) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"Props CSV not found at {self.csv_path}. Copy the sample or supply your own."
            )
        df = pd.read_csv(self.csv_path)
        df["fetched_at"] = datetime.now(timezone.utc).isoformat()
        expected_cols = {
            "event_id",
            "book",
            "market",
            "player",
            "line",
            "over_odds",
            "under_odds",
            "season",
            "def_team",
        }
        missing = expected_cols.difference(df.columns)
        if missing:
            raise ValueError(f"Props CSV missing required columns: {sorted(missing)}")
        df["line"] = pd.to_numeric(df["line"], errors="coerce")
        df["over_odds"] = pd.to_numeric(df["over_odds"], errors="coerce").astype("Int64")
        df["under_odds"] = pd.to_numeric(df["under_odds"], errors="coerce").astype("Int64")
        return df

    def persist(self, df: pd.DataFrame, database_path: Path) -> None:
        if df.empty:
            return
        database_path.parent.mkdir(parents=True, exist_ok=True)
        import sqlite3

        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            for row in df.to_dict("records"):
                cursor.execute(
                    """
                    INSERT INTO qb_props_odds (
                        fetched_at, event_id, player, market, line, over_odds, under_odds, book, season, def_team
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["fetched_at"],
                        row["event_id"],
                        row["player"],
                        row["market"],
                        row["line"],
                        int(row["over_odds"]) if pd.notna(row["over_odds"]) else None,
                        int(row["under_odds"]) if pd.notna(row["under_odds"]) else None,
                        row["book"],
                        int(row.get("season")) if pd.notna(row.get("season")) else None,
                        row.get("def_team"),
                    ),
                )
            conn.commit()


def load_qb_props(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Convenience function to load the props CSV without instantiating the adapter."""
    return CsvQBPropsAdapter(csv_path).fetch()

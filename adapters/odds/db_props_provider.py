"""Database-based odds provider that reads from current_best_lines table."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from adapters.odds.base import OddsAdapter
from utils.teams import infer_offense_team, normalize_team_code, parse_event_id
from engine.week_populator import populate_week_from_schedule


class DbPropsAdapter(OddsAdapter):
    """Load prop odds from the database current_best_lines table."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or Path("storage/odds.db")

    def fetch(self, *_, **__) -> pd.DataFrame:
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            # Read from current_best_lines table
            query = """
                SELECT
                    event_id,
                    player,
                    market,
                    line,
                    over_odds,
                    under_odds,
                    book,
                    season,
                    week,
                    team_code,
                    opponent_def_code,
                    pos,
                    is_stale,
                    updated_at,
                    commence_time,
                    home_team,
                    away_team
                FROM current_best_lines
                WHERE event_id IS NOT NULL
                AND player IS NOT NULL
                AND market IS NOT NULL
                AND over_odds IS NOT NULL
                AND under_odds IS NOT NULL
            """
            df = pd.read_sql(query, conn)

        if df.empty:
            return pd.DataFrame(columns=[
                "event_id", "book", "market", "player", "line", "over_odds",
                "under_odds", "season", "def_team", "team", "week", "pos"
            ])

        # Add fetched_at timestamp
        df["fetched_at"] = datetime.now(timezone.utc).isoformat()

        # Ensure required columns and data types
        df["line"] = pd.to_numeric(df["line"], errors="coerce")
        df["over_odds"] = pd.to_numeric(df["over_odds"], errors="coerce").astype("Int64")
        df["under_odds"] = pd.to_numeric(df["under_odds"], errors="coerce").astype("Int64")
        df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
        df["week"] = pd.to_numeric(df["week"], errors="coerce").astype("Int64")

        # Map database columns to expected adapter columns
        df["def_team"] = df["opponent_def_code"].apply(normalize_team_code)
        df["team"] = df["team_code"].apply(normalize_team_code)

        # Handle missing team inference
        for idx, row in df.iterrows():
            if pd.isna(row.get("team")) and not pd.isna(row.get("event_id")):
                inferred_team = normalize_team_code(
                    infer_offense_team(row.get("event_id"), row.get("def_team"))
                )
                df.at[idx, "team"] = inferred_team

        # Clean up column names to match expected interface
        expected_cols = [
            "event_id", "book", "market", "player", "line", "over_odds",
            "under_odds", "season", "def_team", "team", "week", "pos",
            "fetched_at", "is_stale"
        ]

        # Populate week using schedule data if available
        import os
        sched_csv = os.getenv("SCHEDULE_CSV", "tests/fixtures/schedule_2025_mini.csv")
        try:
            schedule_df = pd.read_csv(sched_csv)
            df = populate_week_from_schedule(df, schedule_df)

            # Extract detailed match statistics
            stats = getattr(df, '_week_population_stats', {
                'stage1_count': 0, 'stage2_count': 0, 'total_filled': 0, 'total_rows': len(df)
            })

            if stats['total_filled'] > 0:
                print(f"DbPropsAdapter: Populated week for {stats['total_filled']}/{stats['total_rows']} rows "
                      f"(stage1 {stats['stage1_count']}, stage2 {stats['stage2_count']})")
        except Exception as e:
            print(f"DbPropsAdapter: Week population skipped ({e})")

        # Ensure all expected columns exist
        for col in expected_cols:
            if col not in df.columns:
                df[col] = pd.NA

        return df[expected_cols].copy()

    def persist(self, df: pd.DataFrame, database_path: Path) -> None:
        """Persist is a no-op for database adapter since data is already in DB."""
        # Data is already in the database, so no need to persist
        print(f"DbPropsAdapter: Data already persisted in database at {database_path}")
        pass
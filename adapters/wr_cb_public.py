"""Load public WR/CB matchup notes from a local CSV."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from utils.teams import normalize_team_code

DEFAULT_CSV_PATH = Path("storage/imports/wr_cb_matchups.csv")


def load_wr_cb_context(csv_path: Path | None = None) -> pd.DataFrame:
    path = csv_path or DEFAULT_CSV_PATH
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "season",
                "week",
                "team",
                "player",
                "note",
                "source_url",
                "event_id",
                "updated_at",
            ]
        )
    df = pd.read_csv(path)
    expected = {"season", "week", "team", "player", "note", "source_url"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"WR/CB context CSV missing required columns: {sorted(missing)}")
    df["season"] = pd.to_numeric(df["season"], errors="coerce").astype("Int64")
    df["week"] = pd.to_numeric(df["week"], errors="coerce").astype("Int64")
    df["team"] = df["team"].apply(normalize_team_code)
    return df


def attach_event_ids(context_df: pd.DataFrame, schedule_df: pd.DataFrame) -> pd.DataFrame:
    if context_df.empty:
        return context_df.assign(event_id=None)
    schedule = schedule_df.copy()
    if schedule.empty:
        return context_df.assign(event_id=None)
    required = {"season", "week", "game_id", "home_team", "away_team"}
    missing = required.difference(schedule.columns)
    if missing:
        raise RuntimeError(f"Schedule data missing required columns: {sorted(missing)}")
    rows = []
    for _, row in schedule.iterrows():
        for team_type in ("home", "away"):
            team = normalize_team_code(row.get(f"{team_type}_team"))
            if team is None:
                continue
            rows.append(
                {
                    "season": int(row.get("season")) if pd.notna(row.get("season")) else None,
                    "week": int(row.get("week")) if pd.notna(row.get("week")) else None,
                    "team": team,
                    "event_id": row.get("game_id"),
                }
            )
    team_games = pd.DataFrame(rows)
    merged = context_df.merge(
        team_games,
        how="left",
        on=["season", "week", "team"],
    )
    return merged


def persist_wr_cb_context(df: pd.DataFrame, database_path: Path) -> None:
    if df.empty:
        return
    import sqlite3

    df = df.copy()
    df["updated_at"] = pd.Timestamp.utcnow().isoformat()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wr_cb_public (
                context_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                season INT,
                week INT,
                team TEXT,
                player TEXT,
                note TEXT,
                source_url TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute("DELETE FROM wr_cb_public")
        conn.executemany(
            """
            INSERT INTO wr_cb_public(event_id, season, week, team, player, note, source_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.get("event_id"),
                    int(row.get("season")) if pd.notna(row.get("season")) else None,
                    int(row.get("week")) if pd.notna(row.get("week")) else None,
                    row.get("team"),
                    row.get("player"),
                    row.get("note"),
                    row.get("source_url"),
                    row.get("updated_at"),
                )
                for _, row in df.iterrows()
            ],
        )
        conn.commit()

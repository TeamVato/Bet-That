"""Fetch and normalize NFL injury reports."""

from __future__ import annotations

import datetime
import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

try:
    import nfl_data_py as nfl
except ImportError:  # pragma: no cover - optional dependency
    nfl = None  # type: ignore

from utils.teams import normalize_team_code


def _load_injuries(seasons: Iterable[int]) -> pd.DataFrame:
    if not nfl:
        raise RuntimeError("nfl_data_py is required for injury ingestion")
    seasons = [int(s) for s in seasons]
    if not seasons:
        return pd.DataFrame()
    df = nfl.import_injuries(seasons)
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _schedule_team_map(schedule_df: pd.DataFrame) -> pd.DataFrame:
    if schedule_df.empty:
        return pd.DataFrame(columns=["season", "week", "team", "event_id", "game_id", "gameday"])
    required = {"season", "week", "game_id", "home_team", "away_team", "gameday"}
    missing = required.difference(schedule_df.columns)
    if missing:
        raise RuntimeError(f"Schedule data missing required columns: {sorted(missing)}")
    records = []
    for _, row in schedule_df.iterrows():
        for team_type in ("home", "away"):
            team = normalize_team_code(row.get(f"{team_type}_team"))
            if pd.isna(team):
                continue
            records.append(
                {
                    "season": int(row.get("season")) if pd.notna(row.get("season")) else None,
                    "week": int(row.get("week")) if pd.notna(row.get("week")) else None,
                    "team": str(team),
                    "event_id": row.get("game_id"),
                    "game_id": row.get("game_id"),
                    "gameday": row.get("gameday"),
                }
            )
    return pd.DataFrame(records)


def transform_injuries(raw: pd.DataFrame, schedule_df: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(
            columns=[
                "event_id",
                "season",
                "week",
                "team",
                "player",
                "position",
                "report_status",
                "report_primary_injury",
                "practice_status",
                "updated_at",
            ]
        )
    mapping = _schedule_team_map(schedule_df)
    merged = raw.copy()
    merged.rename(
        columns={
            "full_name": "player",
            "report_status": "status",
            "report_primary_injury": "primary_injury",
            "practice_status": "practice_status",
        },
        inplace=True,
    )
    merged["team"] = merged["team"].apply(normalize_team_code)
    merged["player"] = merged["player"].astype(str)
    merged["position"] = merged.get("position")
    merged["updated_at"] = merged.get("date_modified")
    merged = merged.merge(
        mapping,
        how="left",
        left_on=["season", "week", "team"],
        right_on=["season", "week", "team"],
    )
    merged["event_id"] = merged.get("event_id").fillna(merged.get("game_id"))
    columns = {
        "event_id": merged["event_id"],
        "season": merged.get("season"),
        "week": merged.get("week"),
        "team": merged.get("team"),
        "player": merged.get("player"),
        "position": merged.get("position"),
        "report_status": merged.get("status"),
        "report_primary_injury": merged.get("primary_injury"),
        "practice_status": merged.get("practice_status"),
        "updated_at": merged.get("updated_at"),
    }
    result = pd.DataFrame(columns)
    result = result.dropna(subset=["player"]).reset_index(drop=True)
    return result


def fetch_injuries(seasons: Iterable[int], schedule_df: pd.DataFrame) -> pd.DataFrame:
    raw = _load_injuries(seasons)
    if raw.empty:
        return raw
    return transform_injuries(raw, schedule_df)


def persist_injuries(df: pd.DataFrame, database_path: Path) -> None:
    if df.empty:
        return
    df = df.copy()
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce", utc=True)
    df["updated_at"] = df["updated_at"].dt.tz_convert(None)
    df["updated_at"] = df["updated_at"].fillna(pd.Timestamp.utcnow())
    df["updated_at"] = df["updated_at"].astype(str)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS injuries (
                injury_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                season INT,
                week INT,
                team TEXT,
                player TEXT,
                position TEXT,
                report_status TEXT,
                report_primary_injury TEXT,
                practice_status TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute("DELETE FROM injuries")
        conn.executemany(
            """
            INSERT INTO injuries (
                event_id, season, week, team, player, position,
                report_status, report_primary_injury, practice_status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.get("event_id"),
                    int(row.get("season")) if pd.notna(row.get("season")) else None,
                    int(row.get("week")) if pd.notna(row.get("week")) else None,
                    row.get("team"),
                    row.get("player"),
                    row.get("position"),
                    row.get("report_status"),
                    row.get("report_primary_injury"),
                    row.get("practice_status"),
                    row.get("updated_at"),
                )
                for _, row in df.iterrows()
            ],
        )
        conn.commit()

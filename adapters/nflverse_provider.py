"""Helpers for working with nflverse data via nfl_data_py."""
from __future__ import annotations

from typing import Dict, Iterable, Optional

import pandas as pd

try:
    import nfl_data_py as nfl
except ImportError:  # pragma: no cover - handled gracefully
    nfl = None  # type: ignore


SCHEDULE_COLUMNS = [
    "game_id",
    "season",
    "week",
    "game_type",
    "away_team",
    "home_team",
    "game_date",
    "venue",
]

PLAYER_LOG_COLUMNS = [
    "player_id",
    "player_name",
    "recent_team",
    "week",
    "season",
    "opponent_team",
    "passing_yards",
    "attempts",
    "completions",
    "game_id",
]


def _empty_schedule() -> pd.DataFrame:
    return pd.DataFrame(columns=SCHEDULE_COLUMNS)


def _empty_logs() -> pd.DataFrame:
    return pd.DataFrame(columns=PLAYER_LOG_COLUMNS)


def get_schedules(seasons: Iterable[int]) -> pd.DataFrame:
    """Download schedules for the requested seasons."""
    if not nfl:
        print("nfl_data_py is not installed; returning empty schedule DataFrame")
        return _empty_schedule()
    try:
        df = nfl.import_schedules(seasons)
        cols = [c for c in SCHEDULE_COLUMNS if c in df.columns]
        return df[cols].copy()
    except Exception as exc:  # pragma: no cover - network failure
        print(f"Failed to download schedules: {exc}")
        return _empty_schedule()


def get_player_game_logs(seasons: Iterable[int]) -> pd.DataFrame:
    """Download player game logs for the requested seasons."""
    if not nfl:
        print("nfl_data_py is not installed; returning empty logs DataFrame")
        return _empty_logs()
    try:
        df = nfl.import_player_stats(seasons, ['passing_yards'])
    except TypeError:
        # Some versions use positional args only
        df = nfl.import_player_stats(seasons)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to download player stats: {exc}")
        return _empty_logs()
    rename_map = {
        "player_display_name": "player_name",
        "recent_team": "recent_team",
        "opponent_team": "opponent_team",
        "pass_yds": "passing_yards",
        "attempts": "attempts",
        "cmp": "completions",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df[new] = df[old]
    cols = [c for c in PLAYER_LOG_COLUMNS if c in df.columns]
    missing = set(PLAYER_LOG_COLUMNS) - set(cols)
    for col in missing:
        df[col] = pd.NA
    return df[PLAYER_LOG_COLUMNS].copy()


def build_event_lookup(schedule_df: pd.DataFrame) -> Dict[str, Dict[str, Optional[str]]]:
    """Create a mapping from game_id to useful metadata fields."""
    lookup: Dict[str, Dict[str, Optional[str]]] = {}
    for _, row in schedule_df.iterrows():
        lookup[str(row.get("game_id"))] = {
            "season": row.get("season"),
            "week": row.get("week"),
            "venue": row.get("venue"),
            "game_date": row.get("game_date"),
        }
    return lookup

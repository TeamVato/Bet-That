"""Helpers for working with nflverse data via nfl_data_py."""
from __future__ import annotations

from typing import Dict, Iterable, Optional, List
from pathlib import Path

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
    "gameday",
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
    """Download player game logs for the requested seasons.

    Order of preference:
    1) Local 2025 (or other configured) CSVs if present
    2) nfl_data_py.import_weekly_data
    3) nfl_data_py.import_player_stats (legacy)
    """
    if not nfl:
        print("nfl_data_py is not installed; returning empty logs DataFrame")
        return _empty_logs()

    DATA_DIR = Path("storage/imports/PlayerProfiler/Game Log")
    LOCAL_LOGS = {
        2025: DATA_DIR / "2025-Advanced-Gamelog.csv",
    }

    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {
            "player_display_name": "player_name",
            "name": "player_name",
            "player": "player_id",
            "team": "recent_team",
            "opponent": "opponent_team",
            "opponent_team": "opponent_team",
            "recent_team": "recent_team",
            "pass_attempts": "attempts",
            "attempts": "attempts",
            "completions": "completions",
            "cmp": "completions",
            "passing_yards": "passing_yards",
            "pass_yds": "passing_yards",
        }
        for old, new in rename_map.items():
            if old in df.columns:
                df[new] = df[old]
        # Ensure all required columns exist
        out = df.copy()
        for col in PLAYER_LOG_COLUMNS:
            if col not in out.columns:
                out[col] = pd.NA
        # Coerce numerics
        for col in ("week", "season", "passing_yards", "attempts", "completions"):
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")
        return out[PLAYER_LOG_COLUMNS].copy()

    frames: List[pd.DataFrame] = []
    seasons = [int(s) for s in seasons]

    # Remote first: attempt to load all requested seasons from nflverse
    df_remote = pd.DataFrame()
    try:
        weekly = nfl.import_weekly_data(seasons)
        df_remote = weekly.copy()
    except Exception:
        try:
            df_remote = nfl.import_player_stats(seasons)
        except Exception as exc:
            print(f"Failed to download player logs: {exc}")
            df_remote = pd.DataFrame()
    if not df_remote.empty:
        frames.append(_normalize(df_remote))

    # Local fallback: only fill gaps or seasons missing from remote
    for season in seasons:
        local_path = LOCAL_LOGS.get(season)
        if not local_path or not local_path.exists():
            continue
        try:
            df_local = pd.read_csv(local_path, low_memory=False)
            df_local["season"] = season
            frames.append(_normalize(df_local))
        except Exception as exc:
            print(f"Warning: failed to load local weekly logs for {season} ({exc})")

    if not frames:
        return _empty_logs()

    combined = pd.concat(frames, ignore_index=True, sort=False)
    # Remote data should win; keep first occurrence (remote appended first)
    combined = combined.drop_duplicates(subset=["player_id", "season", "week"], keep="first")
    return combined.reset_index(drop=True)


def build_event_lookup(schedule_df: pd.DataFrame) -> Dict[str, Dict[str, Optional[str]]]:
    """Create a mapping from game_id to useful metadata fields."""
    lookup: Dict[str, Dict[str, Optional[str]]] = {}
    for _, row in schedule_df.iterrows():
        info = {
            "season": row.get("season"),
            "week": row.get("week"),
            "venue": row.get("venue"),
            "game_date": row.get("gameday"),
        }
        game_id = row.get("game_id")
        if pd.notna(game_id):
            lookup[str(game_id)] = info
        gameday = row.get("gameday")
        away = row.get("away_team")
        home = row.get("home_team")
        if pd.notna(gameday) and pd.notna(away) and pd.notna(home):
            date_str = pd.to_datetime(gameday).strftime("%Y-%m-%d")
            alt_key_away_home = f"{date_str}-{away}-{home}"
            alt_key_home_away = f"{date_str}-{home}-{away}"
            lookup[alt_key_away_home] = info
            lookup[alt_key_home_away] = info
    return lookup

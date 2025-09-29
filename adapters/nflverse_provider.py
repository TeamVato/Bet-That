"""Helpers for working with nflverse data via nfl_data_py."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

try:
    import nfl_data_py as nfl
except ImportError:  # pragma: no cover - handled gracefully
    nfl = None  # type: ignore

from adapters.stats_provider import import_weekly_stats

SCHEDULE_COLUMNS = [
    "game_id",
    "season",
    "week",
    "game_type",
    "away_team",
    "home_team",
    "gameday",
    "venue",
    "roof",
    "surface",
    "temp",
    "wind",
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


SCHEDULE_CACHE_PATH = Path("storage/imports/nflverse_schedules_cache.csv")


def _load_cached_schedule(seasons: Iterable[int]) -> pd.DataFrame:
    """Load cached schedules filtered to the requested seasons."""

    if not SCHEDULE_CACHE_PATH.exists():
        return _empty_schedule()
    try:
        cached = pd.read_csv(SCHEDULE_CACHE_PATH, low_memory=False)
    except Exception as exc:
        print(f"Warning: failed to load cached schedules ({exc})")
        return _empty_schedule()
    if cached.empty:
        return _empty_schedule()
    for col in SCHEDULE_COLUMNS:
        if col not in cached.columns:
            cached[col] = pd.NA
    if "season" in cached.columns:
        filtered = cached[cached["season"].isin(seasons)]
        if not filtered.empty:
            cached = filtered
    cols = [c for c in SCHEDULE_COLUMNS if c in cached.columns]
    if not cols:
        return _empty_schedule()
    return cached[cols].copy()


def _update_schedule_cache(df: pd.DataFrame) -> None:
    """Persist the provided schedule frame into the local cache."""

    if df.empty:
        return
    cols = [c for c in SCHEDULE_COLUMNS if c in df.columns]
    if not cols:
        return
    SCHEDULE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    to_store = df[cols].copy()
    if SCHEDULE_CACHE_PATH.exists():
        try:
            existing = pd.read_csv(SCHEDULE_CACHE_PATH, low_memory=False)
        except Exception:
            existing = pd.DataFrame(columns=SCHEDULE_COLUMNS)
        if not existing.empty:
            for col in cols:
                if col not in existing.columns:
                    existing[col] = pd.NA
            to_store = pd.concat([existing[cols], to_store], ignore_index=True, sort=False)
    subset = [c for c in ("game_id", "gameday", "home_team", "away_team") if c in to_store.columns]
    if subset:
        to_store = to_store.drop_duplicates(subset=subset, keep="last")
    to_store = to_store.sort_values(by=[c for c in ("season", "week") if c in to_store.columns])
    to_store.to_csv(SCHEDULE_CACHE_PATH, index=False)


def get_schedules(seasons: Iterable[int]) -> pd.DataFrame:
    """Download schedules for the requested seasons."""
    seasons = sorted({int(s) for s in seasons})
    if not seasons:
        return _empty_schedule()

    cached = _load_cached_schedule(seasons)

    if not nfl:
        if cached.empty:
            print("nfl_data_py is not installed; returning empty schedule DataFrame")
        return cached

    attempts = 3
    wait_seconds = 1.0
    last_exc: Exception | None = None
    df_remote = pd.DataFrame()
    for attempt in range(1, attempts + 1):
        try:
            df_remote = nfl.import_schedules(seasons)
            break
        except Exception as exc:  # pragma: no cover - network failure
            last_exc = exc
            print(f"Failed to download schedules (attempt {attempt}/{attempts}): {exc}")
            if attempt < attempts:
                time.sleep(wait_seconds)
                wait_seconds *= 2
    else:
        df_remote = pd.DataFrame()

    if df_remote.empty:
        if last_exc:
            print("Falling back to cached schedules snapshot.")
        return cached

    cols = [c for c in SCHEDULE_COLUMNS if c in df_remote.columns]
    df_remote = df_remote[cols].copy()

    if cached.empty:
        combined = df_remote
    else:
        remote_seasons = set(df_remote.get("season", pd.Series(dtype=int)).dropna().astype(int))
        missing = set(seasons) - remote_seasons
        if missing:
            cached_missing = (
                cached[cached["season"].isin(missing)] if "season" in cached.columns else cached
            )
            if not cached_missing.empty:
                combined = pd.concat([df_remote, cached_missing], ignore_index=True, sort=False)
            else:
                combined = df_remote
        else:
            combined = df_remote

    subset = [c for c in ("game_id", "gameday", "home_team", "away_team") if c in combined.columns]
    if subset:
        combined = combined.drop_duplicates(subset=subset, keep="last")
    combined = combined.reset_index(drop=True)
    _update_schedule_cache(combined)
    return combined


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
    if nfl:
        try:
            weekly = nfl.import_weekly_data(seasons)
            df_remote = weekly.copy()
        except Exception:
            try:
                df_remote = import_weekly_stats(seasons)
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

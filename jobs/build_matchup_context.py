"""Build matchup context artifacts: scheme metrics, injuries, weather, WR/CB notes."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))

from adapters.injuries import fetch_injuries, persist_injuries
from adapters.weather import build_weather, persist_weather
from adapters.wr_cb_public import attach_event_ids, load_wr_cb_context, persist_wr_cb_context
from adapters.nflverse_provider import get_schedules
from db.migrate import migrate, parse_database_url
from engine.scheme import build_team_week_scheme, persist_team_week_scheme


def _load_seasons() -> list[int]:
    seasons_env = os.getenv("DEFAULT_SEASONS", "2023")
    seasons = [int(s.strip()) for s in seasons_env.split(",") if s.strip()]
    return seasons or [2023]


def _database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    db_path = parse_database_url(url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        migrate()
    return db_path


def _ensure_dataframe(obj) -> pd.DataFrame:
    if isinstance(obj, pd.DataFrame):
        return obj
    if obj is None:
        return pd.DataFrame()
    return pd.DataFrame(obj)


def main() -> None:
    seasons = _load_seasons()
    db_path = _database_path()

    print(f"Building matchup context for seasons: {seasons}")
    schedule = _ensure_dataframe(get_schedules(seasons))
    print(f"Loaded schedule rows: {len(schedule)}")

    # Scheme metrics (team-week PROE, etc.)
    try:
        scheme_df = build_team_week_scheme(seasons)
        print(f"Computed team_week_scheme rows: {len(scheme_df)}")
        persist_team_week_scheme(scheme_df, db_path)
    except Exception as exc:
        print(f"Warning: failed to compute scheme metrics ({exc})")

    # Injuries
    try:
        injuries_df = fetch_injuries(seasons, schedule)
        injuries_df = _ensure_dataframe(injuries_df)
        print(f"Fetched injuries rows: {len(injuries_df)}")
        persist_injuries(injuries_df, db_path)
    except Exception as exc:
        print(f"Warning: failed to ingest injuries ({exc})")

    # Weather
    try:
        weather_df = build_weather(schedule)
        weather_df = _ensure_dataframe(weather_df)
        for col in ("event_id", "game_id", "temp_f", "wind_mph", "precip", "updated_at"):
            if col not in weather_df.columns:
                weather_df[col] = None
        print(f"Derived weather rows: {len(weather_df)}")
        persist_weather(weather_df, db_path)
    except Exception as exc:
        print(f"Warning: failed to derive weather context ({exc})")

    # WR/CB notes (optional CSV)
    try:
        raw_wr_cb = load_wr_cb_context()
        raw_wr_cb = _ensure_dataframe(raw_wr_cb)
        if raw_wr_cb.empty:
            print("WR/CB matchup CSV not found; skipping.")
        else:
            wr_cb = attach_event_ids(raw_wr_cb, schedule)
            print(f"Loaded WR/CB context rows: {len(wr_cb)}")
            persist_wr_cb_context(wr_cb, db_path)
    except Exception as exc:
        print(f"Warning: failed to ingest WR/CB context ({exc})")

    print("Matchup context build complete.")


if __name__ == "__main__":
    main()

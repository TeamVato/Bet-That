"""Build simple weather context from schedule metadata."""
from __future__ import annotations

from datetime import UTC, datetime
import sqlite3
from pathlib import Path

import pandas as pd

INDOOR_KEYWORDS = {"dome", "domed", "indoor", "closed", "retractable"}


def build_weather(schedule_df: pd.DataFrame) -> pd.DataFrame:
    if schedule_df.empty:
        return pd.DataFrame(columns=["event_id", "temp_f", "wind_mph", "roof", "surface", "precip", "indoor", "updated_at"])
    required = {"game_id", "temp", "wind", "roof", "surface"}
    missing = required.difference(schedule_df.columns)
    if missing:
        raise RuntimeError(f"Schedule data missing required columns: {sorted(missing)}")
    df = schedule_df.copy()
    df["event_id"] = df["game_id"].astype(str)
    df["temp_f"] = pd.to_numeric(df.get("temp"), errors="coerce")
    df["wind_mph"] = pd.to_numeric(df.get("wind"), errors="coerce")
    df["roof"] = df.get("roof").astype(str).str.lower()
    df["surface"] = df.get("surface")
    weather_detail = df.get("weather")
    if weather_detail is None:
        weather_detail = df.get("weather_detail")
    df["precip"] = weather_detail
    df["indoor"] = df["roof"].apply(lambda val: int(val in INDOOR_KEYWORDS) if isinstance(val, str) else None)
    df["updated_at"] = datetime.now(UTC).isoformat()
    result = df[["event_id", "temp_f", "wind_mph", "roof", "surface", "precip", "indoor", "updated_at"]]
    result = result.drop_duplicates(subset=["event_id"], keep="last").reset_index(drop=True)
    return result


def persist_weather(df: pd.DataFrame, database_path: Path) -> None:
    if df.empty:
        return
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                event_id TEXT PRIMARY KEY,
                temp_f FLOAT,
                wind_mph FLOAT,
                roof TEXT,
                surface TEXT,
                precip TEXT,
                indoor INT,
                updated_at TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO weather(event_id, temp_f, wind_mph, roof, surface, precip, indoor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                temp_f=excluded.temp_f,
                wind_mph=excluded.wind_mph,
                roof=excluded.roof,
                surface=excluded.surface,
                precip=excluded.precip,
                indoor=excluded.indoor,
                updated_at=excluded.updated_at
            """,
            [tuple(row) for row in df.to_numpy()],
        )
        conn.commit()

"""Build simple weather context from schedule metadata."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

INDOOR_KEYWORDS = {"dome", "domed", "indoor", "closed", "retractable"}


def build_weather(schedule_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "event_id",
        "game_id",
        "temp_f",
        "wind_mph",
        "roof",
        "surface",
        "precip",
        "indoor",
        "updated_at",
    ]
    if schedule_df.empty:
        return pd.DataFrame(columns=columns)

    df = schedule_df.copy()
    if "game_id" not in df.columns:
        df["game_id"] = None

    df["event_id"] = df["game_id"].apply(lambda val: str(val) if pd.notna(val) else None)
    df["temp_f"] = pd.to_numeric(df.get("temp"), errors="coerce") if "temp" in df.columns else None
    df["wind_mph"] = (
        pd.to_numeric(df.get("wind"), errors="coerce") if "wind" in df.columns else None
    )
    df["roof"] = df.get("roof") if "roof" in df.columns else None
    if "roof" in df.columns:
        df["roof"] = df["roof"].astype(str).str.lower()
    df["surface"] = df.get("surface") if "surface" in df.columns else None

    precip_source = None
    for candidate in ("precip", "weather", "weather_detail"):
        if candidate in df.columns:
            precip_source = candidate
            break
    if precip_source is None:
        df["precip"] = None
    else:
        df["precip"] = pd.to_numeric(df.get(precip_source), errors="coerce")

    if "indoor" in df.columns:
        df["indoor"] = pd.to_numeric(df["indoor"], errors="coerce")
    else:
        df["indoor"] = df.get("roof").apply(
            lambda val: int(val in INDOOR_KEYWORDS) if isinstance(val, str) else None
        )

    df["updated_at"] = datetime.now(UTC).isoformat()
    result = df[[col for col in columns if col in df.columns]].copy()
    for col in columns:
        if col not in result.columns:
            result[col] = None
    result = result[columns]
    result = result.drop_duplicates(subset=["event_id"], keep="last").reset_index(drop=True)
    return result


def persist_weather(df: pd.DataFrame, database_path: Path) -> None:
    if df.empty:
        return
    database_path.parent.mkdir(parents=True, exist_ok=True)
    required_cols = [
        "event_id",
        "game_id",
        "temp_f",
        "wind_mph",
        "roof",
        "surface",
        "precip",
        "indoor",
        "updated_at",
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                event_id TEXT PRIMARY KEY,
                game_id TEXT,
                temp_f FLOAT,
                wind_mph FLOAT,
                roof TEXT,
                surface TEXT,
                precip REAL,
                indoor INT,
                updated_at TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO weather(event_id, game_id, temp_f, wind_mph, roof, surface, precip, indoor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                game_id=excluded.game_id,
                temp_f=excluded.temp_f,
                wind_mph=excluded.wind_mph,
                roof=excluded.roof,
                surface=excluded.surface,
                precip=excluded.precip,
                indoor=excluded.indoor,
                updated_at=excluded.updated_at
            """,
            [tuple(row) for row in df[required_cols].to_numpy()],
        )
        conn.commit()

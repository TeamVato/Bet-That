from __future__ import annotations

import sqlite3
from pathlib import Path

from jobs.migrate_weather_schema import migrate_weather_schema


def _weather_columns(database_path: Path) -> set[str]:
    with sqlite3.connect(database_path) as conn:
        return {row[1] for row in conn.execute("PRAGMA table_info(weather)")}


def test_weather_schema_columns(tmp_path) -> None:
    db_path = tmp_path / "weather.sqlite"
    migrate_weather_schema(db_path)

    columns = _weather_columns(db_path)
    expected = {"event_id", "game_id", "temp_f", "wind_mph", "precip", "updated_at"}
    assert expected.issubset(columns)


def test_weather_schema_idempotent(tmp_path) -> None:
    db_path = tmp_path / "weather_twice.sqlite"
    migrate_weather_schema(db_path)
    migrate_weather_schema(db_path)

    columns = _weather_columns(db_path)
    expected = {"event_id", "game_id", "temp_f", "wind_mph", "precip", "updated_at"}
    assert expected.issubset(columns)
    assert len(columns) >= len(expected)

from __future__ import annotations

import sqlite3

from jobs.migrate_weather_schema import ensure_weather_schema, main as run_migration

REQUIRED_COLUMNS = {
    "event_id",
    "game_id",
    "temp_f",
    "wind_mph",
    "precip",
    "roof",
    "surface",
    "indoor",
    "updated_at",
}


def _weather_columns(db_path: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        return {row[1] for row in conn.execute("PRAGMA table_info(weather)")}


def test_ensure_weather_schema_adds_columns(tmp_path) -> None:
    db_path = tmp_path / "weather.sqlite"
    ensure_weather_schema(str(db_path))
    ensure_weather_schema(str(db_path))  # idempotent safety

    assert REQUIRED_COLUMNS <= _weather_columns(str(db_path))


def test_main_uses_database_url(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "from_env.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    run_migration()

    assert REQUIRED_COLUMNS <= _weather_columns(str(db_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)

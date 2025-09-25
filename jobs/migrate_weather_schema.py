"""Ensure the weather table exists with the expected columns."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from db.migrate import parse_database_url


REQUIRED_COLUMNS: dict[str, str] = {
    "game_id": "TEXT",
    "temp_f": "REAL",
    "wind_mph": "REAL",
    "precip": "REAL",
    "updated_at": "TEXT",
}


def _database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    return parse_database_url(url)


def migrate_weather_schema(database_path: Path | None = None) -> None:
    db_path = database_path or _database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                event_id TEXT PRIMARY KEY,
                game_id TEXT,
                temp_f REAL,
                wind_mph REAL,
                roof TEXT,
                surface TEXT,
                precip REAL,
                indoor INT,
                updated_at TEXT
            )
            """
        )

        existing_columns = {
            row[1]: row[2]
            for row in conn.execute("PRAGMA table_info(weather)")
        }
        for column, column_type in REQUIRED_COLUMNS.items():
            if column not in existing_columns:
                conn.execute(
                    f"ALTER TABLE weather ADD COLUMN {column} {column_type}"
                )
        conn.commit()


def main() -> None:
    migrate_weather_schema()


if __name__ == "__main__":
    main()

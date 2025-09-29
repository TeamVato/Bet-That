"""Ensure the weather table exists with required columns without repo imports."""

import os
import sqlite3
from typing import Iterable

REQ_COLS: Iterable[tuple[str, str]] = (
    ("event_id", "TEXT"),
    ("game_id", "TEXT"),
    ("temp_f", "REAL"),
    ("wind_mph", "REAL"),
    ("precip", "REAL"),
    ("roof", "TEXT"),
    ("surface", "TEXT"),
    ("indoor", "INTEGER"),
    ("updated_at", "TEXT"),
)


def _sqlite_path() -> str:
    """Resolve the SQLite file path from DATABASE_URL with sensible defaults."""
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")

    if url.startswith("sqlite:////"):
        return "/" + url[len("sqlite:////") :]

    if url.startswith("sqlite:///"):
        return url[len("sqlite:///") :]

    if url.startswith("sqlite://"):
        # Handles forms like sqlite://relative/path.db
        return url[len("sqlite://") :]

    return "storage/odds.db"


def ensure_weather_schema(db_path: str) -> None:
    """Create the weather table and add missing columns for the given db path."""
    directory = os.path.dirname(db_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS weather (
                event_id   TEXT,
                game_id    TEXT,
                temp_f     REAL,
                wind_mph   REAL,
                precip     REAL,
                roof       TEXT,
                surface    TEXT,
                indoor     INTEGER,
                updated_at TEXT
            );
            """
        )

        existing = {row[1] for row in con.execute("PRAGMA table_info(weather)")}
        for column, column_type in REQ_COLS:
            if column not in existing:
                con.execute(f"ALTER TABLE weather ADD COLUMN {column} {column_type};")

        con.commit()


def main() -> None:
    db_path = _sqlite_path()
    ensure_weather_schema(db_path)

    print("weather schema OK")


if __name__ == "__main__":
    main()

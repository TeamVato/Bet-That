"""Utility script to create the SQLite schema defined in db/schema.sql."""

from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def parse_database_url(database_url: str) -> Path:
    """Parse a SQLAlchemy-style SQLite URL into a filesystem path."""
    if database_url.startswith("sqlite:///"):
        path_str = database_url.replace("sqlite:///", "", 1)
        return Path(path_str)
    raise ValueError("Only sqlite:/// URLs are supported for this starter project.")


def migrate(database_url: str | None = None) -> Path:
    """Create the SQLite database and run the schema script."""
    load_dotenv()
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    db_path = parse_database_url(url)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    print(f"Database migrated at {db_path}")
    return db_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--database-url",
        dest="database_url",
        help="Override the DATABASE_URL environment variable",
    )
    args = parser.parse_args()
    migrate(args.database_url)


if __name__ == "__main__":
    main()

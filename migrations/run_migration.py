#!/usr/bin/env python3
"""Simple migration runner for Bet-That database."""

import sqlite3
import sys
from pathlib import Path

def run_migration(db_path: Path, migration_file: Path) -> None:
    """Run a single migration file against the database."""
    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    print(f"Running migration: {migration_file.name}")

    with sqlite3.connect(db_path) as conn:
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")

        # Read and execute migration
        migration_sql = migration_file.read_text()

        # Execute each statement separately (SQLite doesn't handle multi-statement well)
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]

        for stmt in statements:
            if stmt.startswith('--') or not stmt:
                continue
            print(f"  Executing: {stmt[:50]}...")
            conn.execute(stmt)

        conn.commit()

    print(f"Migration completed: {migration_file.name}")

def main():
    """Run migration specified in command line args."""
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file> [database_path]")
        print("Example: python run_migration.py 001_season_backfill_and_indexes.sql")
        sys.exit(1)

    migration_file = Path(__file__).parent / sys.argv[1]
    db_path = Path(sys.argv[2] if len(sys.argv) > 2 else "storage/odds.db")

    try:
        run_migration(db_path, migration_file)
        print("✅ Migration successful!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
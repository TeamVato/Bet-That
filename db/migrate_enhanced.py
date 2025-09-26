"""Enhanced migration system with schema versioning and validation."""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

try:
    from schemas.odds_schemas import (
        validate_odds_snapshots,
        validate_current_best_lines,
        validate_edges,
        validate_defense_ratings,
    )
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    print("Warning: Validation schemas not available - continuing without validation")

from db.migrate import parse_database_url


class DatabaseMigrator:
    """Enhanced database migrator with versioning and validation."""

    CURRENT_SCHEMA_VERSION = 2
    MIGRATION_SCRIPTS = {
        1: "schema.sql",
        2: "schema_enhanced.sql",
    }

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.logger = logging.getLogger(f"{__name__}.DatabaseMigrator")

    def get_current_version(self) -> int:
        """Get current schema version from database."""
        if not self.database_path.exists():
            return 0

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Check if version table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='schema_version'
                """)

                if not cursor.fetchone():
                    # No version table - check if any tables exist
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    return 1 if tables else 0

                # Get current version
                cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
                result = cursor.fetchone()
                return result[0] if result else 0

        except sqlite3.Error as e:
            self.logger.warning(f"Could not determine schema version: {e}")
            return 0

    def create_version_table(self, conn: sqlite3.Connection) -> None:
        """Create schema version tracking table."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL,
                applied_at TEXT NOT NULL,
                script_name TEXT,
                checksum TEXT
            )
        """)
        conn.commit()

    def record_migration(self, conn: sqlite3.Connection, version: int, script_name: str) -> None:
        """Record successful migration in version table."""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schema_version (version, applied_at, script_name, checksum)
            VALUES (?, ?, ?, ?)
        """, (version, time.strftime("%Y-%m-%d %H:%M:%S UTC"), script_name, ""))
        conn.commit()

    def apply_migration(self, version: int) -> bool:
        """Apply a specific migration version."""
        if version not in self.MIGRATION_SCRIPTS:
            self.logger.error(f"Migration script for version {version} not found")
            return False

        script_name = self.MIGRATION_SCRIPTS[version]
        script_path = Path(__file__).parent / script_name

        if not script_path.exists():
            self.logger.error(f"Migration script {script_path} not found")
            return False

        self.logger.info(f"Applying migration {version}: {script_name}")

        try:
            # Create database directory if needed
            self.database_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(self.database_path, timeout=30) as conn:
                # Enable WAL mode for better performance
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")

                # Create version table if needed
                self.create_version_table(conn)

                # Read and execute migration script
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()

                # Execute script in transaction
                conn.executescript(script_content)

                # Record successful migration
                self.record_migration(conn, version, script_name)

                self.logger.info(f"Migration {version} applied successfully")
                return True

        except Exception as e:
            self.logger.error(f"Migration {version} failed: {e}")
            return False

    def migrate_to_latest(self) -> bool:
        """Migrate database to latest schema version."""
        current_version = self.get_current_version()
        target_version = self.CURRENT_SCHEMA_VERSION

        self.logger.info(f"Current schema version: {current_version}, target: {target_version}")

        if current_version >= target_version:
            self.logger.info("Database is already at latest version")
            return True

        # Apply migrations in sequence
        for version in range(current_version + 1, target_version + 1):
            if not self.apply_migration(version):
                return False

        self.logger.info(f"Successfully migrated to version {target_version}")
        return True

    def validate_schema(self) -> bool:
        """Validate database schema and data integrity."""
        if not self.database_path.exists():
            self.logger.error("Database does not exist")
            return False

        self.logger.info("Validating database schema and data integrity")
        issues_found = 0

        try:
            with sqlite3.connect(self.database_path, timeout=30) as conn:
                # Check foreign key constraints
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_key_check")
                fk_violations = cursor.fetchall()

                if fk_violations:
                    issues_found += len(fk_violations)
                    self.logger.error(f"Foreign key violations found: {len(fk_violations)}")
                    for violation in fk_violations[:5]:  # Show first 5
                        self.logger.error(f"  {violation}")

                # Check table integrity
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()
                if integrity_result[0] != "ok":
                    issues_found += 1
                    self.logger.error(f"Database integrity check failed: {integrity_result[0]}")

                # Validate data using pandera schemas if available
                if VALIDATION_AVAILABLE:
                    issues_found += self._validate_table_data(conn)

                if issues_found == 0:
                    self.logger.info("✅ Schema validation passed")
                    return True
                else:
                    self.logger.error(f"❌ Schema validation failed with {issues_found} issues")
                    return False

        except Exception as e:
            self.logger.error(f"Schema validation error: {e}")
            return False

    def _validate_table_data(self, conn: sqlite3.Connection) -> int:
        """Validate table data using pandera schemas."""
        issues_found = 0

        # Define table validations
        table_validators = {
            "odds_snapshots": validate_odds_snapshots,
            "current_best_lines": validate_current_best_lines,
            "edges": validate_edges,
            "defense_ratings": validate_defense_ratings,
        }

        for table_name, validator in table_validators.items():
            try:
                # Check if table exists and has data
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                if row_count == 0:
                    self.logger.info(f"Table {table_name} is empty - skipping validation")
                    continue

                # Load sample data for validation (limit to 1000 rows for performance)
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 1000", conn)

                if not df.empty:
                    validator(df)
                    self.logger.info(f"✅ Table {table_name} validation passed ({len(df)} rows checked)")

            except Exception as e:
                issues_found += 1
                self.logger.error(f"❌ Table {table_name} validation failed: {e}")

        return issues_found

    def optimize_database(self) -> bool:
        """Optimize database performance with VACUUM and ANALYZE."""
        self.logger.info("Optimizing database performance")

        try:
            with sqlite3.connect(self.database_path, timeout=60) as conn:
                # Update table statistics
                conn.execute("ANALYZE")

                # Optimize database (this can take time for large databases)
                conn.execute("PRAGMA optimize")

                self.logger.info("Database optimization completed")
                return True

        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            return False

    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics for monitoring."""
        if not self.database_path.exists():
            return {}

        stats = {}
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Get table row counts
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)

                for (table_name,) in cursor.fetchall():
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        stats[f"{table_name}_rows"] = count
                    except sqlite3.Error:
                        stats[f"{table_name}_rows"] = -1

                # Get database file size
                stats["database_size_bytes"] = self.database_path.stat().st_size

        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")

        return stats

    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """Create a backup of the database."""
        if not self.database_path.exists():
            self.logger.error("Source database does not exist")
            return False

        if backup_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.database_path.parent / f"{self.database_path.stem}_backup_{timestamp}.db"

        try:
            import shutil
            shutil.copy2(self.database_path, backup_path)

            self.logger.info(f"Database backed up to {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Enhanced database migration and management")

    parser.add_argument(
        "--database-url",
        help="Override DATABASE_URL environment variable"
    )

    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Migrate to latest schema version"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate schema and data integrity"
    )

    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Optimize database performance"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics"
    )

    parser.add_argument(
        "--backup",
        metavar="PATH",
        help="Create database backup at specified path"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Get database path
    load_dotenv()
    import os
    url = args.database_url or os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    database_path = parse_database_url(url)

    # Initialize migrator
    migrator = DatabaseMigrator(database_path)

    # Execute requested operations
    success = True

    if args.backup:
        backup_path = Path(args.backup)
        success &= migrator.backup_database(backup_path)

    if args.migrate:
        success &= migrator.migrate_to_latest()

    if args.validate:
        success &= migrator.validate_schema()

    if args.optimize:
        success &= migrator.optimize_database()

    if args.stats:
        stats = migrator.get_database_stats()
        print("\n📊 Database Statistics:")
        for key, value in stats.items():
            if key.endswith("_rows"):
                table_name = key.replace("_rows", "")
                print(f"  {table_name:<25} {value:>10,} rows")

        if "database_size_bytes" in stats:
            size_mb = stats["database_size_bytes"] / (1024 * 1024)
            print(f"  {'Database size':<25} {size_mb:>10.2f} MB")

    if not any([args.migrate, args.validate, args.optimize, args.stats, args.backup]):
        # Default: migrate to latest
        success = migrator.migrate_to_latest()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
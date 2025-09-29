#!/usr/bin/env python3
"""Enhanced database initialization script"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from api.database import create_tables, get_db_session, init_database
from api.fixtures.sample_data import load_sample_data

logger = logging.getLogger(__name__)


def run_migration(migration_file: Path) -> None:
    """Run a migration SQL file"""
    import sqlite3

    from api.settings import get_database_url
    from db.migrate import parse_database_url

    db_path = parse_database_url(get_database_url())

    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    logger.info(f"Running migration: {migration_file.name}")

    with sqlite3.connect(db_path) as conn:
        # Enable foreign keys and WAL mode
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")

        # Read and execute migration
        migration_sql = migration_file.read_text()

        # Execute script
        conn.executescript(migration_sql)
        conn.commit()

    logger.info(f"Migration completed: {migration_file.name}")


def initialize_enhanced_database(
    run_migrations: bool = True, create_sample: bool = False, force_recreate: bool = False
):
    """Initialize the enhanced database with all models"""

    try:
        # Initialize database connection
        init_database()
        logger.info("Database connection initialized")

        # Run migrations if requested
        if run_migrations:
            migrations_dir = Path(__file__).parent.parent / "migrations"

            # Run our enhanced user models migration
            enhanced_migration = migrations_dir / "002_create_enhanced_user_models.sql"
            if enhanced_migration.exists():
                run_migration(enhanced_migration)
            else:
                logger.warning(f"Enhanced migration file not found: {enhanced_migration}")

        # Create tables using SQLAlchemy (this will create any missing tables)
        if force_recreate:
            from api.database import drop_tables

            logger.warning("Dropping all tables (force recreate)")
            drop_tables()

        create_tables()
        logger.info("SQLAlchemy tables created/updated")

        # Create sample data if requested
        if create_sample:
            with get_db_session() as db:
                try:
                    sample_data = load_sample_data(db)
                    logger.info("Sample data created successfully")
                except Exception as e:
                    logger.error(f"Failed to create sample data: {e}")

        logger.info("Enhanced database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Initialize enhanced Bet-That database")

    parser.add_argument(
        "--skip-migrations", action="store_true", help="Skip running SQL migrations"
    )

    parser.add_argument("--sample-data", action="store_true", help="Create sample data for testing")

    parser.add_argument(
        "--force-recreate",
        action="store_true",
        help="Drop and recreate all tables (WARNING: destroys data)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if args.force_recreate:
        confirmation = input("This will DELETE ALL DATA. Are you sure? (type 'yes' to confirm): ")
        if confirmation.lower() != "yes":
            print("Operation cancelled")
            return

    # Initialize database
    initialize_enhanced_database(
        run_migrations=not args.skip_migrations,
        create_sample=args.sample_data,
        force_recreate=args.force_recreate,
    )


if __name__ == "__main__":
    main()

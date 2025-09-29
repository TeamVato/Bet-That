"""Production-grade scheduled odds import from The Odds API with comprehensive monitoring."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from adapters.odds.the_odds_api import (
    TheOddsAPIClient,
    TheOddsAPIConfig,
    TheOddsAPIError,
    TheOddsAPIKeyPoolExhaustedError,
    create_production_client,
    update_current_best_lines,
)
from db.migrate import migrate, parse_database_url


class PipelineMetrics:
    """Track pipeline execution metrics and performance."""

    def __init__(self):
        self.start_time = time.time()
        self.events_processed = 0
        self.odds_rows_fetched = 0
        self.odds_rows_persisted = 0
        self.best_lines_updated = 0
        self.api_requests_made = 0
        self.keys_exhausted = 0
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for logging/monitoring."""
        duration = time.time() - self.start_time
        return {
            "pipeline_duration_seconds": round(duration, 2),
            "events_processed": self.events_processed,
            "odds_rows_fetched": self.odds_rows_fetched,
            "odds_rows_persisted": self.odds_rows_persisted,
            "best_lines_updated": self.best_lines_updated,
            "api_requests_made": self.api_requests_made,
            "keys_exhausted": self.keys_exhausted,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "throughput_rows_per_second": (
                round(self.odds_rows_fetched / duration, 2) if duration > 0 else 0
            ),
            "success_rate": 1.0 if len(self.errors) == 0 else 0.0,
        }

    def log_summary(self, logger: logging.Logger) -> None:
        """Log comprehensive pipeline summary."""
        metrics = self.to_dict()

        if metrics["success_rate"] == 1.0:
            logger.info("Pipeline completed successfully")
        else:
            logger.error("Pipeline completed with errors")

        logger.info(f"Pipeline metrics: {json.dumps(metrics, indent=2)}")

        if self.errors:
            logger.error(f"Errors encountered: {self.errors}")
        if self.warnings:
            logger.warning(f"Warnings encountered: {self.warnings}")


class OddsImportPipeline:
    """Production-grade pipeline for importing odds from The Odds API."""

    def __init__(
        self, config: Optional[TheOddsAPIConfig] = None, database_path: Optional[Path] = None
    ):
        self.config = config or TheOddsAPIConfig.from_env()
        self.database_path = database_path or self._get_database_path()
        self.client: Optional[TheOddsAPIClient] = None
        self.metrics = PipelineMetrics()

        # Setup comprehensive logging
        self.logger = logging.getLogger(f"{__name__}.OddsImportPipeline")
        if not self.logger.handlers:
            # Create both console and file handlers
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Create logs directory and file handler
            log_dir = Path("storage/logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(
                log_dir / f"odds_import_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.DEBUG)

            # Create formatter
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)

    def _get_database_path(self) -> Path:
        """Get database path from environment configuration."""
        load_dotenv()
        url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
        return parse_database_url(url)

    def _initialize_client(self) -> None:
        """Initialize the Odds API client with proper error handling."""
        try:
            self.client = TheOddsAPIClient(self.config)
            self.logger.info(f"Initialized API client with {len(self.config.api_keys)} keys")

            # Log initial key pool status
            status = self.client.get_key_pool_status()
            self.logger.debug(f"Initial key pool status: {json.dumps(status, indent=2)}")

        except Exception as e:
            self.metrics.errors.append(f"Failed to initialize API client: {e}")
            self.logger.error(f"Failed to initialize API client: {e}")
            raise

    def _ensure_database_ready(self) -> None:
        """Ensure database schema is up-to-date and ready."""
        try:
            self.logger.info(f"Ensuring database schema at {self.database_path}")
            migrate(str(self.database_path))
            self.logger.info("Database schema validated")
        except Exception as e:
            self.metrics.errors.append(f"Database initialization failed: {e}")
            self.logger.error(f"Database initialization failed: {e}")
            raise

    def _fetch_odds_data(self, **fetch_params) -> pd.DataFrame:
        """Fetch odds data with comprehensive error handling and monitoring."""
        if not self.client:
            raise RuntimeError("API client not initialized")

        self.logger.info("Starting odds data fetch")

        try:
            # Log request parameters
            self.logger.info(f"Fetch parameters: {fetch_params}")

            # Fetch data
            df = self.client.fetch(**fetch_params)

            # Update metrics
            self.metrics.odds_rows_fetched = len(df)
            self.metrics.api_requests_made += 1

            # Validate fetched data
            if df.empty:
                self.metrics.warnings.append("No odds data fetched from API")
                self.logger.warning("No odds data fetched from API")
                return df

            # Log data quality metrics
            unique_events = df["event_id"].nunique() if "event_id" in df.columns else 0
            unique_bookmakers = (
                df["bookmaker_key"].nunique() if "bookmaker_key" in df.columns else 0
            )
            unique_markets = df["market_key"].nunique() if "market_key" in df.columns else 0

            self.logger.info(
                f"Fetched {len(df)} odds rows covering {unique_events} events, "
                f"{unique_bookmakers} bookmakers, {unique_markets} markets"
            )

            self.metrics.events_processed = unique_events

            return df

        except TheOddsAPIKeyPoolExhaustedError as e:
            self.metrics.keys_exhausted = len(self.config.api_keys)
            self.metrics.errors.append(f"All API keys exhausted: {e}")
            self.logger.error(f"All API keys exhausted: {e}")
            raise

        except TheOddsAPIError as e:
            self.metrics.errors.append(f"API error: {e}")
            self.logger.error(f"API error: {e}")
            raise

        except Exception as e:
            self.metrics.errors.append(f"Unexpected error during fetch: {e}")
            self.logger.error(f"Unexpected error during fetch: {e}")
            raise

    def _persist_snapshots(self, df: pd.DataFrame) -> None:
        """Persist odds snapshots with monitoring."""
        if df.empty:
            self.logger.info("No data to persist")
            return

        if not self.client:
            raise RuntimeError("API client not initialized")

        self.logger.info(f"Persisting {len(df)} odds snapshots")

        try:
            self.client.persist_snapshots(df, self.database_path)
            self.metrics.odds_rows_persisted = len(df)
            self.logger.info("Snapshots persisted successfully")

        except Exception as e:
            self.metrics.errors.append(f"Failed to persist snapshots: {e}")
            self.logger.error(f"Failed to persist snapshots: {e}")
            raise

    def _update_best_lines(self) -> None:
        """Update current best lines table with monitoring."""
        self.logger.info("Updating current best lines")

        try:
            best_lines_df = update_current_best_lines(self.database_path)
            self.metrics.best_lines_updated = len(best_lines_df)

            if best_lines_df.empty:
                self.metrics.warnings.append("No best lines computed")
                self.logger.warning("No best lines computed")
            else:
                self.logger.info(f"Updated {len(best_lines_df)} best lines")

        except Exception as e:
            self.metrics.errors.append(f"Failed to update best lines: {e}")
            self.logger.error(f"Failed to update best lines: {e}")
            raise

    def _save_execution_history(self) -> None:
        """Save pipeline execution history for monitoring and debugging."""
        try:
            history_dir = Path("storage/pipeline_history")
            history_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = history_dir / f"odds_import_{timestamp}.json"

            execution_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pipeline_type": "odds_import_api",
                "config": {
                    "sport_key": self.config.sport_key,
                    "regions": self.config.regions,
                    "markets": self.config.markets,
                    "total_keys": len(self.config.api_keys),
                },
                "metrics": self.metrics.to_dict(),
                "key_pool_final_status": self.client.get_key_pool_status() if self.client else None,
            }

            with open(history_file, "w") as f:
                json.dump(execution_record, f, indent=2)

            self.logger.info(f"Execution history saved to {history_file}")

        except Exception as e:
            self.logger.warning(f"Failed to save execution history: {e}")

    def run(self, **fetch_params) -> Dict[str, Any]:
        """Execute the complete odds import pipeline.

        Args:
            **fetch_params: Parameters to pass to the odds API fetch

        Returns:
            Dictionary with execution metrics and status
        """
        self.logger.info("Starting odds import pipeline")

        try:
            # Initialize components
            self._initialize_client()
            self._ensure_database_ready()

            # Execute pipeline steps
            odds_df = self._fetch_odds_data(**fetch_params)
            self._persist_snapshots(odds_df)
            self._update_best_lines()

            # Save execution history
            self._save_execution_history()

            # Log final summary
            self.metrics.log_summary(self.logger)

            return {
                "success": True,
                "metrics": self.metrics.to_dict(),
                "key_pool_status": self.client.get_key_pool_status() if self.client else None,
            }

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.metrics.errors.append(f"Pipeline failure: {e}")
            self.metrics.log_summary(self.logger)

            return {
                "success": False,
                "error": str(e),
                "metrics": self.metrics.to_dict(),
                "key_pool_status": self.client.get_key_pool_status() if self.client else None,
            }


def create_cron_job_script() -> None:
    """Create a cron-compatible script for scheduled execution."""
    script_content = """#!/usr/bin/env bash
set -euo pipefail

# Production odds import cron script
# Schedule: Daily at 15:05 UTC (5 minutes after typical Google Sheets export)
# Cron entry: 5 15 * * * /path/to/Bet-That/scripts/cron_odds_import.sh

# Change to project directory
cd "$(dirname "$0")/.."

# Activate virtual environment
source .venv/bin/activate

# Set production environment
export PYTHONPATH="$PWD"
export ODDS_IMPORT_MODE="scheduled"

# Run odds import with logging
python jobs/import_odds_from_api.py \\
    --log-level INFO \\
    --save-metrics \\
    --enable-monitoring \\
    2>&1 | tee -a storage/logs/cron_odds_import.log

# Check exit code and optionally send alerts
if [ $? -ne 0 ]; then
    echo "ERROR: Odds import failed at $(date)" >> storage/logs/cron_errors.log
    # Add your alerting mechanism here (email, Slack, etc.)
fi
"""

    script_path = Path("scripts/cron_odds_import.sh")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, "w") as f:
        f.write(script_content)

    # Make script executable
    script_path.chmod(0o755)

    print(f"Created cron job script at {script_path}")
    print("\nTo schedule daily execution at 15:05 UTC, add this to your crontab:")
    print(f"5 15 * * * {script_path.absolute()}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(description="Import odds from The Odds API")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )

    parser.add_argument(
        "--markets",
        help="Override markets to fetch (comma-separated)",
    )

    parser.add_argument(
        "--bookmakers",
        help="Limit to specific bookmakers (comma-separated)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch data but don't persist to database",
    )

    parser.add_argument(
        "--save-metrics",
        action="store_true",
        help="Save detailed execution metrics",
    )

    parser.add_argument(
        "--create-cron-script",
        action="store_true",
        help="Create cron job script for scheduled execution",
    )

    parser.add_argument(
        "--enable-monitoring",
        action="store_true",
        help="Enable enhanced monitoring and alerting",
    )

    args = parser.parse_args()

    # Handle special commands
    if args.create_cron_script:
        create_cron_job_script()
        return

    # Setup logging level
    logging.basicConfig(level=getattr(logging, args.log_level))

    # Prepare fetch parameters
    fetch_params = {}
    if args.markets:
        fetch_params["markets"] = args.markets
    if args.bookmakers:
        fetch_params["bookmakers"] = args.bookmakers

    # Initialize and run pipeline
    try:
        pipeline = OddsImportPipeline()

        if args.dry_run:
            # Dry run: fetch but don't persist
            pipeline.logger.info("DRY RUN MODE: Data will be fetched but not persisted")
            pipeline._initialize_client()
            odds_df = pipeline._fetch_odds_data(**fetch_params)

            print(f"\nDRY RUN RESULTS:")
            print(f"- Fetched {len(odds_df)} odds rows")
            print(f"- Events: {odds_df['event_id'].nunique() if not odds_df.empty else 0}")
            print(f"- Bookmakers: {odds_df['bookmaker_key'].nunique() if not odds_df.empty else 0}")
            print(f"- Markets: {odds_df['market_key'].nunique() if not odds_df.empty else 0}")

            if not odds_df.empty:
                print(f"\nSample data:")
                print(odds_df.head())

            return

        # Regular execution
        result = pipeline.run(**fetch_params)

        # Print summary
        if result["success"]:
            print("\n✅ Pipeline completed successfully")
            metrics = result["metrics"]
            print(f"📊 Fetched: {metrics['odds_rows_fetched']} rows")
            print(f"💾 Persisted: {metrics['odds_rows_persisted']} rows")
            print(f"🎯 Best lines: {metrics['best_lines_updated']} updated")
            print(f"⏱️  Duration: {metrics['pipeline_duration_seconds']}s")
        else:
            print(f"\n❌ Pipeline failed: {result['error']}")
            sys.exit(1)

        # Save detailed metrics if requested
        if args.save_metrics:
            metrics_file = (
                Path("storage/metrics")
                / f"odds_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            metrics_file.parent.mkdir(parents=True, exist_ok=True)

            with open(metrics_file, "w") as f:
                json.dump(result, f, indent=2)

            print(f"📈 Detailed metrics saved to {metrics_file}")

    except KeyboardInterrupt:
        print("\n🛑 Pipeline interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n💥 Pipeline failed with unexpected error: {e}")
        logging.error(f"Unexpected pipeline failure: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

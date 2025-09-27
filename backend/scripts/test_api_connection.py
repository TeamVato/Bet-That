from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from dotenv import load_dotenv  # noqa: E402

from app.services.odds_api_manager import (  # noqa: E402
    DailyLimitReached,
    OddsAPIError,
    OddsAPIManager,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment(env_path: Path) -> None:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment variables from %s", env_path)
    else:
        logger.warning("No .env file found at %s; relying on system environment.", env_path)


async def run_test(force_refresh: bool) -> int:
    manager = OddsAPIManager()
    usage_before = await manager.get_usage_stats()
    logger.info("Daily usage before call: %s", usage_before)

    try:
        odds = await manager.fetch_current_week_odds(force_refresh=force_refresh)
    except DailyLimitReached as exc:
        logger.error("Daily limit reached: %s", exc)
        return 2
    except OddsAPIError as exc:
        logger.error("Odds API failure: %s", exc)
        return 1

    logger.info("Fetched %d NFL matchups.", len(odds))
    if odds:
        sample = odds[0]
        logger.info("Sample matchup: %s", json.dumps(sample, indent=2)[:500])

    usage_after = await manager.get_usage_stats()
    logger.info("Daily usage after call: %s", usage_after)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Odds API connectivity and caching.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a fresh API call; otherwise cache/demo data is used when available.",
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=BASE_DIR / ".env",
        help="Path to the environment file.",
    )
    args = parser.parse_args()

    load_environment(args.env)
    return asyncio.run(run_test(force_refresh=args.force))


if __name__ == "__main__":
    raise SystemExit(main())

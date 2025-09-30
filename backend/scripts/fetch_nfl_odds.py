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

from app.services.odds_api_manager import DailyLimitReached, OddsAPIManager  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_environment(env_path: Path) -> None:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment variables from %s", env_path)
    else:
        logger.warning(
            "No .env file found at %s; running in demo mode if no keys are set.", env_path
        )


async def fetch_and_cache(limit_output: int) -> int:
    manager = OddsAPIManager()
    try:
        odds = await manager.fetch_current_week_odds()
    except DailyLimitReached as exc:
        logger.error("Cannot fetch odds; daily limit reached: %s", exc)
        return 2

    logger.info("Retrieved %d matchups.", len(odds))
    preview = odds[:limit_output] if 0 < limit_output < len(odds) else odds
    if preview:
        logger.info("Preview data:\n%s", json.dumps(preview, indent=2)[:1000])

    usage = await manager.get_usage_stats()
    logger.info("Usage snapshot: %s", usage)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and cache current NFL odds.")
    parser.add_argument(
        "--env",
        type=Path,
        default=BASE_DIR / ".env",
        help="Path to the environment file.",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=3,
        help="Number of matchups to include in the preview output (0 for all).",
    )
    args = parser.parse_args()

    load_environment(args.env)
    return asyncio.run(fetch_and_cache(limit_output=args.preview))


if __name__ == "__main__":
    raise SystemExit(main())

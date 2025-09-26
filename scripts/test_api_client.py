#!/usr/bin/env python3
"""Test script for the production-grade Odds API client."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from adapters.odds.the_odds_api import (
    TheOddsAPIClient,
    TheOddsAPIConfig,
    create_production_client,
)

def test_api_client():
    """Test the API client with comprehensive logging."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Testing production-grade Odds API client")

    try:
        # Create client
        client = create_production_client()

        # Log key pool status
        status = client.get_key_pool_status()
        logger.info(f"Key pool status: {status['available_keys']}/{status['total_keys']} keys available")

        # Test fetch (dry run - small request)
        logger.info("Testing odds fetch...")
        df = client.fetch(markets="h2h")  # Minimal request

        logger.info(f"✅ Fetch successful: {len(df)} rows")

        if not df.empty:
            logger.info(f"Sample data columns: {list(df.columns)}")
            logger.info(f"Unique events: {df['event_id'].nunique()}")
            logger.info(f"Unique bookmakers: {df['bookmaker_key'].nunique()}")

        # Log final key pool status
        final_status = client.get_key_pool_status()
        logger.info(f"Final key pool status: {final_status}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_client()
    sys.exit(0 if success else 1)
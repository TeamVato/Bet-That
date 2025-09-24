"""CLI job to poll The Odds API and store snapshots."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import argparse
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from adapters.odds.the_odds_api import TheOddsAPIClient, update_current_best_lines
from db.migrate import migrate, parse_database_url


def get_database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    return parse_database_url(url)


def poll_once(client: TheOddsAPIClient, database_path: Path, *, markets: str | None = None) -> None:
    df = client.fetch(markets=markets)
    client.persist_snapshots(df, database_path)
    update_current_best_lines(database_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll The Odds API and store snapshots")
    parser.add_argument("--interval", type=int, help="Loop interval in seconds")
    parser.add_argument("--markets", help="Override markets list", default=None)
    args = parser.parse_args()

    database_path = get_database_path()
    if not database_path.exists():
        print("Database not found; running migration first...")
        migrate()

    client = TheOddsAPIClient()

    try:
        if args.interval:
            print(f"Polling The Odds API every {args.interval} seconds. Press Ctrl+C to stop.")
            while True:
                poll_once(client, database_path, markets=args.markets)
                time.sleep(args.interval)
        else:
            poll_once(client, database_path, markets=args.markets)
    except KeyboardInterrupt:
        print("Polling stopped by user.")


if __name__ == "__main__":
    main()

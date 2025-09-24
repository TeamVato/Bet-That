"""Minimal The Odds API poller with daily key rotation."""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Tuple

sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from adapters.odds.the_odds_api import (
    TheOddsAPIClient,
    TheOddsAPIConfig,
    update_current_best_lines,
)
from db.migrate import migrate, parse_database_url

DEFAULT_SPORT = "americanfootball_nfl"
DEFAULT_REGION = "us"
DEFAULT_BOOKS = "draftkings,fanduel,betmgm,caesars"
DEFAULT_MARKETS = "player_pass_yards,player_pass_completions,player_pass_attempts"
DEFAULT_SLEEP = 900  # 15 minutes


def get_database_path() -> Path:
    load_dotenv()
    url = os.getenv("DATABASE_URL", "sqlite:///storage/odds.db")
    return parse_database_url(url)


def select_api_key(now: time.struct_time | None = None) -> Tuple[str, int, int]:
    """Rotate through ODDS_API_KEYS based on the day of year."""
    keys_env = os.getenv("ODDS_API_KEYS", "")
    keys = [k.strip() for k in keys_env.split(",") if k.strip()]
    if not keys:
        single = os.getenv("ODDS_API_KEY")
        if not single:
            raise SystemExit("Set ODDS_API_KEYS or ODDS_API_KEY to poll The Odds API.")
        return single, 0, 1
    if now is None:
        now = time.localtime()
    idx = now.tm_yday % len(keys)
    key = keys[idx]
    print(
        f"Using Odds API key {idx + 1}/{len(keys)} for day {now.tm_yday}. "
        "(ODDS_API_KEYS rotation)"
    )
    return key, idx, len(keys)


def build_client(*, api_key: str, sport: str, region: str, markets: str) -> TheOddsAPIClient:
    config = TheOddsAPIConfig(
        api_key=api_key,
        sport_key=sport,
        regions=region,
        markets=markets,
        odds_format=os.getenv("ODDS_API_ODDS_FORMAT", "american"),
        date_format="iso",
    )
    return TheOddsAPIClient(config=config)


def poll_once(*, sport: str, books: str | None, markets: str, region: str, database_path: Path) -> None:
    api_key, _, _ = select_api_key()
    client = build_client(api_key=api_key, sport=sport, region=region, markets=markets)
    print(
        "Polling The Odds API: "
        f"sport={sport} books={books or 'ALL'} markets={markets} region={region}"
    )
    df = client.fetch(markets=markets, bookmakers=books)
    client.persist_snapshots(df, database_path)
    update_current_best_lines(database_path)
    usage = getattr(client, "last_usage", {}) or {}
    if usage:
        used = usage.get("requests_used") or "?"
        remaining = usage.get("requests_remaining") or "?"
        reset = usage.get("requests_reset") or "?"
        print(f"Usage headers: used={used} remaining={remaining} reset={reset}")
    print("Poll complete.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll The Odds API and store snapshots")
    parser.set_defaults(once=True)
    parser.add_argument(
        "--once",
        dest="once",
        action="store_true",
        help="Poll exactly once (default).",
    )
    parser.add_argument(
        "--loop",
        dest="once",
        action="store_false",
        help="Continuously poll on an interval (requires --sleep).",
    )
    parser.add_argument(
        "--sleep",
        type=int,
        default=int(os.getenv("ODDS_API_POLL_SLEEP", str(DEFAULT_SLEEP))),
        help="Seconds to sleep between polls when looping (default: 900).",
    )
    parser.add_argument(
        "--sport",
        default=os.getenv("ODDS_API_SPORT_KEY", DEFAULT_SPORT),
        help="Odds API sport key (default: americanfootball_nfl).",
    )
    parser.add_argument(
        "--region",
        default=os.getenv("ODDS_API_REGION", DEFAULT_REGION),
        help="Odds API region filter (default: us).",
    )
    parser.add_argument(
        "--books",
        default=os.getenv("ODDS_API_BOOKS", DEFAULT_BOOKS),
        help="Comma separated bookmaker keys to request (default: draftkings,fanduel,betmgm,caesars).",
    )
    parser.add_argument(
        "--markets",
        default=os.getenv("ODDS_API_MARKETS", DEFAULT_MARKETS),
        help="Comma separated market keys to request (default: QB passing props).",
    )
    args = parser.parse_args()

    database_path = get_database_path()
    if not database_path.exists():
        print("Database not found; running migration first...")
        migrate()

    books = args.books.strip() if args.books else ""
    if books.lower() == "all":
        books = ""

    try:
        if args.once:
            poll_once(
                sport=args.sport,
                books=books or None,
                markets=args.markets,
                region=args.region,
                database_path=database_path,
            )
        else:
            sleep_interval = max(30, int(args.sleep))
            print(
                f"Polling The Odds API every {sleep_interval} seconds. Press Ctrl+C to stop."
            )
            while True:
                poll_once(
                    sport=args.sport,
                    books=books or None,
                    markets=args.markets,
                    region=args.region,
                    database_path=database_path,
                )
                time.sleep(sleep_interval)
    except KeyboardInterrupt:
        print("Polling stopped by user.")


+if __name__ == "__main__":
+    main()

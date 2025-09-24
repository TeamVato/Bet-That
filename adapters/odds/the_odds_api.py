"""Adapter for The Odds API (https://the-odds-api.com/)."""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import (RetryCallState, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from adapters.odds.base import OddsAdapter

DEFAULT_SPORT_KEY = "americanfootball_nfl"
API_BASE_URL = "https://api.the-odds-api.com/v4"


class TheOddsAPIError(RuntimeError):
    """Raised when The Odds API returns an error response."""


@dataclass
class TheOddsAPIConfig:
    """Configuration for The Odds API requests."""

    api_key: str
    sport_key: str = DEFAULT_SPORT_KEY
    regions: str = "us"
    markets: str = "h2h,spreads,totals"
    odds_format: str = "american"
    date_format: str = "iso"

    @classmethod
    def from_env(cls) -> "TheOddsAPIConfig":
        load_dotenv()
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            raise TheOddsAPIError("ODDS_API_KEY is required to poll The Odds API")
        return cls(
            api_key=api_key,
            sport_key=os.getenv("ODDS_SPORT_KEY", DEFAULT_SPORT_KEY),
            regions=os.getenv("ODDS_REGION", "us"),
            markets=os.getenv("ODDS_MARKETS", "h2h,spreads,totals"),
            odds_format=os.getenv("ODDS_ODDS_FORMAT", "american"),
        )


def _log_retry(retry_state: RetryCallState) -> None:
    exc = retry_state.outcome.exception()
    if exc:
        print(f"Retrying due to error: {exc}")


class TheOddsAPIClient(OddsAdapter):
    """Client for fetching odds from The Odds API."""

    def __init__(self, config: Optional[TheOddsAPIConfig] = None) -> None:
        self.config = config or TheOddsAPIConfig.from_env()

    @retry(
        reraise=True,
        retry=retry_if_exception_type((requests.RequestException, TheOddsAPIError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        after=_log_retry,
    )
    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{API_BASE_URL}/{endpoint}"
        query = {"apiKey": self.config.api_key, **(params or {})}
        response = requests.get(url, params=query, timeout=15)
        if response.status_code == 401:
            raise TheOddsAPIError("Invalid or missing The Odds API key")
        if response.status_code == 429:
            raise TheOddsAPIError("Rate limit hit for The Odds API")
        if not response.ok:
            raise TheOddsAPIError(f"API request failed: {response.status_code} {response.text}")
        remaining = response.headers.get("X-Requests-Remaining")
        if remaining is not None:
            print(f"The Odds API requests remaining this month: {remaining}")
        return response.json()

    def fetch(self, **params: Any) -> pd.DataFrame:
        """Fetch odds for the configured sport and normalize to a DataFrame."""
        fetched_at = datetime.now(timezone.utc)
        payload = self._request(
            f"sports/{self.config.sport_key}/odds",
            {
                "regions": self.config.regions,
                "markets": params.get("markets", self.config.markets),
                "oddsFormat": self.config.odds_format,
                "dateFormat": self.config.date_format,
            },
        )
        df = normalize_odds_response(payload, fetched_at=fetched_at)
        print(f"Fetched {len(df)} odds rows from The Odds API")
        return df

    def persist_snapshots(self, df: pd.DataFrame, database_path: Path) -> None:
        """Persist normalized odds snapshots to SQLite, deduplicating duplicates."""
        if df.empty:
            print("No odds rows to persist.")
            return
        database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            rows = df.to_dict("records")
            for row in rows:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO odds_snapshots (
                        fetched_at, sport_key, event_id, market_key, bookmaker_key,
                        line, price, outcome, points, iso_time, odds_raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["fetched_at"],
                        row["sport_key"],
                        row["event_id"],
                        row["market_key"],
                        row["bookmaker_key"],
                        row.get("line"),
                        row.get("price"),
                        row.get("outcome"),
                        row.get("points"),
                        row.get("iso_time"),
                        row.get("odds_raw_json"),
                    ),
                )
            conn.commit()
        print(f"Persisted {len(df)} snapshots to {database_path}")


def normalize_odds_response(payload: Iterable[Dict[str, Any]], *, fetched_at: datetime) -> pd.DataFrame:
    """Normalize The Odds API response into a tidy DataFrame."""
    rows: List[Dict[str, Any]] = []
    fetched_at_iso = fetched_at.astimezone(timezone.utc).isoformat()
    for event in payload or []:
        sport_key = event.get("sport_key")
        event_id = event.get("id") or event.get("event_id")
        for bookmaker in event.get("bookmakers", []):
            bookmaker_key = bookmaker.get("key")
            last_update = bookmaker.get("last_update")
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                market_last_update = market.get("last_update") or last_update
                for outcome in market.get("outcomes", []):
                    rows.append(
                        {
                            "fetched_at": fetched_at_iso,
                            "sport_key": sport_key,
                            "event_id": event_id,
                            "commence_time": event.get("commence_time"),
                            "home_team": event.get("home_team"),
                            "away_team": event.get("away_team"),
                            "bookmaker_key": bookmaker_key,
                            "market_key": market_key,
                            "outcome": outcome.get("name"),
                            "points": outcome.get("point"),
                            "line": outcome.get("point"),
                            "price": outcome.get("price"),
                            "iso_time": market_last_update,
                            "odds_raw_json": json.dumps(
                                {
                                    "event_id": event_id,
                                    "bookmaker_key": bookmaker_key,
                                    "market_key": market_key,
                                    "outcome": outcome,
                                }
                            ),
                        }
                    )
    df = pd.DataFrame(rows)
    if not df.empty:
        numeric_cols = ["price", "points", "line"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    expected_cols = [
        "fetched_at",
        "sport_key",
        "event_id",
        "commence_time",
        "home_team",
        "away_team",
        "bookmaker_key",
        "market_key",
        "outcome",
        "points",
        "price",
        "iso_time",
        "line",
        "odds_raw_json",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df[expected_cols]


def compute_current_best_lines(df: pd.DataFrame) -> pd.DataFrame:
    """Return the best available price per event/market/outcome."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "event_id",
                "market_key",
                "outcome",
                "bookmaker_key",
                "price",
                "points",
                "fetched_at",
            ]
        )
    df = df.copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    idx = df.groupby(["event_id", "market_key", "outcome"])["price"].idxmax()
    best = df.loc[idx]
    return best[[
        "event_id",
        "market_key",
        "outcome",
        "bookmaker_key",
        "price",
        "points",
        "fetched_at",
    ]].rename(columns={"bookmaker_key": "best_book", "price": "best_price", "points": "best_points"})


def update_current_best_lines(database_path: Path) -> pd.DataFrame:
    """Load odds snapshots and update the current_best_lines table."""
    with sqlite3.connect(database_path) as conn:
        df = pd.read_sql_query("SELECT * FROM odds_snapshots", conn)
        best = compute_current_best_lines(df)
        cursor = conn.cursor()
        for row in best.to_dict("records"):
            cursor.execute(
                """
                INSERT OR REPLACE INTO current_best_lines (
                    event_id, market_key, outcome, best_book, best_price, best_points, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["event_id"],
                    row["market_key"],
                    row["outcome"],
                    row["best_book"],
                    int(row["best_price"]),
                    row.get("best_points"),
                    row.get("fetched_at"),
                ),
            )
        conn.commit()
    print("Updated current best lines table")
    return best

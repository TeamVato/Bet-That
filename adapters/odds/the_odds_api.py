"""Production-grade adapter for The Odds API with key pool management and atomic operations."""
from __future__ import annotations

import json
import logging
import os
import random
import sqlite3
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from adapters.odds.base import OddsAdapter

# Import validation schemas (optional - graceful fallback if not available)
try:
    from schemas.odds_schemas import validate_odds_snapshots, validate_current_best_lines
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    validate_odds_snapshots = lambda df: df
    validate_current_best_lines = lambda df: df

DEFAULT_SPORT_KEY = "americanfootball_nfl"
API_BASE_URL = "https://api.the-odds-api.com/v4"


class TheOddsAPIError(RuntimeError):
    """Raised when The Odds API returns an error response."""


class TheOddsAPIRateLimitError(TheOddsAPIError):
    """Raised when API rate limit is exceeded."""


class TheOddsAPIQuotaExceededError(TheOddsAPIError):
    """Raised when API quota is exceeded."""


class TheOddsAPIKeyPoolExhaustedError(TheOddsAPIError):
    """Raised when all API keys are exhausted or rate-limited."""


@dataclass
class APIKeyInfo:
    """Information about an API key's usage and status."""

    key: str
    requests_used: int = 0
    requests_remaining: Optional[int] = None
    requests_reset: Optional[str] = None
    last_used_at: Optional[datetime] = None
    consecutive_failures: int = 0
    is_rate_limited: bool = False
    rate_limit_reset_at: Optional[datetime] = None

    @property
    def is_available(self) -> bool:
        """Check if this key is available for use."""
        if self.is_rate_limited:
            if self.rate_limit_reset_at and datetime.now(timezone.utc) > self.rate_limit_reset_at:
                self.is_rate_limited = False
                self.rate_limit_reset_at = None
            else:
                return False

        # Consider key unavailable if quota is exhausted (remaining = 0)
        if self.requests_remaining is not None and self.requests_remaining <= 0:
            return False

        # Consider key temporarily unavailable after consecutive failures
        return self.consecutive_failures < 3


@dataclass
class TheOddsAPIConfig:
    """Configuration for The Odds API requests with key pool management."""

    api_keys: List[str]
    sport_key: str = DEFAULT_SPORT_KEY
    regions: str = "us"
    markets: str = "h2h,spreads,totals,player_props"
    odds_format: str = "american"
    date_format: str = "iso"
    max_retries: int = 3
    base_timeout: float = 15.0
    max_timeout: float = 60.0
    bookmakers: Optional[str] = None
    enable_props: bool = True

    # Key rotation and circuit breaker settings
    key_failure_threshold: int = 3
    key_cooldown_minutes: int = 15
    pool_exhaustion_cooldown_minutes: int = 60

    @classmethod
    def from_env(cls) -> "TheOddsAPIConfig":
        load_dotenv()

        # Support both single key and multiple keys
        api_keys_env = os.getenv("ODDS_API_KEYS") or os.getenv("ODDS_API_KEY")
        if not api_keys_env:
            raise TheOddsAPIError(
                "ODDS_API_KEYS (comma-separated) or ODDS_API_KEY is required to poll The Odds API"
            )

        # Parse comma-separated keys and clean them
        api_keys = [key.strip() for key in api_keys_env.split(",") if key.strip()]
        if not api_keys:
            raise TheOddsAPIError("No valid API keys found in ODDS_API_KEYS")

        # Default markets for production use
        default_markets = "h2h,spreads,totals"
        if os.getenv("ENABLE_PLAYER_PROPS", "false").lower() in ("true", "1", "yes"):
            default_markets += ",player_props"

        return cls(
            api_keys=api_keys,
            sport_key=os.getenv("ODDS_SPORT_KEY", DEFAULT_SPORT_KEY),
            regions=os.getenv("ODDS_REGION", "us"),
            markets=os.getenv("ODDS_MARKETS", default_markets),
            odds_format=os.getenv("ODDS_ODDS_FORMAT", "american"),
            bookmakers=os.getenv("ODDS_BOOKMAKERS"),  # Optional constraint
            max_retries=int(os.getenv("ODDS_MAX_RETRIES", "3")),
            base_timeout=float(os.getenv("ODDS_BASE_TIMEOUT", "15.0")),
            max_timeout=float(os.getenv("ODDS_MAX_TIMEOUT", "60.0")),
        )


def _log_retry(retry_state: RetryCallState) -> None:
    """Enhanced retry logging with attempt details."""
    exc = retry_state.outcome.exception()
    attempt = retry_state.attempt_number
    if exc:
        logging.warning(
            f"API request attempt {attempt} failed: {exc.__class__.__name__}: {exc}"
        )


class TheOddsAPIClient(OddsAdapter):
    """Production-grade client for fetching odds from The Odds API.

    Features:
    - Key pool management with automatic rotation
    - Circuit breaker pattern for failed keys
    - Atomic snapshot operations (all-or-nothing)
    - Comprehensive error handling and monitoring
    - Rate limit and quota tracking
    - Exponential backoff with jitter
    """

    def __init__(self, config: Optional[TheOddsAPIConfig] = None) -> None:
        self.config = config or TheOddsAPIConfig.from_env()

        # Initialize key pool
        self.key_pool: Dict[str, APIKeyInfo] = {
            key: APIKeyInfo(key=key) for key in self.config.api_keys
        }

        # Track overall client state
        self.last_successful_fetch: Optional[datetime] = None
        self.consecutive_pool_failures: int = 0
        self.pool_exhausted_at: Optional[datetime] = None

        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _get_available_key(self) -> Optional[APIKeyInfo]:
        """Get the next available API key from the pool."""
        available_keys = [info for info in self.key_pool.values() if info.is_available]

        if not available_keys:
            # Check if pool exhaustion cooldown has expired
            if self.pool_exhausted_at:
                cooldown_duration = timezone.utc.now() - self.pool_exhausted_at
                if cooldown_duration.total_seconds() < (self.config.pool_exhaustion_cooldown_minutes * 60):
                    return None
                else:
                    # Reset pool exhaustion state
                    self.pool_exhausted_at = None
                    self.consecutive_pool_failures = 0
                    # Reset all keys' failure counts for a fresh start
                    for key_info in self.key_pool.values():
                        key_info.consecutive_failures = 0
                        key_info.is_rate_limited = False
                        key_info.rate_limit_reset_at = None
                    return self._get_available_key()
            return None

        # Choose key with least recent usage (or random if tied)
        available_keys.sort(key=lambda k: k.last_used_at or datetime.min.replace(tzinfo=timezone.utc))
        return available_keys[0]

    def _update_key_usage(self, key_info: APIKeyInfo, response: requests.Response) -> None:
        """Update key usage statistics from API response headers."""
        key_info.last_used_at = datetime.now(timezone.utc)
        key_info.requests_used = int(response.headers.get("X-Requests-Used", key_info.requests_used))

        if "X-Requests-Remaining" in response.headers:
            key_info.requests_remaining = int(response.headers["X-Requests-Remaining"])

        if "X-Requests-Reset" in response.headers:
            key_info.requests_reset = response.headers["X-Requests-Reset"]

        # Reset failure count on successful request
        key_info.consecutive_failures = 0

        # Log usage information
        self.logger.info(
            f"API usage for key {key_info.key[:8]}**: "
            f"used={key_info.requests_used}, remaining={key_info.requests_remaining}, "
            f"reset={key_info.requests_reset}"
        )

    def _handle_key_failure(self, key_info: APIKeyInfo, exc: Exception, response: Optional[requests.Response] = None) -> None:
        """Handle API key failure and potentially mark it as rate-limited."""
        key_info.consecutive_failures += 1

        if response and response.status_code == 429:
            key_info.is_rate_limited = True
            # Set rate limit reset time (default to 15 minutes if not provided)
            reset_time = datetime.now(timezone.utc).replace(minute=(datetime.now().minute + self.config.key_cooldown_minutes) % 60)
            key_info.rate_limit_reset_at = reset_time

            self.logger.warning(
                f"Key {key_info.key[:8]}** rate-limited, cooldown until {reset_time}"
            )

        self.logger.error(
            f"Key {key_info.key[:8]}** failed (attempt {key_info.consecutive_failures}): {exc}"
        )

    @retry(
        reraise=True,
        retry=retry_if_exception_type((requests.RequestException, TheOddsAPIRateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(multiplier=1, max=30, jitter=5),
        after=_log_retry,
    )
    def _request_with_key(self, key_info: APIKeyInfo, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Tuple[Any, requests.Response]:
        """Make a request with a specific API key."""
        url = f"{API_BASE_URL}/{endpoint}"
        query = {"apiKey": key_info.key, **(params or {})}

        timeout = min(self.config.base_timeout * (2 ** key_info.consecutive_failures), self.config.max_timeout)

        try:
            response = requests.get(url, params=query, timeout=timeout)

            # Handle different error conditions
            if response.status_code == 401:
                raise TheOddsAPIError(f"Invalid API key {key_info.key[:8]}**")
            elif response.status_code == 429:
                raise TheOddsAPIRateLimitError(f"Rate limit exceeded for key {key_info.key[:8]}**")
            elif response.status_code == 403:
                # Check if this is a quota exceeded error
                error_text = response.text.lower()
                if "quota" in error_text or "limit" in error_text:
                    raise TheOddsAPIQuotaExceededError(f"API quota exceeded for key {key_info.key[:8]}**")
                else:
                    raise TheOddsAPIError(f"Access forbidden for key {key_info.key[:8]}**: {response.text}")
            elif not response.ok:
                raise TheOddsAPIError(
                    f"API request failed for key {key_info.key[:8]}**: "
                    f"{response.status_code} {response.text}"
                )

            return response.json(), response

        except requests.RequestException as e:
            self.logger.error(f"Network error with key {key_info.key[:8]}**: {e}")
            raise

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a request using the key pool with automatic rotation and failure handling."""
        last_exception = None

        # Try each available key once
        for attempt in range(len(self.config.api_keys)):
            key_info = self._get_available_key()

            if not key_info:
                if not self.pool_exhausted_at:
                    self.pool_exhausted_at = datetime.now(timezone.utc)
                    self.logger.error(
                        f"All API keys exhausted or rate-limited. Pool will reset in "
                        f"{self.config.pool_exhaustion_cooldown_minutes} minutes."
                    )
                raise TheOddsAPIKeyPoolExhaustedError(
                    "All API keys are exhausted or rate-limited. "
                    f"Pool will reset in {self.config.pool_exhaustion_cooldown_minutes} minutes."
                )

            try:
                data, response = self._request_with_key(key_info, endpoint, params)
                self._update_key_usage(key_info, response)
                self.last_successful_fetch = datetime.now(timezone.utc)
                self.consecutive_pool_failures = 0
                return data

            except (TheOddsAPIRateLimitError, TheOddsAPIQuotaExceededError) as e:
                self._handle_key_failure(key_info, e, getattr(e, 'response', None))
                last_exception = e
                continue  # Try next key

            except (TheOddsAPIError, requests.RequestException) as e:
                self._handle_key_failure(key_info, e)
                last_exception = e
                continue  # Try next key

        # If we get here, all keys failed
        self.consecutive_pool_failures += 1
        if last_exception:
            raise last_exception
        else:
            raise TheOddsAPIError("All API keys failed with unknown errors")

    def fetch(self, **params: Any) -> pd.DataFrame:
        """Fetch odds for the configured sport and normalize to a DataFrame.

        Returns:
            pd.DataFrame: Normalized odds data with comprehensive metadata

        Raises:
            TheOddsAPIKeyPoolExhaustedError: When all keys are exhausted/rate-limited
            TheOddsAPIError: For other API-related errors
        """
        fetch_start_time = time.time()
        fetched_at = datetime.now(timezone.utc)

        # Build request parameters
        request_params = {
            "regions": self.config.regions,
            "markets": params.get("markets", self.config.markets),
            "oddsFormat": self.config.odds_format,
            "dateFormat": self.config.date_format,
        }

        # Add optional bookmaker filter
        bookmakers = params.get("bookmakers") or self.config.bookmakers
        if bookmakers:
            request_params["bookmakers"] = bookmakers

        self.logger.info(
            f"Fetching odds for {self.config.sport_key} with params: {request_params}"
        )

        try:
            payload = self._request(
                f"sports/{self.config.sport_key}/odds",
                request_params
            )

            df = normalize_odds_response(payload, fetched_at=fetched_at)

            fetch_duration = time.time() - fetch_start_time
            self.logger.info(
                f"Successfully fetched {len(df)} odds rows in {fetch_duration:.2f}s"
            )

            return df

        except Exception as e:
            fetch_duration = time.time() - fetch_start_time
            self.logger.error(
                f"Failed to fetch odds after {fetch_duration:.2f}s: {e}"
            )
            raise

    def persist_snapshots(self, df: pd.DataFrame, database_path: Path) -> None:
        """Persist normalized odds snapshots to SQLite with atomic operations.

        Uses atomic writes to ensure either all data is persisted or none,
        preventing partial writes that could corrupt the database state.

        Args:
            df: Normalized odds DataFrame to persist
            database_path: Path to SQLite database
        """
        if df.empty:
            self.logger.info("No odds rows to persist")
            return

        database_path.parent.mkdir(parents=True, exist_ok=True)
        persist_start_time = time.time()

        # Create a temporary database for atomic operations
        temp_db = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
                temp_db = Path(temp_file.name)

            # First, copy the existing database to temp location
            if database_path.exists():
                import shutil
                shutil.copy2(database_path, temp_db)
            else:
                # Initialize new database with schema
                self._initialize_database_schema(temp_db)

            # Perform the insert operation on temp database
            rows_inserted = 0
            with sqlite3.connect(temp_db, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("BEGIN IMMEDIATE")

                try:
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
                        if cursor.rowcount > 0:
                            rows_inserted += cursor.rowcount

                    conn.commit()

                    # Atomic move: replace original database with temp database
                    import shutil
                    shutil.move(temp_db, database_path)
                    temp_db = None  # Don't delete it in finally block

                    persist_duration = time.time() - persist_start_time
                    self.logger.info(
                        f"Atomically persisted {rows_inserted} new snapshots "
                        f"(of {len(df)} total) to {database_path} in {persist_duration:.2f}s"
                    )

                except Exception as e:
                    conn.rollback()
                    raise TheOddsAPIError(f"Failed to persist snapshots: {e}")

        except Exception as e:
            self.logger.error(f"Atomic persist failed: {e}")
            raise
        finally:
            # Clean up temp database if it still exists
            if temp_db and temp_db.exists():
                try:
                    temp_db.unlink()
                except Exception:
                    pass  # Best effort cleanup

    def _initialize_database_schema(self, database_path: Path) -> None:
        """Initialize database schema if creating a new database."""
        schema_path = Path(__file__).parent.parent.parent / "db" / "schema.sql"

        with sqlite3.connect(database_path) as conn:
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            else:
                # Fallback minimal schema
                conn.executescript("""
                    PRAGMA journal_mode=WAL;
                    CREATE TABLE IF NOT EXISTS odds_snapshots (
                        snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fetched_at TEXT,
                        sport_key TEXT,
                        event_id TEXT,
                        market_key TEXT,
                        bookmaker_key TEXT,
                        line FLOAT,
                        price INT,
                        outcome TEXT,
                        points FLOAT,
                        iso_time TEXT,
                        odds_raw_json TEXT,
                        UNIQUE (fetched_at, event_id, market_key, bookmaker_key, outcome, points)
                    );
                """)

    def get_key_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the API key pool."""
        available_keys = sum(1 for info in self.key_pool.values() if info.is_available)
        total_keys = len(self.key_pool)

        return {
            "total_keys": total_keys,
            "available_keys": available_keys,
            "exhausted_keys": total_keys - available_keys,
            "pool_exhausted_at": self.pool_exhausted_at.isoformat() if self.pool_exhausted_at else None,
            "last_successful_fetch": self.last_successful_fetch.isoformat() if self.last_successful_fetch else None,
            "consecutive_pool_failures": self.consecutive_pool_failures,
            "keys": {
                f"{info.key[:8]}**": {
                    "available": info.is_available,
                    "requests_used": info.requests_used,
                    "requests_remaining": info.requests_remaining,
                    "consecutive_failures": info.consecutive_failures,
                    "is_rate_limited": info.is_rate_limited,
                    "last_used_at": info.last_used_at.isoformat() if info.last_used_at else None,
                }
                for info in self.key_pool.values()
            }
        }


def normalize_odds_response(payload: Iterable[Dict[str, Any]], *, fetched_at: datetime) -> pd.DataFrame:
    """Normalize The Odds API response into a tidy DataFrame with enhanced validation.

    Args:
        payload: Raw API response data
        fetched_at: UTC timestamp when data was fetched

    Returns:
        pd.DataFrame: Normalized odds data with comprehensive metadata
    """
    rows: List[Dict[str, Any]] = []
    fetched_at_iso = fetched_at.astimezone(timezone.utc).isoformat()

    logger = logging.getLogger(f"{__name__}.normalize_odds_response")

    events_processed = 0
    odds_rows_created = 0

    for event in payload or []:
        try:
            sport_key = event.get("sport_key")
            event_id = event.get("id") or event.get("event_id")

            # Validate critical event fields
            if not event_id:
                logger.warning(f"Skipping event with missing ID: {event}")
                continue

            events_processed += 1

            for bookmaker in event.get("bookmakers", []):
                bookmaker_key = bookmaker.get("key")
                if not bookmaker_key:
                    logger.warning(f"Skipping bookmaker with missing key in event {event_id}")
                    continue

                last_update = bookmaker.get("last_update")

                for market in bookmaker.get("markets", []):
                    market_key = market.get("key")
                    if not market_key:
                        logger.warning(f"Skipping market with missing key for {bookmaker_key} in event {event_id}")
                        continue

                    market_last_update = market.get("last_update") or last_update

                    for outcome in market.get("outcomes", []):
                        try:
                            # Validate outcome has required fields
                            if not outcome.get("name") or outcome.get("price") is None:
                                logger.debug(f"Skipping incomplete outcome in {event_id}/{market_key}/{bookmaker_key}")
                                continue

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
                                        },
                                        separators=(',', ':')  # Compact JSON
                                    ),
                                }
                            )
                            odds_rows_created += 1

                        except Exception as e:
                            logger.error(f"Error processing outcome in {event_id}/{market_key}/{bookmaker_key}: {e}")
                            continue

        except Exception as e:
            logger.error(f"Error processing event {event.get('id', 'unknown')}: {e}")
            continue

    df = pd.DataFrame(rows)

    logger.info(
        f"Processed {events_processed} events, created {odds_rows_created} odds rows"
    )

    if df.empty:
        logger.warning("No valid odds data found in API response")
        # Return empty DataFrame with expected schema
        expected_cols = [
            "fetched_at", "sport_key", "event_id", "commence_time", "home_team",
            "away_team", "bookmaker_key", "market_key", "outcome", "points",
            "price", "iso_time", "line", "odds_raw_json"
        ]
        return pd.DataFrame(columns=expected_cols)

    # Normalize numeric columns with error handling
    numeric_cols = ["price", "points", "line"]
    for col in numeric_cols:
        if col in df.columns:
            original_count = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            coerced_count = df[col].notna().sum()

            if coerced_count < original_count:
                logger.warning(
                    f"Column '{col}': {original_count - coerced_count} values could not be converted to numeric"
                )

    # Ensure all expected columns exist
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

    # Validate critical fields
    missing_event_ids = df["event_id"].isna().sum()
    missing_prices = df["price"].isna().sum()
    missing_bookmakers = df["bookmaker_key"].isna().sum()

    if missing_event_ids > 0:
        logger.error(f"{missing_event_ids} rows missing event_id")
    if missing_prices > 0:
        logger.warning(f"{missing_prices} rows missing price data")
    if missing_bookmakers > 0:
        logger.error(f"{missing_bookmakers} rows missing bookmaker_key")

    # Apply data validation if available
    if VALIDATION_AVAILABLE:
        try:
            df = validate_odds_snapshots(df)
            logger.info("✅ Data validation passed")
        except Exception as e:
            logger.warning(f"⚠️  Data validation failed: {e}")
            # Continue with unvalidated data for now - could be made stricter in production
    else:
        logger.debug("Data validation not available (pandera not installed)")

    return df[expected_cols]


def compute_current_best_lines(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the best available price per event/market/outcome with enhanced validation.

    Args:
        df: DataFrame with odds snapshots

    Returns:
        pd.DataFrame: Best lines with metadata
    """
    logger = logging.getLogger(f"{__name__}.compute_current_best_lines")

    if df.empty:
        logger.info("No data provided for best lines computation")
        return pd.DataFrame(
            columns=[
                "event_id", "market_key", "outcome", "best_book",
                "best_price", "best_points", "fetched_at"
            ]
        )

    computation_start = time.time()
    df = df.copy()

    # Validate and clean price data
    original_rows = len(df)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price", "event_id", "market_key", "outcome", "bookmaker_key"])

    valid_rows = len(df)
    if valid_rows < original_rows:
        logger.warning(
            f"Filtered out {original_rows - valid_rows} rows with missing critical data"
        )

    if df.empty:
        logger.warning("No valid data remaining after filtering")
        return pd.DataFrame(
            columns=[
                "event_id", "market_key", "outcome", "best_book",
                "best_price", "best_points", "fetched_at"
            ]
        )

    # For American odds, "best" means highest value (less negative, more positive)
    # Group by market keys and find the maximum price for each outcome
    try:
        idx = df.groupby(["event_id", "market_key", "outcome"])["price"].idxmax()
        best = df.loc[idx]

        # Rename columns to match schema
        result = best[[
            "event_id",
            "market_key",
            "outcome",
            "bookmaker_key",
            "price",
            "points",
            "fetched_at",
        ]].rename(columns={
            "bookmaker_key": "best_book",
            "price": "best_price",
            "points": "best_points"
        })

        computation_duration = time.time() - computation_start
        unique_markets = result.groupby(["event_id", "market_key"]).size().sum()

        logger.info(
            f"Computed {len(result)} best lines across {unique_markets} unique markets "
            f"in {computation_duration:.3f}s"
        )

        # Apply data validation if available
        if VALIDATION_AVAILABLE:
            try:
                result = validate_current_best_lines(result)
                logger.info("✅ Best lines validation passed")
            except Exception as e:
                logger.warning(f"⚠️  Best lines validation failed: {e}")
                # Continue with unvalidated data for now

        return result

    except Exception as e:
        logger.error(f"Error computing best lines: {e}")
        raise


def update_current_best_lines(database_path: Path) -> pd.DataFrame:
    """Load odds snapshots and atomically update the current_best_lines table.

    Uses atomic operations to ensure consistency during updates.
    """
    logger = logging.getLogger(f"{__name__}.update_current_best_lines")
    update_start_time = time.time()

    try:
        with sqlite3.connect(database_path, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL")

            # Load all snapshots
            df = pd.read_sql_query("SELECT * FROM odds_snapshots ORDER BY fetched_at DESC", conn)

            if df.empty:
                logger.info("No odds snapshots found, skipping best lines update")
                return pd.DataFrame()

            # Compute best lines
            best = compute_current_best_lines(df)

            if best.empty:
                logger.warning("No valid best lines computed from snapshots")
                return best

            # Atomic update of best lines table
            conn.execute("BEGIN IMMEDIATE")
            try:
                # Clear existing data
                conn.execute("DELETE FROM current_best_lines")

                # Insert new best lines
                cursor = conn.cursor()
                rows_inserted = 0
                for row in best.to_dict("records"):
                    cursor.execute(
                        """
                        INSERT INTO current_best_lines (
                            event_id, market_key, outcome, best_book, best_price, best_points, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["event_id"],
                            row["market_key"],
                            row["outcome"],
                            row["best_book"],
                            int(row["best_price"]) if pd.notna(row["best_price"]) else None,
                            row.get("best_points"),
                            row.get("fetched_at"),
                        ),
                    )
                    rows_inserted += cursor.rowcount

                conn.commit()

                update_duration = time.time() - update_start_time
                logger.info(
                    f"Atomically updated {rows_inserted} best lines from {len(df)} snapshots "
                    f"in {update_duration:.2f}s"
                )

                return best

            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to update best lines, rolled back: {e}")
                raise

    except Exception as e:
        logger.error(f"Database error during best lines update: {e}")
        raise


def create_production_client() -> TheOddsAPIClient:
    """Factory function to create a production-configured Odds API client."""
    try:
        config = TheOddsAPIConfig.from_env()
        client = TheOddsAPIClient(config)

        # Log initial configuration
        logging.info(
            f"Initialized Odds API client with {len(config.api_keys)} keys for {config.sport_key}"
        )

        return client
    except Exception as e:
        logging.error(f"Failed to create Odds API client: {e}")
        raise
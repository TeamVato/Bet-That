from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
import redis.asyncio as redis

from app.core.config import get_cache_prefix, get_settings  # type: ignore
from app.models.odds import GameOdds, MarketLine  # type: ignore

logger = logging.getLogger(__name__)


class OddsAPIError(Exception):
    """Raised when the Odds API cannot satisfy a request."""


class DailyLimitReached(OddsAPIError):
    """Raised when the daily request limit has been exceeded."""


class OddsAPIManager:
    """Manages Odds API requests with caching, rate limiting, and key rotation."""

    SPORTS_KEY = "americanfootball_nfl"
    TARGET_BOOKMAKERS = ["draftkings", "fanduel", "betmgm"]
    TARGET_MARKETS = ["spreads", "totals"]

    def __init__(self, redis_client: Optional[redis.Redis] = None) -> None:
        self.settings = get_settings()
        self.redis = redis_client or redis.from_url(self.settings.redis_url, decode_responses=True)
        self.cache_ttl = max(1800, self.settings.cache_ttl_seconds)
        self.daily_limit = max(1, self.settings.daily_request_limit)
        self.cache_key_odds = get_cache_prefix("odds", self.SPORTS_KEY, "current_week")
        self.usage_key = get_cache_prefix("usage", "daily_count")
        self.key_index_key = get_cache_prefix("usage", "current_key_index")
        self._keys = self.settings.all_odds_keys
        self._lock = asyncio.Lock()

    async def get_cached_week_odds(self) -> List[Dict[str, Any]]:
        cached = await self.redis.get(self.cache_key_odds)
        if cached:
            try:
                payload = json.loads(cached)
                logger.debug("Serving cached NFL odds payload with %d items.", len(payload))
                return payload
            except json.JSONDecodeError:
                logger.warning("Cached odds payload was invalid JSON; ignoring cache entry.")
        return []

    async def fetch_current_week_odds(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch NFL odds for the current week, respecting cache and rate limits."""

        if not force_refresh:
            cached = await self.get_cached_week_odds()
            if cached:
                return cached

        if await self._requests_today() >= self.daily_limit:
            raise DailyLimitReached("Daily request cap reached; try again after midnight UTC.")

        raw_events = await self._fetch_with_key_rotation()
        processed = self._process_events(raw_events)

        await self.redis.set(
            self.cache_key_odds, json.dumps(processed, default=str), ex=self.cache_ttl
        )
        return processed

    async def get_usage_stats(self) -> Dict[str, Any]:
        requests_made = await self._requests_today()
        per_key_counts: Dict[str, int] = {}
        for key in self._keys:
            usage = await self.redis.get(self._key_usage_key(key))
            per_key_counts[key[-6:]] = int(usage) if usage else 0

        blocked_status: Dict[str, str] = {}
        for key in self._keys:
            blocked_until = await self.redis.get(self._key_blocked_key(key))
            if blocked_until:
                try:
                    timestamp = float(blocked_until)
                except ValueError:
                    continue
                if timestamp > time.time():
                    blocked_status[key[-6:]] = datetime.fromtimestamp(
                        timestamp, tz=timezone.utc
                    ).isoformat()

        return {
            "daily_limit": self.daily_limit,
            "requests_made": requests_made,
            "requests_remaining": max(0, self.daily_limit - requests_made),
            "keys_configured": len(self._keys),
            "key_usage_snapshot": per_key_counts,
            "blocked_keys": blocked_status,
        }

    async def force_refresh(self) -> List[Dict[str, Any]]:
        return await self.fetch_current_week_odds(force_refresh=True)

    async def _fetch_with_key_rotation(self) -> List[Dict[str, Any]]:
        if not self._keys:
            logger.warning("No Odds API keys configured; returning demo payload.")
            return self._demo_payload()

        last_index_raw = await self.redis.get(self.key_index_key)
        start_index = int(last_index_raw) if last_index_raw else 0

        for offset in range(len(self._keys)):
            index = (start_index + offset) % len(self._keys)
            api_key = self._keys[index]

            if await self._is_key_blocked(api_key):
                continue

            await self._register_attempt(api_key)

            try:
                events = await self._request_odds(api_key)
                await self.redis.set(self.key_index_key, str((index + 1) % len(self._keys)))
                return events
            except OddsAPIError as exc:
                await self._handle_key_failure(api_key, exc)
                logger.error("Key ending with %s failed due to %s", api_key[-6:], exc)
                continue

        logger.error("All Odds API keys failed; falling back to demo payload.")
        return self._demo_payload()

    async def _requests_today(self) -> int:
        value = await self.redis.get(self.usage_key)
        return int(value) if value else 0

    async def _register_attempt(self, api_key: str) -> None:
        async with self._lock:
            pipeline = self.redis.pipeline()
            pipeline.incr(self.usage_key)
            pipeline.expireat(self.usage_key, self._midnight_epoch())
            per_key_key = self._key_usage_key(api_key)
            pipeline.incr(per_key_key)
            pipeline.expireat(per_key_key, self._midnight_epoch())
            await pipeline.execute()

    async def _request_odds(self, api_key: str) -> List[Dict[str, Any]]:
        params = {
            "apiKey": api_key,
            "regions": "us",
            "markets": ",".join(self.TARGET_MARKETS),
            "oddsFormat": "american",
            "bookmakers": ",".join(self.TARGET_BOOKMAKERS),
            "dateFormat": "iso",
        }

        timeout = httpx.Timeout(10.0, read=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(self.settings.odds_api_base_url, params=params)

        if response.status_code == 200:
            try:
                events = response.json()
                if not isinstance(events, list):
                    raise OddsAPIError("Unexpected Odds API payload format")
                return events
            except (ValueError, json.JSONDecodeError) as exc:
                raise OddsAPIError(f"Failed to decode Odds API response: {exc}") from exc

        if response.status_code in {401, 403}:
            raise OddsAPIError("Key unauthorized or exhausted")
        if response.status_code == 429:
            raise OddsAPIError("Rate limit exceeded for key")
        if response.status_code >= 500:
            raise OddsAPIError(f"Odds API server error ({response.status_code})")

        raise OddsAPIError(
            f"Odds API request failed with status {response.status_code}: {response.text[:200]}"
        )

    async def _handle_key_failure(self, api_key: str, exc: OddsAPIError) -> None:
        block_duration = 0
        message = str(exc).lower()

        if "unauthorized" in message or "exhausted" in message:
            block_duration = 24 * 3600
        elif "rate limit" in message:
            block_duration = 3600
        elif "server error" in message:
            block_duration = 300
        else:
            block_duration = 600

        if block_duration > 0:
            await self.redis.set(
                self._key_blocked_key(api_key),
                str(time.time() + block_duration),
                ex=block_duration,
            )

    async def _is_key_blocked(self, api_key: str) -> bool:
        blocked_until = await self.redis.get(self._key_blocked_key(api_key))
        if blocked_until:
            try:
                timestamp = float(blocked_until)
            except ValueError:
                return False
            if timestamp > time.time():
                logger.debug("Key ending with %s is blocked until %s", api_key[-6:], timestamp)
                return True
        return False

    def _process_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        week_end = now + timedelta(days=7)
        processed: List[Dict[str, Any]] = []

        for event in events:
            commence_time_raw = event.get("commence_time")
            if not commence_time_raw:
                continue
            try:
                commence_time = datetime.fromisoformat(commence_time_raw.replace("Z", "+00:00"))
            except Exception:
                logger.debug("Skipping event with invalid commence_time: %s", commence_time_raw)
                continue

            if commence_time < now - timedelta(hours=2) or commence_time > week_end:
                continue

            bookmakers = event.get("bookmakers", [])
            filtered_bookmakers = [b for b in bookmakers if b.get("key") in self.TARGET_BOOKMAKERS]
            if not filtered_bookmakers:
                continue

            best_spreads = self._best_lines(filtered_bookmakers, market_key="spreads")
            best_totals = self._best_lines(filtered_bookmakers, market_key="totals")

            processed.append(
                GameOdds(
                    id=event.get("id", ""),
                    commence_time=commence_time,
                    home_team=event.get("home_team", ""),
                    away_team=event.get("away_team", ""),
                    best_spreads=best_spreads,
                    best_totals=best_totals,
                    last_updated=now,
                ).dict(by_alias=True)
            )

        return processed

    def _best_lines(
        self, bookmakers: List[Dict[str, Any]], market_key: str
    ) -> Dict[str, Dict[str, Any]]:
        outcomes_by_type: Dict[str, MarketLine] = {}

        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market.get("key") != market_key:
                    continue
                for outcome in market.get("outcomes", []):
                    name = outcome.get("name")
                    if not name:
                        continue
                    price = outcome.get("price")
                    point = outcome.get("point")
                    if price is None:
                        continue
                    line = MarketLine(
                        bookmaker=bookmaker.get("title", bookmaker.get("key", "")),
                        price=float(price),
                        point=float(point) if point is not None else None,
                    )
                    key = name.lower()
                    existing = outcomes_by_type.get(key)
                    if existing is None or self._is_better_price(line.price, existing.price):
                        outcomes_by_type[key] = line

        return {name: line.dict() for name, line in outcomes_by_type.items()}

    @staticmethod
    def _is_better_price(candidate: float, current: float) -> bool:
        if candidate >= 0 and current >= 0:
            return candidate > current
        if candidate < 0 and current < 0:
            return candidate > current
        return candidate > current

    def _demo_payload(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        sample_game = GameOdds(
            id="demo-game-001",
            commence_time=now + timedelta(days=2),
            home_team="Demo Home",
            away_team="Demo Away",
            best_spreads={
                "home": MarketLine(bookmaker="DemoBook", price=-110.0, point=-3.5).dict(),
                "away": MarketLine(bookmaker="DemoBook", price=-105.0, point=3.5).dict(),
            },
            best_totals={
                "over": MarketLine(bookmaker="DemoBook", price=-108.0, point=45.5).dict(),
                "under": MarketLine(bookmaker="DemoBook", price=-112.0, point=45.5).dict(),
            },
            last_updated=now,
        )
        return [sample_game.dict(by_alias=True)]

    def _key_usage_key(self, api_key: str) -> str:
        return get_cache_prefix("usage", "key", api_key[-6:])

    def _key_blocked_key(self, api_key: str) -> str:
        return get_cache_prefix("usage", "key_blocked", api_key[-6:])

    @staticmethod
    def _midnight_epoch() -> int:
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int(tomorrow.timestamp())


async def get_odds_manager() -> OddsAPIManager:
    return OddsAPIManager()

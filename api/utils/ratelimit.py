"""Token bucket rate limiting implementation"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Tuple


class TokenBucket:
    """Token bucket rate limiter for API endpoints"""

    def __init__(self, capacity: int, refill_rate: float, last_update: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_update = last_update

    def is_allowed(self) -> Tuple[bool, TokenBucket]:
        now = time.time()
        time_passed = now - self.last_update

        # Add tokens based on time passed
        tokens_to_add = time_passed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now

        # Check if request is allowed
        if self.tokens >= 1:
            self.tokens -= 1
            return True, self
        else:
            return False, self


class RateLimiter:
    """Rate limiter with token bucket per client/route"""

    def __init__(self, requests_per_minute: int, window_seconds: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.refill_rate = requests_per_minute / window_seconds
        self.buckets: Dict[str, TokenBucket] = {}
        self.last_cleanup = time.time()

    def is_allowed(self, client_id: str, route_key: str) -> bool:
        """Check if request is allowed for client on specific route"""
        key = f"{client_id}:{route_key}"
        now = time.time()

        # Cleanup old buckets periodically
        if now - self.last_cleanup > 3600:  # Clean every hour
            self._cleanup()
            self.last_cleanup = now

        # Get or create bucket for this client/route
        if key in self.buckets:
            bucket = self.buckets[key]
        else:
            bucket = TokenBucket(
                capacity=self.requests_per_minute, refill_rate=self.refill_rate, last_update=now
            )

        # Check if request is allowed
        allowed, updated_bucket = bucket.is_allowed()
        self.buckets[key] = updated_bucket

        return allowed

    def _cleanup(self):
        """Remove old/expired buckets to prevent memory leaks"""
        now = time.time()
        cutoff_time = now - (self.window_seconds * 2)

        keys_to_remove = []
        for key, bucket in self.buckets.items():
            if bucket.last_update < cutoff_time:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.buckets[key]

"""Rate limiter service for AI Engine using Redis with memory fallback."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis import Redis

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    current_count: int
    limit: int
    retry_after_ms: int | None = None


class MemoryRateLimiter:
    """In-memory rate limiter fallback when Redis is unavailable."""

    def __init__(self, limit_per_min: int) -> None:
        self.limit_per_min = limit_per_min
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check_rate_limit(self, user_id: str) -> RateLimitResult:
        """Check if user has exceeded rate limit."""
        with self._lock:
            now = time.time()
            window_start = now - 60.0

            timestamps = self._requests[user_id]
            timestamps[:] = [ts for ts in timestamps if ts > window_start]

            current_count = len(timestamps)
            if current_count >= self.limit_per_min:
                oldest = min(timestamps) if timestamps else now
                retry_after_ms = int((oldest + 60.0 - now) * 1000)
                return RateLimitResult(
                    allowed=False,
                    current_count=current_count,
                    limit=self.limit_per_min,
                    retry_after_ms=max(retry_after_ms, 1000),
                )

            timestamps.append(now)
            return RateLimitResult(
                allowed=True,
                current_count=current_count + 1,
                limit=self.limit_per_min,
            )

    def reset(self, user_id: str) -> None:
        """Reset rate limit for a user (for testing)."""
        with self._lock:
            self._requests.pop(user_id, None)


class RedisRateLimiter:
    """Redis-based rate limiter using sliding window."""

    KEY_PREFIX = "ai_ratelimit"

    def __init__(self, redis_client: "Redis[bytes]", limit_per_min: int) -> None:
        self.redis = redis_client
        self.limit_per_min = limit_per_min
        self.window_seconds = 60

    def check_rate_limit(self, user_id: str) -> RateLimitResult:
        """Check if user has exceeded rate limit using sliding window."""
        key = f"{self.KEY_PREFIX}:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.execute()

        current_count = self.redis.zcard(key)

        if current_count >= self.limit_per_min:
            oldest_scores = self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_scores:
                oldest_ts = oldest_scores[0][1]
                retry_after_ms = int((oldest_ts + self.window_seconds - now) * 1000)
            else:
                retry_after_ms = 60000
            return RateLimitResult(
                allowed=False,
                current_count=current_count,
                limit=self.limit_per_min,
                retry_after_ms=max(retry_after_ms, 1000),
            )

        pipe = self.redis.pipeline()
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window_seconds + 10)
        pipe.execute()

        return RateLimitResult(
            allowed=True,
            current_count=current_count + 1,
            limit=self.limit_per_min,
        )

    def reset(self, user_id: str) -> None:
        """Reset rate limit for a user (for testing)."""
        key = f"{self.KEY_PREFIX}:{user_id}"
        self.redis.delete(key)


class RateLimiter:
    """
    Rate limiter with Redis backend and memory fallback.

    Uses Redis sorted set for distributed rate limiting.
    Falls back to in-memory rate limiting if Redis is unavailable.
    """

    _instance: "RateLimiter | None" = None
    _lock = Lock()

    def __init__(
        self,
        redis_url: str | None,
        limit_per_min: int,
        enabled: bool = True,
    ) -> None:
        self.limit_per_min = limit_per_min
        self.enabled = enabled
        self._redis_client: "Redis[bytes] | None" = None
        self._redis_limiter: RedisRateLimiter | None = None
        self._memory_limiter = MemoryRateLimiter(limit_per_min)
        self._use_memory = True

        if redis_url and enabled:
            self._init_redis(redis_url)

    def _init_redis(self, redis_url: str) -> None:
        """Initialize Redis connection."""
        try:
            import redis

            self._redis_client = redis.from_url(redis_url, decode_responses=False)
            self._redis_client.ping()
            self._redis_limiter = RedisRateLimiter(self._redis_client, self.limit_per_min)
            self._use_memory = False
            logger.info("rate_limiter_redis_connected url=%s", redis_url.split("@")[-1])
        except Exception as e:
            logger.warning(
                "rate_limiter_redis_failed error=%s fallback=memory",
                str(e),
            )
            self._redis_client = None
            self._redis_limiter = None
            self._use_memory = True

    def check_rate_limit(self, user_id: str | int) -> RateLimitResult:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Returns:
            RateLimitResult with allowed status and metadata
        """
        if not self.enabled:
            return RateLimitResult(
                allowed=True,
                current_count=0,
                limit=self.limit_per_min,
            )

        user_key = str(user_id)

        if self._use_memory or self._redis_limiter is None:
            return self._memory_limiter.check_rate_limit(user_key)

        try:
            return self._redis_limiter.check_rate_limit(user_key)
        except Exception as e:
            logger.warning(
                "rate_limiter_redis_error user_id=%s error=%s fallback=memory",
                user_key,
                str(e),
            )
            return self._memory_limiter.check_rate_limit(user_key)

    def reset(self, user_id: str | int) -> None:
        """Reset rate limit for a user (for testing)."""
        user_key = str(user_id)
        self._memory_limiter.reset(user_key)
        if self._redis_limiter and not self._use_memory:
            try:
                self._redis_limiter.reset(user_key)
            except Exception:
                pass

    @classmethod
    def get_instance(cls) -> "RateLimiter":
        """Get singleton rate limiter instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    from app.ai_engine.config import ai_engine_settings

                    cls._instance = cls(
                        redis_url=ai_engine_settings.redis_url,
                        limit_per_min=ai_engine_settings.rate_limit_per_min,
                        enabled=ai_engine_settings.rate_limit_enabled,
                    )
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                if cls._instance._redis_client is not None:
                    try:
                        cls._instance._redis_client.close()
                    except Exception:
                        pass
            cls._instance = None

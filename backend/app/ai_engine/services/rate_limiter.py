"""Rate limiter service for AI Engine using Redis with memory fallback."""

from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis import Redis

logger = logging.getLogger(__name__)

# Atomic sliding window rate limit Lua script.
# Cleans expired entries, checks count, and conditionally adds a new entry — all atomically.
# Args: KEYS[1]=key, ARGV[1]=now(float), ARGV[2]=window_seconds, ARGV[3]=limit, ARGV[4]=unique_member
# Returns: {0|1 (blocked|allowed), current_count, retry_after_ms}
_SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]
local window_start = now - window

redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
local count = tonumber(redis.call('ZCARD', key))

if count >= limit then
    local oldest = redis.call('ZRANGEBYSCORE', key, '-inf', '+inf', 'WITHSCORES', 'LIMIT', 0, 1)
    local retry_ms = 60000
    if oldest and #oldest >= 2 then
        local oldest_ts = tonumber(oldest[2])
        if oldest_ts then
            local diff = oldest_ts + window - now
            retry_ms = math.max(math.floor(diff * 1000), 1000)
        end
    end
    return {0, count, retry_ms}
end

redis.call('ZADD', key, now, member)
redis.call('EXPIRE', key, math.floor(window) + 10)
return {1, count + 1, 0}
"""


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
        """Check if user has exceeded rate limit using atomic sliding window Lua script."""
        key = f"{self.KEY_PREFIX}:{user_id}"
        now = time.time()
        member = uuid.uuid4().hex

        result = self.redis.eval(
            _SLIDING_WINDOW_SCRIPT,
            1,
            key,
            str(now),
            str(self.window_seconds),
            str(self.limit_per_min),
            member,
        )

        allowed = bool(result[0])
        current_count = int(result[1])
        return RateLimitResult(
            allowed=allowed,
            current_count=current_count,
            limit=self.limit_per_min,
            retry_after_ms=int(result[2]) if not allowed else None,
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

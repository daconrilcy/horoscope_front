"""Cache service for AI Engine responses using Redis."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from redis import Redis

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached AI response."""

    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str


def compute_cache_key(use_case: str, input_data: dict[str, Any], context: dict[str, Any]) -> str:
    """
    Compute a stable cache key from use_case, input and context.

    Args:
        use_case: The use case identifier
        input_data: Input parameters (question, tone, etc.)
        context: Context data (natal_chart_summary, birth_data, etc.)

    Returns:
        A stable hash string for use as cache key
    """
    payload = {
        "use_case": use_case,
        "input": input_data,
        "context": context,
    }
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class MemoryCacheService:
    """In-memory cache fallback when Redis is unavailable."""

    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[CachedResponse, float]] = {}
        self._lock = Lock()

    def get(self, cache_key: str) -> CachedResponse | None:
        """Get cached response if not expired."""
        with self._lock:
            if cache_key not in self._cache:
                return None
            response, timestamp = self._cache[cache_key]
            if time.time() - timestamp > self.ttl_seconds:
                del self._cache[cache_key]
                return None
            return response

    def set(self, cache_key: str, response: CachedResponse) -> None:
        """Store response in cache."""
        with self._lock:
            self._cache[cache_key] = (response, time.time())

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()


class RedisCacheService:
    """Redis-based cache service."""

    KEY_PREFIX = "ai_cache"

    def __init__(self, redis_client: "Redis[bytes]", ttl_seconds: int) -> None:
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds

    def get(self, cache_key: str) -> CachedResponse | None:
        """Get cached response from Redis."""
        key = f"{self.KEY_PREFIX}:{cache_key}"
        try:
            data = self.redis.get(key)
            if data is None:
                return None
            parsed = json.loads(data)
            return CachedResponse(
                text=parsed["text"],
                input_tokens=parsed["input_tokens"],
                output_tokens=parsed["output_tokens"],
                total_tokens=parsed["total_tokens"],
                model=parsed["model"],
            )
        except Exception as e:
            logger.warning("cache_get_error key=%s error=%s", cache_key, str(e))
            return None

    def set(self, cache_key: str, response: CachedResponse) -> None:
        """Store response in Redis with TTL."""
        key = f"{self.KEY_PREFIX}:{cache_key}"
        try:
            data = json.dumps(
                {
                    "text": response.text,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "total_tokens": response.total_tokens,
                    "model": response.model,
                }
            )
            self.redis.setex(key, self.ttl_seconds, data)
        except Exception as e:
            logger.warning("cache_set_error key=%s error=%s", cache_key, str(e))


class CacheService:
    """
    Cache service with Redis backend and memory fallback.

    Used to cache AI engine responses for identical requests.
    NOT used for streaming chat (non-deterministic).
    """

    _instance: "CacheService | None" = None
    _lock = Lock()

    def __init__(
        self,
        redis_url: str | None,
        ttl_seconds: int,
        enabled: bool = False,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self._redis_client: "Redis[bytes] | None" = None
        self._redis_cache: RedisCacheService | None = None
        self._memory_cache = MemoryCacheService(ttl_seconds)
        self._use_memory = True

        if redis_url and enabled:
            self._init_redis(redis_url)

    def _init_redis(self, redis_url: str) -> None:
        """Initialize Redis connection."""
        try:
            import redis

            self._redis_client = redis.from_url(redis_url, decode_responses=False)
            self._redis_client.ping()
            self._redis_cache = RedisCacheService(self._redis_client, self.ttl_seconds)
            self._use_memory = False
            logger.info("cache_service_redis_connected url=%s", redis_url.split("@")[-1])
        except Exception as e:
            logger.warning(
                "cache_service_redis_failed error=%s fallback=memory",
                str(e),
            )
            self._redis_client = None
            self._redis_cache = None
            self._use_memory = True

    def get_cached_response(
        self,
        use_case: str,
        input_data: dict[str, Any],
        context: dict[str, Any],
    ) -> CachedResponse | None:
        """
        Get cached response for a request.

        Args:
            use_case: The use case identifier
            input_data: Input parameters dict
            context: Context dict

        Returns:
            CachedResponse if found and not expired, None otherwise
        """
        if not self.enabled:
            return None

        cache_key = compute_cache_key(use_case, input_data, context)

        if self._use_memory or self._redis_cache is None:
            result = self._memory_cache.get(cache_key)
        else:
            try:
                result = self._redis_cache.get(cache_key)
            except Exception as e:
                logger.warning("cache_get_redis_error error=%s fallback=memory", str(e))
                result = self._memory_cache.get(cache_key)

        if result:
            logger.info("cache_hit use_case=%s", use_case)
        return result

    def cache_response(
        self,
        use_case: str,
        input_data: dict[str, Any],
        context: dict[str, Any],
        response: CachedResponse,
    ) -> None:
        """
        Cache a response for a request.

        Args:
            use_case: The use case identifier
            input_data: Input parameters dict
            context: Context dict
            response: The response to cache
        """
        if not self.enabled:
            return

        cache_key = compute_cache_key(use_case, input_data, context)

        if self._use_memory or self._redis_cache is None:
            self._memory_cache.set(cache_key, response)
        else:
            try:
                self._redis_cache.set(cache_key, response)
            except Exception as e:
                logger.warning("cache_set_redis_error error=%s fallback=memory", str(e))
                self._memory_cache.set(cache_key, response)

        logger.info("cache_stored use_case=%s ttl=%d", use_case, self.ttl_seconds)

    def clear(self) -> None:
        """Clear memory cache (for testing)."""
        self._memory_cache.clear()

    @classmethod
    def get_instance(cls) -> "CacheService":
        """Get singleton cache service instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    from app.ai_engine.config import ai_engine_settings

                    cls._instance = cls(
                        redis_url=ai_engine_settings.redis_url,
                        ttl_seconds=ai_engine_settings.cache_ttl_seconds,
                        enabled=ai_engine_settings.cache_enabled,
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

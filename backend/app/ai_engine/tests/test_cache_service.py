"""Tests for the cache service."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from app.ai_engine.services.cache_service import (
    CachedResponse,
    CacheService,
    MemoryCacheService,
    RedisCacheService,
    compute_cache_key,
)


class TestComputeCacheKey:
    """Tests for cache key computation."""

    def test_same_input_produces_same_key(self) -> None:
        """Identical inputs should produce identical keys."""
        key1 = compute_cache_key(
            "chat",
            {"question": "Hello"},
            {"natal_chart_summary": "Sun in Aries"},
        )
        key2 = compute_cache_key(
            "chat",
            {"question": "Hello"},
            {"natal_chart_summary": "Sun in Aries"},
        )
        assert key1 == key2

    def test_different_input_produces_different_key(self) -> None:
        """Different inputs should produce different keys."""
        key1 = compute_cache_key("chat", {"question": "Hello"}, {})
        key2 = compute_cache_key("chat", {"question": "Goodbye"}, {})
        assert key1 != key2

    def test_different_use_case_produces_different_key(self) -> None:
        """Different use cases should produce different keys."""
        key1 = compute_cache_key("chat", {"question": "Hello"}, {})
        key2 = compute_cache_key("natal_chart_interpretation", {"question": "Hello"}, {})
        assert key1 != key2

    def test_key_order_independent(self) -> None:
        """Dictionary key order should not affect cache key."""
        key1 = compute_cache_key("chat", {"a": "1", "b": "2"}, {})
        key2 = compute_cache_key("chat", {"b": "2", "a": "1"}, {})
        assert key1 == key2


class TestMemoryCacheService:
    """Tests for MemoryCacheService."""

    def test_cache_miss_returns_none(self) -> None:
        """Cache miss should return None."""
        cache = MemoryCacheService(ttl_seconds=3600)
        result = cache.get("nonexistent")
        assert result is None

    def test_cache_hit_returns_response(self) -> None:
        """Cache hit should return stored response."""
        cache = MemoryCacheService(ttl_seconds=3600)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.set("key1", response)
        result = cache.get("key1")
        assert result is not None
        assert result.text == "Hello"
        assert result.model == "gpt-4o-mini"

    def test_cache_expiration(self) -> None:
        """Expired cache entries should return None."""
        cache = MemoryCacheService(ttl_seconds=1)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        base_time = 1000000000.0

        with patch("app.ai_engine.services.cache_service.time") as mock_time:
            mock_time.time.return_value = base_time
            cache.set("key1", response)

            mock_time.time.return_value = base_time + 2
            result = cache.get("key1")
            assert result is None

    def test_clear_removes_all_entries(self) -> None:
        """Clear should remove all cached entries."""
        cache = MemoryCacheService(ttl_seconds=3600)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.set("key1", response)
        cache.set("key2", response)

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestRedisCacheService:
    """Tests for RedisCacheService with mocked Redis."""

    def test_cache_miss_returns_none(self) -> None:
        """Cache miss should return None."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None

        cache = RedisCacheService(mock_redis, ttl_seconds=3600)
        result = cache.get("key1")

        assert result is None
        mock_redis.get.assert_called_once()

    def test_cache_hit_returns_response(self) -> None:
        """Cache hit should return parsed response."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(
            {
                "text": "Hello",
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "model": "gpt-4o-mini",
            }
        ).encode()

        cache = RedisCacheService(mock_redis, ttl_seconds=3600)
        result = cache.get("key1")

        assert result is not None
        assert result.text == "Hello"
        assert result.model == "gpt-4o-mini"

    def test_set_stores_with_ttl(self) -> None:
        """Set should store with TTL."""
        mock_redis = MagicMock()

        cache = RedisCacheService(mock_redis, ttl_seconds=3600)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.set("key1", response)

        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args
        assert args[0][1] == 3600

    def test_get_handles_redis_error(self) -> None:
        """Get should handle Redis errors gracefully."""
        mock_redis = MagicMock()
        mock_redis.get.side_effect = Exception("Connection error")

        cache = RedisCacheService(mock_redis, ttl_seconds=3600)
        result = cache.get("key1")

        assert result is None


class TestCacheService:
    """Tests for CacheService (main class with fallback)."""

    def test_disabled_cache_returns_none(self) -> None:
        """Disabled cache should always return None."""
        cache = CacheService(redis_url=None, ttl_seconds=3600, enabled=False)
        result = cache.get_cached_response("chat", {"question": "Hello"}, {})
        assert result is None

    def test_disabled_cache_does_not_store(self) -> None:
        """Disabled cache should not store responses."""
        cache = CacheService(redis_url=None, ttl_seconds=3600, enabled=False)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.cache_response("chat", {"question": "Hello"}, {}, response)
        result = cache.get_cached_response("chat", {"question": "Hello"}, {})
        assert result is None

    def test_memory_fallback_cache_hit(self) -> None:
        """Memory fallback should work for cache hit."""
        cache = CacheService(redis_url=None, ttl_seconds=3600, enabled=True)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.cache_response("chat", {"question": "Hello"}, {}, response)
        result = cache.get_cached_response("chat", {"question": "Hello"}, {})

        assert result is not None
        assert result.text == "Hello"

    def test_memory_fallback_cache_miss(self) -> None:
        """Memory fallback should return None for cache miss."""
        cache = CacheService(redis_url=None, ttl_seconds=3600, enabled=True)
        result = cache.get_cached_response("chat", {"question": "Hello"}, {})
        assert result is None

    def test_uses_memory_fallback_on_redis_connection_error(self) -> None:
        """Should fallback to memory when Redis connection fails."""
        cache = CacheService(
            redis_url="redis://nonexistent:6379",
            ttl_seconds=3600,
            enabled=True,
        )

        assert cache._use_memory is True

    def test_clear_clears_memory_cache(self) -> None:
        """Clear should clear memory cache."""
        cache = CacheService(redis_url=None, ttl_seconds=3600, enabled=True)
        response = CachedResponse(
            text="Hello",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            model="gpt-4o-mini",
        )
        cache.cache_response("chat", {"question": "Hello"}, {}, response)
        cache.clear()

        result = cache.get_cached_response("chat", {"question": "Hello"}, {})
        assert result is None

    def test_get_instance_singleton(self) -> None:
        """get_instance should return singleton."""
        CacheService.reset_instance()

        with patch("app.ai_engine.config.ai_engine_settings") as mock_settings:
            mock_settings.redis_url = None
            mock_settings.cache_ttl_seconds = 3600
            mock_settings.cache_enabled = True

            instance1 = CacheService.get_instance()
            instance2 = CacheService.get_instance()

            assert instance1 is instance2

        CacheService.reset_instance()

    def test_reset_instance(self) -> None:
        """reset_instance should clear singleton."""
        CacheService.reset_instance()

        with patch("app.ai_engine.config.ai_engine_settings") as mock_settings:
            mock_settings.redis_url = None
            mock_settings.cache_ttl_seconds = 3600
            mock_settings.cache_enabled = True

            instance1 = CacheService.get_instance()
            CacheService.reset_instance()
            instance2 = CacheService.get_instance()

            assert instance1 is not instance2

        CacheService.reset_instance()


class TestCachedResponse:
    """Tests for CachedResponse dataclass."""

    def test_create_cached_response(self) -> None:
        """Test CachedResponse creation."""
        response = CachedResponse(
            text="Hello world",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            model="gpt-4o-mini",
        )

        assert response.text == "Hello world"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.total_tokens == 150
        assert response.model == "gpt-4o-mini"

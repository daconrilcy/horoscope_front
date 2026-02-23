"""Tests for the rate limiter service."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

from app.ai_engine.services.rate_limiter import (
    MemoryRateLimiter,
    RateLimiter,
    RateLimitResult,
    RedisRateLimiter,
)


class TestMemoryRateLimiter:
    """Tests for MemoryRateLimiter."""

    def test_allows_requests_under_limit(self) -> None:
        """Requests under limit should be allowed."""
        limiter = MemoryRateLimiter(limit_per_min=5)

        for i in range(5):
            result = limiter.check_rate_limit("user1")
            assert result.allowed is True
            assert result.current_count == i + 1
            assert result.limit == 5

    def test_blocks_requests_at_limit(self) -> None:
        """Requests at limit should be blocked."""
        limiter = MemoryRateLimiter(limit_per_min=3)

        for _ in range(3):
            limiter.check_rate_limit("user1")

        result = limiter.check_rate_limit("user1")
        assert result.allowed is False
        assert result.current_count == 3
        assert result.retry_after_ms is not None
        assert result.retry_after_ms > 0

    def test_reset_allows_new_requests(self) -> None:
        """Reset should clear rate limit for user."""
        limiter = MemoryRateLimiter(limit_per_min=2)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")
        result = limiter.check_rate_limit("user1")
        assert result.allowed is False

        limiter.reset("user1")
        result = limiter.check_rate_limit("user1")
        assert result.allowed is True

    def test_different_users_have_separate_limits(self) -> None:
        """Each user should have their own rate limit."""
        limiter = MemoryRateLimiter(limit_per_min=2)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")
        result1 = limiter.check_rate_limit("user1")
        assert result1.allowed is False

        result2 = limiter.check_rate_limit("user2")
        assert result2.allowed is True

    def test_window_resets_after_time(self) -> None:
        """Requests should be allowed after window expires."""
        limiter = MemoryRateLimiter(limit_per_min=2)
        base_time = time.time()

        with patch("app.ai_engine.services.rate_limiter.time") as mock_time:
            mock_time.time.return_value = base_time
            limiter.check_rate_limit("user1")
            limiter.check_rate_limit("user1")

            mock_time.time.return_value = base_time + 61
            result = limiter.check_rate_limit("user1")
            assert result.allowed is True


class TestRateLimiter:
    """Tests for RateLimiter (main class with fallback)."""

    def test_disabled_limiter_always_allows(self) -> None:
        """Disabled limiter should always allow requests."""
        limiter = RateLimiter(redis_url=None, limit_per_min=1, enabled=False)

        for _ in range(10):
            result = limiter.check_rate_limit("user1")
            assert result.allowed is True
            assert result.current_count == 0

    def test_uses_memory_fallback_when_no_redis(self) -> None:
        """Should use memory fallback when Redis is not configured."""
        limiter = RateLimiter(redis_url=None, limit_per_min=2, enabled=True)

        result1 = limiter.check_rate_limit("user1")
        assert result1.allowed is True

        result2 = limiter.check_rate_limit("user1")
        assert result2.allowed is True

        result3 = limiter.check_rate_limit("user1")
        assert result3.allowed is False

    def test_uses_memory_fallback_on_redis_connection_error(self) -> None:
        """Should fallback to memory when Redis connection fails."""
        limiter = RateLimiter(
            redis_url="redis://nonexistent:6379",
            limit_per_min=2,
            enabled=True,
        )

        assert limiter._use_memory is True
        result = limiter.check_rate_limit("user1")
        assert result.allowed is True

    def test_reset_clears_memory_limiter(self) -> None:
        """Reset should clear memory limiter."""
        limiter = RateLimiter(redis_url=None, limit_per_min=1, enabled=True)

        limiter.check_rate_limit("user1")
        result = limiter.check_rate_limit("user1")
        assert result.allowed is False

        limiter.reset("user1")
        result = limiter.check_rate_limit("user1")
        assert result.allowed is True

    def test_accepts_integer_user_id(self) -> None:
        """Should accept integer user IDs."""
        limiter = RateLimiter(redis_url=None, limit_per_min=2, enabled=True)

        result = limiter.check_rate_limit(123)
        assert result.allowed is True
        assert result.current_count == 1

    def test_get_instance_singleton(self) -> None:
        """get_instance should return singleton."""
        RateLimiter.reset_instance()

        with patch("app.ai_engine.config.ai_engine_settings") as mock_settings:
            mock_settings.redis_url = None
            mock_settings.rate_limit_per_min = 30
            mock_settings.rate_limit_enabled = True

            instance1 = RateLimiter.get_instance()
            instance2 = RateLimiter.get_instance()

            assert instance1 is instance2

        RateLimiter.reset_instance()

    def test_reset_instance(self) -> None:
        """reset_instance should clear singleton."""
        RateLimiter.reset_instance()

        with patch("app.ai_engine.config.ai_engine_settings") as mock_settings:
            mock_settings.redis_url = None
            mock_settings.rate_limit_per_min = 30
            mock_settings.rate_limit_enabled = True

            instance1 = RateLimiter.get_instance()
            RateLimiter.reset_instance()
            instance2 = RateLimiter.get_instance()

            assert instance1 is not instance2

        RateLimiter.reset_instance()


class TestRedisRateLimiter:
    """Tests for RedisRateLimiter with mocked Redis (uses atomic Lua script via eval)."""

    def test_allows_requests_under_limit(self) -> None:
        """Requests under limit should be allowed."""
        mock_redis = MagicMock()
        # Lua script returns [1 (allowed), count, 0]
        mock_redis.eval.return_value = [1, 1, 0]

        limiter = RedisRateLimiter(mock_redis, limit_per_min=5)
        result = limiter.check_rate_limit("user1")

        assert result.allowed is True
        assert result.current_count == 1
        assert result.retry_after_ms is None
        mock_redis.eval.assert_called_once()

    def test_blocks_requests_at_limit(self) -> None:
        """Requests at limit should be blocked."""
        mock_redis = MagicMock()
        # Lua script returns [0 (blocked), count, retry_ms]
        mock_redis.eval.return_value = [0, 5, 30000]

        limiter = RedisRateLimiter(mock_redis, limit_per_min=5)
        result = limiter.check_rate_limit("user1")

        assert result.allowed is False
        assert result.current_count == 5
        assert result.retry_after_ms == 30000

    def test_reset_deletes_key(self) -> None:
        """Reset should delete Redis key."""
        mock_redis = MagicMock()

        limiter = RedisRateLimiter(mock_redis, limit_per_min=5)
        limiter.reset("user1")

        mock_redis.delete.assert_called_once_with("ai_ratelimit:user1")


class TestRateLimitResult:
    """Tests for RateLimitResult dataclass."""

    def test_allowed_result(self) -> None:
        """Test allowed result structure."""
        result = RateLimitResult(allowed=True, current_count=5, limit=10)

        assert result.allowed is True
        assert result.current_count == 5
        assert result.limit == 10
        assert result.retry_after_ms is None

    def test_blocked_result(self) -> None:
        """Test blocked result structure."""
        result = RateLimitResult(
            allowed=False,
            current_count=10,
            limit=10,
            retry_after_ms=30000,
        )

        assert result.allowed is False
        assert result.retry_after_ms == 30000

"""Tests for Context Compactor."""

import pytest

from app.ai_engine.exceptions import ContextTooLargeError
from app.ai_engine.services.context_compactor import (
    compact_context,
    estimate_tokens,
    validate_context_size,
)


class TestEstimateTokens:
    """Tests for token estimation."""

    def test_estimate_tokens_empty_string(self) -> None:
        """Empty string returns 0 tokens."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_short_text(self) -> None:
        """Short text returns expected token count."""
        text = "Hello world"
        tokens = estimate_tokens(text)
        # ~3.5 chars per token for multilingual
        assert tokens == int(len(text) / 3.5)

    def test_estimate_tokens_longer_text(self) -> None:
        """Longer text returns proportional token count."""
        text = "a" * 350
        assert estimate_tokens(text) == 100


class TestCompactContext:
    """Tests for context compaction."""

    def test_compact_context_returns_unchanged_if_under_limit(self) -> None:
        """Context under limit returns unchanged."""
        context = "Short context"
        result = compact_context(context, max_tokens=1000)
        assert result == context

    def test_compact_context_truncates_large_context(self) -> None:
        """Large context is truncated with marker."""
        context = "a" * 20000
        result = compact_context(context, max_tokens=1000)
        assert len(result) < len(context)
        assert "tronqué" in result

    def test_compact_context_preserves_head_and_tail(self) -> None:
        """Truncation preserves head and tail of content."""
        context = "HEAD" + "x" * 20000 + "TAIL"
        result = compact_context(context, max_tokens=1000)
        assert result.startswith("HEAD")
        assert result.endswith("TAIL")

    def test_compact_context_uses_settings_default(self) -> None:
        """Compact uses settings default when max_tokens not specified."""
        context = "Short context"
        result = compact_context(context)
        assert result == context


class TestValidateContextSize:
    """Tests for context size validation."""

    def test_validate_context_size_passes_for_small_context(self) -> None:
        """Small context passes validation."""
        validate_context_size("Small context", max_tokens=1000)

    def test_validate_context_size_raises_for_excessive_context(self) -> None:
        """Excessive context raises ContextTooLargeError."""
        context = "a" * 100000
        with pytest.raises(ContextTooLargeError) as exc_info:
            validate_context_size(context, max_tokens=1000)
        assert exc_info.value.status_code == 400

    def test_validate_context_size_respects_multiplier(self) -> None:
        """Validation respects hard limit multiplier."""
        context = "a" * 8000
        validate_context_size(context, max_tokens=1000, hard_limit_multiplier=3.0)
        with pytest.raises(ContextTooLargeError):
            validate_context_size(context, max_tokens=1000, hard_limit_multiplier=1.5)

"""Context Compactor for managing context size."""

from __future__ import annotations

import logging

from app.ai_engine.config import ai_engine_settings
from app.ai_engine.exceptions import ContextTooLargeError

logger = logging.getLogger(__name__)

# ~3.5 chars/token for multilingual content (French averages ~3.2, English ~4.0)
CHARS_PER_TOKEN_ESTIMATE = 3.5


def estimate_tokens(text: str) -> int:
    """Estimate token count from text length."""
    return int(len(text) / CHARS_PER_TOKEN_ESTIMATE)


def compact_context(
    context: str,
    *,
    max_tokens: int | None = None,
    strategy: str = "truncate",
) -> str:
    """
    Compact context to fit within token limits.

    Args:
        context: The context string to compact
        max_tokens: Maximum tokens allowed (default from settings)
        strategy: Compaction strategy - currently only 'truncate' is supported

    Returns:
        Compacted context string

    Note:
        The 'summarize' strategy is not yet implemented and falls back to 'truncate'.
        A future implementation could use LLM-based summarization.
    """
    if max_tokens is None:
        max_tokens = ai_engine_settings.context_max_tokens

    estimated_tokens = estimate_tokens(context)
    if estimated_tokens <= max_tokens:
        return context

    max_chars = int(max_tokens * CHARS_PER_TOKEN_ESTIMATE)
    effective_strategy = "truncate"

    if strategy == "summarize":
        logger.warning(
            "context_compactor_summarize_not_implemented falling_back_to=truncate"
        )
        effective_strategy = "truncate"

    compacted = _truncate_context(context, max_chars)

    final_tokens = estimate_tokens(compacted)
    logger.info(
        "context_compacted strategy=%s original_tokens=%d final_tokens=%d max_tokens=%d",
        effective_strategy,
        estimated_tokens,
        final_tokens,
        max_tokens,
    )

    return compacted


def _truncate_context(context: str, max_chars: int) -> str:
    """Truncate context to fit within character limit."""
    if len(context) <= max_chars:
        return context

    truncation_marker = "\n\n[...contexte tronqué pour respecter les limites...]\n\n"
    marker_len = len(truncation_marker)
    available_chars = max_chars - marker_len

    if available_chars <= 0:
        return context[:max_chars]

    head_chars = available_chars * 2 // 3
    tail_chars = available_chars - head_chars

    head = context[:head_chars]
    tail = context[-tail_chars:] if tail_chars > 0 else ""

    return head + truncation_marker + tail


def validate_context_size(
    context: str,
    *,
    max_tokens: int | None = None,
    hard_limit_multiplier: float = 3.0,
) -> None:
    """
    Validate that context is not excessively large.

    Args:
        context: The context string to validate
        max_tokens: Maximum tokens allowed (default from settings)
        hard_limit_multiplier: How many times max_tokens before rejection

    Raises:
        ContextTooLargeError: If context exceeds hard limit
    """
    if max_tokens is None:
        max_tokens = ai_engine_settings.context_max_tokens

    estimated_tokens = estimate_tokens(context)
    hard_limit = int(max_tokens * hard_limit_multiplier)

    if estimated_tokens > hard_limit:
        logger.warning(
            "context_too_large estimated_tokens=%d hard_limit=%d",
            estimated_tokens,
            hard_limit,
        )
        raise ContextTooLargeError(estimated_tokens, hard_limit)

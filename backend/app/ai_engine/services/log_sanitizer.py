"""Log sanitization utility for AI Engine to mask sensitive data."""

from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"

SENSITIVE_KEYS = frozenset(
    {
        "birth_data",
        "birth_date",
        "birthdate",
        "birth_time",
        "birthtime",
        "birth_place",
        "birthplace",
        "content",
        "message",
        "messages",
        "natal_chart_summary",
        "password",
        "api_key",
        "apikey",
        "secret",
        "token",
        "authorization",
        "credentials",
        "credit_card",
        "ssn",
        "social_security",
        "email",
        "phone",
        "address",
    }
)

PARTIAL_REDACT_KEYS = frozenset({"question", "text", "prompt"})

MAX_TEXT_LENGTH = 100


def _should_fully_redact(key: str) -> bool:
    """Check if key should be fully redacted."""
    key_lower = key.lower()
    return key_lower in SENSITIVE_KEYS or any(
        sensitive in key_lower for sensitive in ("password", "secret", "token", "key", "credential")
    )


def _should_partially_redact(key: str) -> bool:
    """Check if key should be partially redacted (truncated)."""
    return key.lower() in PARTIAL_REDACT_KEYS


def _truncate_text(value: str) -> str:
    """Truncate long text for logging."""
    if len(value) <= MAX_TEXT_LENGTH:
        return value
    return value[:MAX_TEXT_LENGTH] + f"... [truncated, {len(value)} chars total]"


def _redact_email(value: str) -> str:
    """Redact email addresses in text."""
    return re.sub(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "[EMAIL_REDACTED]",
        value,
    )


def _sanitize_value(key: str, value: Any) -> Any:
    """Sanitize a single value based on its key."""
    if value is None:
        return None

    if _should_fully_redact(key):
        if isinstance(value, str):
            return REDACTED
        if isinstance(value, dict):
            return REDACTED
        if isinstance(value, list):
            return REDACTED
        return REDACTED

    if _should_partially_redact(key) and isinstance(value, str):
        sanitized = _redact_email(value)
        return _truncate_text(sanitized)

    if isinstance(value, dict):
        return sanitize_for_logging(value)

    if isinstance(value, list):
        return [_sanitize_value(key, item) for item in value]

    if isinstance(value, str) and len(value) > MAX_TEXT_LENGTH * 2:
        return _truncate_text(_redact_email(value))

    return value


def sanitize_for_logging(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize a payload dict for safe logging.

    Masks sensitive data like birth information, message content,
    and any potential PII.

    Args:
        payload: The dict to sanitize

    Returns:
        A deep copy with sensitive values replaced by [REDACTED]
    """
    if not isinstance(payload, dict):
        return payload

    result = {}
    for key, value in payload.items():
        result[key] = _sanitize_value(key, value)
    return result


def sanitize_request_for_logging(
    use_case: str,
    user_id: int | str,
    request_id: str,
    trace_id: str,
    input_data: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """
    Build a sanitized log payload for an AI request.

    Args:
        use_case: The use case identifier
        user_id: User identifier
        request_id: Request identifier
        trace_id: Trace identifier
        input_data: Input parameters (will be sanitized)
        context: Context data (will be sanitized)
        **extra: Additional fields to include

    Returns:
        A dict safe for structured logging
    """
    result: dict[str, Any] = {
        "use_case": use_case,
        "user_id": str(user_id),
        "request_id": request_id,
        "trace_id": trace_id,
    }

    if input_data:
        result["input"] = sanitize_for_logging(input_data)

    if context:
        result["context"] = sanitize_for_logging(context)

    for key, value in extra.items():
        if isinstance(value, dict):
            result[key] = sanitize_for_logging(value)
        else:
            result[key] = value

    return result


def sanitize_messages_for_logging(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sanitize chat messages for logging.

    Preserves role but masks content.

    Args:
        messages: List of chat messages

    Returns:
        List with content masked
    """
    result = []
    for msg in messages:
        sanitized = {"role": msg.get("role", "unknown")}
        content = msg.get("content", "")
        if isinstance(content, str):
            sanitized["content_length"] = len(content)
            sanitized["content_preview"] = _truncate_text(content[:50]) if content else ""
        else:
            sanitized["content"] = REDACTED
        result.append(sanitized)
    return result

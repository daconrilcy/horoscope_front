"""Log sanitization utility for AI Engine to mask sensitive data."""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.core.sensitive_data import Sink, sanitize_payload

REDACTED = "[REDACTED]"


def sanitize_for_logging(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a payload dict for safe logging.

    Uses the central Sensitive Data Policy for STRUCTURED_LOGS sink.
    """
    if not isinstance(payload, dict):
        return payload

    return sanitize_payload(payload, Sink.STRUCTURED_LOGS)


def sanitize_request_for_logging(
    use_case: str,
    user_id: int | str,
    request_id: str,
    trace_id: str,
    input_data: Dict[str, Any] | None = None,
    context: Dict[str, Any] | None = None,
    **extra: Any,
) -> Dict[str, Any]:
    """
    Build a sanitized log payload for an AI request.
    """
    result: Dict[str, Any] = {
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
            # Re-classify and redact individual extra fields
            from app.core.sensitive_data import classify_field, get_policy_action, redact_value

            category = classify_field(key)
            action = get_policy_action(Sink.STRUCTURED_LOGS, category)
            result[key] = redact_value(value, action)

    return result


def sanitize_messages_for_logging(messages: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """
    Sanitize chat messages for logging.
    """
    result = []
    for msg in messages:
        sanitized = {"role": msg.get("role", "unknown")}
        content = msg.get("content", "")
        if isinstance(content, str):
            sanitized["content_length"] = len(content)
            # content_preview is risky, but policy says REDACTED for USER_AUTHORED_CONTENT in logs
            sanitized["content"] = REDACTED
        else:
            sanitized["content"] = REDACTED
        result.append(sanitized)
    return result


class SensitiveDataFilter(logging.Filter):
    """
    AC11: Python 3.13-style global logging filter for sensitive data.
    Acts as a terminal safety net.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Sanitize 'extra' fields if present (Python 3.12+)
        if hasattr(record, "args") and isinstance(record.args, dict):
            record.args = sanitize_for_logging(record.args)

        # In structured logging, 'extra' is often merged into record.__dict__
        # We can't safely iterate over record.__dict__ without affecting logging internals,
        # but we can target common patterns.

        # If the message itself is a dict (some loggers support this)
        if isinstance(record.msg, dict):
            record.msg = sanitize_for_logging(record.msg)

        return True

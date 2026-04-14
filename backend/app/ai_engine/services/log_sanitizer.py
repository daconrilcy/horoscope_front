"""Log sanitization utility for AI Engine to mask sensitive data."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict

REDACTED = "[REDACTED]"
EMAIL_REDACTED = "[EMAIL_REDACTED]"

_SECRET_MARKERS = ("password", "secret", "token", "api_key", "apikey", "authorization", "key")
_SENSITIVE_DOMAIN_MARKERS = ("birth", "natal", "chart", "astro")
_CONTENT_FIELDS = {"content", "message", "messages", "raw_output", "structured_output", "prompt"}
_SAFE_FIELDS = {
    "use_case",
    "locale",
    "request_id",
    "trace_id",
    "latency_ms",
    "cached",
    "role",
    "theme",
}


def _sanitize_text_preview(text: str, *, truncate: bool = False) -> str:
    sanitized = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", EMAIL_REDACTED, text)
    if truncate and len(sanitized) > 120:
        remaining = len(sanitized) - 120
        return f"{sanitized[:120]}...[truncated {remaining} chars]"
    return sanitized


def _sanitize_value(key: str, value: Any) -> Any:
    key_lower = key.lower()

    if value is None:
        return None

    if key in _SAFE_FIELDS:
        return value

    if any(marker in key_lower for marker in _SECRET_MARKERS):
        return REDACTED

    if any(marker in key_lower for marker in _SENSITIVE_DOMAIN_MARKERS):
        return REDACTED

    if key_lower in _CONTENT_FIELDS:
        return REDACTED

    if key_lower == "question":
        return _sanitize_text_preview(str(value), truncate=True)

    if isinstance(value, dict):
        return {
            nested_key: _sanitize_value(nested_key, nested_value)
            for nested_key, nested_value in value.items()
        }

    if isinstance(value, list):
        return [_sanitize_value(key, item) if isinstance(item, dict) else item for item in value]

    if isinstance(value, str):
        return _sanitize_text_preview(value)

    return value


def sanitize_for_logging(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a payload dict for safe logging.

    Applies a practical structured-log sanitizer:
    preserve operational metadata, redact secrets/domain-sensitive fields,
    and truncate free-form questions.
    """
    if not isinstance(payload, dict):
        return payload

    return {key: _sanitize_value(key, value) for key, value in payload.items()}


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
        result[key] = _sanitize_value(key, value)

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
            sanitized["content_preview"] = REDACTED
            sanitized["content"] = REDACTED
        else:
            sanitized["content_length"] = 0
            sanitized["content_preview"] = REDACTED
            sanitized["content"] = REDACTED
        result.append(sanitized)
    return result


class SensitiveDataFilter(logging.Filter):
    """
    AC11: Python 3.13-style global logging filter for sensitive data.
    Acts as a terminal safety net for all structured and unstructured logs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # 1. Sanitize 'msg' if it's a dict (common in structured logging)
        if isinstance(record.msg, dict):
            record.msg = sanitize_for_logging(record.msg)

        # 2. Sanitize positional 'args' (tuple) - AC11 fix for positional bypass
        if record.args:
            if isinstance(record.args, dict):
                record.args = sanitize_for_logging(record.args)
            elif isinstance(record.args, tuple):
                # Sanitize each element of the tuple
                new_args = list(record.args)
                for i, arg in enumerate(new_args):
                    if isinstance(arg, dict):
                        new_args[i] = sanitize_for_logging(arg)
                    elif isinstance(arg, str):
                        # Apply heuristics to individual strings in args
                        from app.core.sensitive_data import (
                            PolicyAction,
                            redact_value,
                        )

                        # We don't have a key here, but we can check if it looks like PII/Secret
                        # For safety in logs, we redact if it's highly sensitive
                        if any(
                            s in arg.lower()
                            for s in ("password", "secret", "token", "key", "authorization")
                        ):
                            new_args[i] = redact_value(arg, PolicyAction.REDACED)
                        elif "@" in arg and "." in arg:  # Likely email
                            new_args[i] = redact_value(arg, PolicyAction.MASKED)
                record.args = tuple(new_args)

        # 3. Handle 'extra' fields merged into record.__dict__
        # AC11: Comprehensive safety net for custom fields
        STANDARD_RECORD_ATTRS = frozenset(
            {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "asctime",
            }
        )
        for key, value in record.__dict__.items():
            if key not in STANDARD_RECORD_ATTRS and not key.startswith("_"):
                from app.core.sensitive_data import (
                    PolicyAction,
                    Sink,
                    classify_field,
                    get_policy_action,
                    redact_value,
                )

                category = classify_field(key)
                action = get_policy_action(Sink.STRUCTURED_LOGS, category)
                if action != PolicyAction.ALLOWED:
                    if isinstance(value, dict):
                        record.__dict__[key] = sanitize_for_logging(value)
                    else:
                        record.__dict__[key] = redact_value(value, action)

        return True

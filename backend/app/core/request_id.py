from __future__ import annotations

from uuid import uuid4

from fastapi import Request

_MAX_REQUEST_ID_LENGTH = 128


def _sanitize_request_id(value: str | None) -> str | None:
    """Sanitize request id from external sources before logging/persistence."""
    if value is None:
        return None
    cleaned = "".join(char for char in value.strip() if 32 <= ord(char) <= 126)
    if not cleaned:
        return None
    return cleaned[:_MAX_REQUEST_ID_LENGTH]


def resolve_request_id(request: Request) -> str:
    existing = _sanitize_request_id(getattr(request.state, "request_id", None))
    if existing is not None:
        request.state.request_id = existing
        return existing

    header_value = _sanitize_request_id(
        request.headers.get("X-Request-Id") or request.headers.get("x-request-id")
    )
    if header_value is not None:
        request.state.request_id = header_value
        return header_value
    generated = uuid4().hex
    request.state.request_id = generated
    return generated

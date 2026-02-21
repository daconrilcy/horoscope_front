from __future__ import annotations

from uuid import uuid4

from fastapi import Request


def resolve_request_id(request: Request) -> str:
    existing = getattr(request.state, "request_id", None)
    if isinstance(existing, str) and existing.strip():
        return existing.strip()

    header_value = request.headers.get("X-Request-Id") or request.headers.get("x-request-id")
    if header_value:
        trimmed = header_value.strip()
        if trimmed:
            request.state.request_id = trimmed
            return trimmed
    generated = uuid4().hex
    request.state.request_id = generated
    return generated

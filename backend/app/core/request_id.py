"""Centralise la résolution sûre des identifiants de corrélation HTTP."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Request

_MAX_CORRELATION_ID_LENGTH = 128


def _sanitize_correlation_id(value: str | None) -> str | None:
    """Nettoie un identifiant externe avant usage dans les logs et la persistance."""
    if value is None:
        return None
    cleaned = "".join(char for char in value.strip() if 32 <= ord(char) <= 126)
    if not cleaned:
        return None
    return cleaned[:_MAX_CORRELATION_ID_LENGTH]


def resolve_request_id(request: Request) -> str:
    """Résout l'identifiant de requête en privilégiant l'état puis le header HTTP."""
    existing = _sanitize_correlation_id(getattr(request.state, "request_id", None))
    if existing is not None:
        request.state.request_id = existing
        return existing

    header_value = _sanitize_correlation_id(
        request.headers.get("X-Request-Id") or request.headers.get("x-request-id")
    )
    if header_value is not None:
        request.state.request_id = header_value
        return header_value
    generated = uuid4().hex
    request.state.request_id = generated
    return generated


def resolve_trace_id(request: Request, *, fallback: str) -> str:
    """Résout l'identifiant de trace HTTP avec repli sur le request_id déjà sûr."""
    header_value = _sanitize_correlation_id(
        request.headers.get("X-Trace-Id") or request.headers.get("x-trace-id")
    )
    if header_value is not None:
        return header_value
    return fallback

"""Factories centralisées pour lever des erreurs applicatives depuis l'API."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ApplicationError


class ApiHttpError(ApplicationError):
    """Erreur applicative levée par l'API avec statut HTTP explicite."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            details=details or {},
            headers=headers,
        )
        self.http_status_code = status_code


def _code_for_status(status_code: int) -> str:
    """Associe un statut HTTP à un code applicatif stable."""
    if status_code == 400:
        return "invalid_request"
    if status_code == 401:
        return "unauthorized"
    if status_code == 403:
        return "forbidden"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limit_exceeded"
    if status_code == 503:
        return "audit_unavailable"
    if 400 <= status_code < 500:
        return "invalid_request"
    return "internal_error"


def _normalize_error_payload(
    *,
    status_code: int,
    code: str | None,
    message: str | dict[str, Any],
    details: dict[str, Any] | None,
) -> tuple[str, str, dict[str, Any]]:
    """Normalise une intention d'erreur API sans champ HTTP legacy."""
    if isinstance(message, dict):
        payload = dict(message)
        resolved_code = code or str(payload.pop("code", _code_for_status(status_code)))
        resolved_message = str(payload.pop("message", "request failed"))
        resolved_details = details if details is not None else payload
        return resolved_code, resolved_message, resolved_details

    return code or _code_for_status(status_code), message, details or {}


def raise_api_error(
    *,
    status_code: int,
    code: str | None = None,
    message: str | dict[str, Any],
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> None:
    """Lève une erreur applicative destinée au handler HTTP central."""
    resolved_code, resolved_message, resolved_details = _normalize_error_payload(
        status_code=status_code,
        code=code,
        message=message,
        details=details,
    )
    raise ApiHttpError(
        status_code=status_code,
        code=resolved_code,
        message=resolved_message,
        details=resolved_details,
        headers=headers,
    )

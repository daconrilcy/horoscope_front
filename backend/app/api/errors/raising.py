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
        legacy_detail: Any = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            details=details or {},
            headers=headers,
        )
        self.http_status_code = status_code
        self.legacy_detail = legacy_detail


def raise_api_error(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    legacy_detail: Any = None,
) -> None:
    """Lève une erreur applicative destinée au handler HTTP central."""
    raise ApiHttpError(
        status_code=status_code,
        code=code,
        message=message,
        details=details or {},
        headers=headers,
        legacy_detail=legacy_detail,
    )


def raise_http_error(
    *,
    status_code: int,
    detail: Any,
    headers: dict[str, str] | None = None,
) -> None:
    """Convertit une ancienne intention HTTP locale vers l'erreur API canonique."""
    message = detail if isinstance(detail, str) else "request failed"
    details = {} if isinstance(detail, str) else {"detail": detail}
    raise_api_error(
        status_code=status_code,
        code=_code_for_status(status_code),
        message=message,
        details=details,
        headers=headers,
        legacy_detail=detail,
    )


def _code_for_status(status_code: int) -> str:
    """Associe un statut HTTP historique à un code applicatif stable."""
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

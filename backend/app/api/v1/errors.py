"""Fabrique centralisée des erreurs HTTP des routeurs API v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ApiV1ErrorCode(StrEnum):
    """Codes d'erreur transverses réutilisables par plusieurs routeurs API v1."""

    INSUFFICIENT_ROLE = "insufficient_role"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_ERROR = "internal_error"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"


@dataclass(frozen=True, kw_only=True)
class ApiV1HttpError(Exception):
    """Erreur HTTP API v1 documentée, sérialisable et spécialisée par héritage."""

    request_id: str
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] | None = None
    status_code: int = 500

    def to_response(self) -> JSONResponse:
        """Convertit l'erreur métier HTTP en réponse JSON FastAPI stable."""
        content = {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": self.request_id,
            }
        }
        return JSONResponse(
            status_code=self.status_code,
            headers=self.headers,
            content=jsonable_encoder(content),
        )


@dataclass(frozen=True, kw_only=True)
class ApiV1BadRequestError(ApiV1HttpError):
    """Erreur API v1 pour les requêtes invalides."""

    status_code: int = 400


@dataclass(frozen=True, kw_only=True)
class ApiV1UnauthorizedError(ApiV1HttpError):
    """Erreur API v1 pour les accès non authentifiés."""

    status_code: int = 401


@dataclass(frozen=True, kw_only=True)
class ApiV1ForbiddenError(ApiV1HttpError):
    """Erreur API v1 pour les accès authentifiés mais interdits."""

    status_code: int = 403


@dataclass(frozen=True, kw_only=True)
class ApiV1NotFoundError(ApiV1HttpError):
    """Erreur API v1 pour les ressources absentes."""

    status_code: int = 404


@dataclass(frozen=True, kw_only=True)
class ApiV1ConflictError(ApiV1HttpError):
    """Erreur API v1 pour les conflits de règles ou d'état."""

    status_code: int = 409


@dataclass(frozen=True, kw_only=True)
class ApiV1RateLimitError(ApiV1HttpError):
    """Erreur API v1 pour les limites de débit."""

    status_code: int = 429


@dataclass(frozen=True, kw_only=True)
class ApiV1DomainError(ApiV1HttpError):
    """Erreur API v1 pour les échecs métier/domaines non représentés par une classe dédiée."""


def _error_class_for_status(status_code: int) -> type[ApiV1HttpError]:
    """Résout la spécialisation HTTP à partir du statut demandé par le routeur."""
    return {
        400: ApiV1BadRequestError,
        401: ApiV1UnauthorizedError,
        403: ApiV1ForbiddenError,
        404: ApiV1NotFoundError,
        409: ApiV1ConflictError,
        429: ApiV1RateLimitError,
    }.get(status_code, ApiV1DomainError)


def api_error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construit la réponse JSON d'erreur standard sans modifier le contrat existant."""
    error_class = _error_class_for_status(status_code)
    error = error_class(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details or {},
        headers=headers,
    )
    return error.to_response()

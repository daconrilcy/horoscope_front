"""Handlers FastAPI centralisés pour convertir les erreurs applicatives."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.errors.catalog import resolve_application_error_status
from app.api.errors.contracts import ApiErrorBody, ApiErrorEnvelope
from app.core.exceptions import ApplicationError
from app.core.request_id import resolve_request_id


def build_error_response(
    *,
    status_code: int,
    request_id: str | None,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construit l'enveloppe HTTP canonique d'une erreur API."""
    envelope = ApiErrorEnvelope(
        error=ApiErrorBody(
            code=code,
            message=message,
            details=details if details is not None else {},
            request_id=request_id,
        )
    )
    content = jsonable_encoder(envelope.model_dump(mode="json"))
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content=content,
    )


def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
    """Convertit une ApplicationError en réponse JSON FastAPI contrôlée."""
    status_code = getattr(error, "http_status_code", resolve_application_error_status(error.code))
    return build_error_response(
        status_code=status_code,
        request_id=resolve_request_id(request),
        code=error.code,
        message=error.message,
        details=error.details,
        headers=error.headers,
    )

"""Exports canoniques du package d'erreurs API."""

from app.api.errors.catalog import (
    HTTP_ERROR_CATALOG,
    ApiErrorCode,
    HttpErrorDefinition,
    resolve_application_error_status,
)
from app.api.errors.contracts import ApiErrorBody, ApiErrorEnvelope
from app.api.errors.handlers import application_error_handler, build_error_response
from app.api.errors.raising import raise_api_error

__all__ = [
    "ApiErrorBody",
    "ApiErrorCode",
    "ApiErrorEnvelope",
    "HTTP_ERROR_CATALOG",
    "HttpErrorDefinition",
    "application_error_handler",
    "build_error_response",
    "raise_api_error",
    "resolve_application_error_status",
]

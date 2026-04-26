"""Tests du contrat d'erreur HTTP centralisé pour l'API v1."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from app.api.v1.errors import (
    ApiV1ErrorCode,
    ApiV1ForbiddenError,
    ApiV1HttpError,
    api_error_response,
)


def test_api_error_response_builds_documented_envelope() -> None:
    """Vérifie que la fabrique produit l'enveloppe d'erreur documentée."""
    response = api_error_response(
        status_code=418,
        request_id="req-api-v1-error",
        code=ApiV1ErrorCode.INVALID_REQUEST,
        message="Payload invalide.",
        details={"field": "birth_date"},
        headers={"X-Test": "contract"},
    )

    assert response.status_code == 418
    assert response.headers["x-test"] == "contract"
    assert json.loads(response.body) == {
        "error": {
            "code": "invalid_request",
            "message": "Payload invalide.",
            "details": {"field": "birth_date"},
            "request_id": "req-api-v1-error",
        }
    }


def test_api_v1_error_families_inherit_from_base_error() -> None:
    """Verrouille le modèle AC13 basé sur une classe parente spécialisée."""
    error = ApiV1ForbiddenError(
        request_id="req-forbidden",
        code=ApiV1ErrorCode.INSUFFICIENT_ROLE,
        message="role is not allowed",
        details={"required_roles": "admin"},
    )

    assert isinstance(error, ApiV1HttpError)
    assert error.to_response().status_code == 403


def test_api_error_response_defaults_details_to_empty_object() -> None:
    """Garantit un objet details stable même sans détail métier."""
    response = api_error_response(
        status_code=404,
        request_id="req-missing",
        code=ApiV1ErrorCode.NOT_FOUND,
        message="Ressource introuvable.",
    )

    assert json.loads(response.body)["error"]["details"] == {}


def test_api_error_response_serializes_pydantic_compatible_details() -> None:
    """Préserve les détails métier contenant des types encodables par FastAPI."""
    response = api_error_response(
        status_code=409,
        request_id="req-datetime",
        code=ApiV1ErrorCode.INVALID_REQUEST,
        message="Conflit de validation.",
        details={"checked_at": datetime(2026, 4, 26, 10, 30, tzinfo=timezone.utc)},
    )

    assert json.loads(response.body)["error"]["details"] == {
        "checked_at": "2026-04-26T10:30:00+00:00"
    }

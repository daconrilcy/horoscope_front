"""Tests du contrat d'erreur HTTP centralisé pour l'API."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.errors import HTTP_ERROR_CATALOG, ApiErrorCode, build_error_response
from app.api.errors.catalog import resolve_application_error_status, validate_error_catalog
from app.api.errors.raising import ApiHttpError
from app.core.exceptions import ApplicationError


def test_build_error_response_builds_documented_envelope() -> None:
    """Vérifie que la fabrique produit l'enveloppe d'erreur documentée."""
    response = build_error_response(
        status_code=418,
        request_id="req-api-v1-error",
        code=ApiErrorCode.INVALID_REQUEST,
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


def test_application_error_is_outside_api_layer() -> None:
    """Verrouille la classe mère applicative hors FastAPI."""
    error = ApplicationError(
        code=ApiErrorCode.INSUFFICIENT_ROLE,
        message="role is not allowed",
        details={"required_roles": "admin"},
    )

    assert error.__class__.__module__ == "app.core.exceptions"
    assert not hasattr(error, "status_code")


def test_api_http_error_does_not_expose_legacy_status_code_property() -> None:
    """Verrouille l'abandon de l'alias legacy status_code côté erreurs API."""
    error = ApiHttpError(
        status_code=403,
        code=ApiErrorCode.INSUFFICIENT_ROLE,
        message="role is not allowed",
    )

    assert error.http_status_code == 403
    assert not hasattr(error, "status_code")


def test_build_error_response_defaults_details_to_empty_object() -> None:
    """Garantit un objet details stable même sans détail métier."""
    response = build_error_response(
        status_code=404,
        request_id="req-missing",
        code=ApiErrorCode.NOT_FOUND,
        message="Ressource introuvable.",
    )

    assert json.loads(response.body)["error"]["details"] == {}


def test_build_error_response_serializes_pydantic_compatible_details() -> None:
    """Préserve les détails métier contenant des types encodables par FastAPI."""
    response = build_error_response(
        status_code=409,
        request_id="req-datetime",
        code=ApiErrorCode.INVALID_REQUEST,
        message="Conflit de validation.",
        details={"checked_at": datetime(2026, 4, 26, 10, 30, tzinfo=timezone.utc)},
    )

    assert json.loads(response.body)["error"]["details"] == {"checked_at": "2026-04-26T10:30:00Z"}


def test_http_error_catalog_is_unique_and_valid() -> None:
    """Valide les invariants publics du catalogue HTTP centralisé."""
    validate_error_catalog()
    codes = [entry.code for entry in HTTP_ERROR_CATALOG]

    assert len(codes) == len(set(codes))
    assert all(400 <= entry.status_code <= 599 for entry in HTTP_ERROR_CATALOG)
    assert all(entry.message.strip() for entry in HTTP_ERROR_CATALOG)


@pytest.mark.parametrize(
    ("code", "expected_status"),
    [
        ("b2b_api_access_denied", 403),
        ("weekly_generation_failed", 422),
        ("enterprise_account_inactive", 422),
        ("alert_event_not_retryable", 409),
        ("token_expired", 401),
        ("invalid_token_type", 401),
    ],
)
def test_resolve_application_error_status_covers_regression_codes(
    code: str, expected_status: int
) -> None:
    """Verrouille les codes métier observés dans la suite d'intégration."""
    assert resolve_application_error_status(code) == expected_status


def test_application_error_handler_fallback_contract() -> None:
    """Vérifie qu'une erreur applicative non dédiée garde l'enveloppe JSON."""
    from app.main import app

    @app.get("/__test_application_error")
    def _raise_application_error() -> None:
        raise ApplicationError(
            code="contract_conflict",
            message="contract conflict",
            details={"field": "email"},
        )

    response = TestClient(app).get(
        "/__test_application_error", headers={"X-Request-Id": "req-test"}
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "contract_conflict",
            "message": "contract conflict",
            "details": {"field": "email"},
            "request_id": "req-test",
        }
    }


def test_application_error_rejects_invalid_missing_arguments() -> None:
    """Documente l'absence de contrat dict libre pour les erreurs applicatives."""
    with pytest.raises(TypeError):
        ApplicationError()  # type: ignore[call-arg]

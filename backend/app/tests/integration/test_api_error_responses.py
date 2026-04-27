"""Tests d'intégration de l'enveloppe d'erreur API centralisée."""

from __future__ import annotations

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.v1.schemas.common import ErrorEnvelope
from app.core.exceptions import ApplicationError
from app.main import app


def test_application_error_response_uses_canonical_envelope() -> None:
    """Vérifie le format JSON public produit par le handler central."""

    @app.get("/__test_canonical_api_error")
    def _raise_application_error() -> None:
        raise ApplicationError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"limit": 1},
        )

    response = TestClient(app).get(
        "/__test_canonical_api_error", headers={"X-Request-Id": "req-integration-error"}
    )

    assert response.status_code == 429
    assert response.json() == {
        "error": {
            "code": "rate_limit_exceeded",
            "message": "rate limit exceeded",
            "details": {"limit": 1},
            "request_id": "req-integration-error",
        }
    }


def test_openapi_paths_are_still_available_after_error_package_migration() -> None:
    """Vérifie que les routes FastAPI actives restent exposées dans OpenAPI."""
    app.openapi_schema = None
    openapi = app.openapi()
    openapi_paths = openapi["paths"]
    missing: list[str] = []

    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", None)
        if not path or path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
            continue
        if methods is None:
            continue
        documented_methods = set(openapi_paths.get(path, {}))
        expected_methods = {
            method.lower() for method in methods if method not in {"HEAD", "OPTIONS"}
        }
        missing_methods = sorted(expected_methods - documented_methods)
        if path not in openapi_paths or missing_methods:
            missing.append(f"{path}:{','.join(missing_methods) or 'path'}")

    assert missing == []


def test_openapi_does_not_duplicate_canonical_api_error_schemas() -> None:
    """Le package central ne doit pas ajouter de second schéma public d'erreur."""
    schemas = app.openapi().get("components", {}).get("schemas", {})

    assert "ApiErrorBody" not in schemas
    assert "ApiErrorEnvelope" not in schemas


def test_openapi_declares_targeted_error_statuses_after_error_migration() -> None:
    """Vérifie que les statuts d'erreur déclarés restent présents dans OpenAPI."""
    app.openapi_schema = None
    openapi_paths = app.openapi()["paths"]
    missing_statuses: list[str] = []
    invalid_error_refs: list[str] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        declared_error_responses = {
            status_code: response_spec
            for status_code, response_spec in route.responses.items()
            if isinstance(status_code, int) and status_code >= 400
        }
        if not declared_error_responses:
            continue

        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            operation = openapi_paths.get(route.path, {}).get(method.lower(), {})
            documented_responses = operation.get("responses", {})
            for status_code, response_spec in declared_error_responses.items():
                documented = documented_responses.get(str(status_code))
                if documented is None:
                    missing_statuses.append(f"{route.path}:{method.lower()}:{status_code}")
                    continue

                if response_spec.get("model") is not ErrorEnvelope:
                    continue
                schema = documented.get("content", {}).get("application/json", {}).get("schema", {})
                if schema.get("$ref") != "#/components/schemas/ErrorEnvelope":
                    invalid_error_refs.append(f"{route.path}:{method.lower()}:{status_code}")

    assert missing_statuses == []
    assert invalid_error_refs == []

# Tests API des refus controles du endpoint de projections.
"""Verifie les erreurs publiques sans exposer les projections internes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.public.projections import get_projection_endpoint_service
from app.core.auth_context import AuthenticatedUser
from app.main import app
from app.services.projections.projection_endpoint_service import ProjectionEndpointServiceError


class _DenyingProjectionService:
    """Service factice qui simule les refus de l'orchestrateur."""

    def __init__(self, error: ProjectionEndpointServiceError) -> None:
        self.error = error

    def generate(self, **_: Any) -> None:
        """Leve le refus controle attendu par le routeur."""
        raise self.error


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> None:
    """Isole les overrides FastAPI afin de ne pas polluer les autres tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_projection_endpoint_denies_internal_projection_identifier() -> None:
    """Le routeur conserve l'enveloppe d'erreur publique pour un type interne."""
    client = _client_with(
        _DenyingProjectionService(
            ProjectionEndpointServiceError(
                code="projection.unauthorized",
                message="projection type is not authorized for B2C clients",
                details={"projection_type": "expert_technical_projection_v1"},
            )
        )
    )

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-123",
            "projection_type": "expert_technical_projection_v1",
            "projection_version": "v1",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "projection.unauthorized"
    assert "provider" not in str(response.json()).lower()


def test_projection_endpoint_denies_insufficient_plan() -> None:
    """Le refus plan_insufficient reste explicite et client-readable."""
    client = _client_with(
        _DenyingProjectionService(
            ProjectionEndpointServiceError(
                code="projection.unauthorized",
                message="user plan is not authorized for public projections",
                details={"current_plan": "none", "required_plan": "free"},
            )
        )
    )

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-123",
            "projection_type": "client_interpretation_projection_v1",
            "projection_version": "v1",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["details"]["current_plan"] == "none"


def _client_with(service: _DenyingProjectionService) -> TestClient:
    """Configure les overrides FastAPI strictement necessaires au test."""
    app.dependency_overrides[require_authenticated_user] = lambda: AuthenticatedUser(
        id=10,
        role="user",
        email="user@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_projection_endpoint_service] = lambda: service
    return TestClient(app)

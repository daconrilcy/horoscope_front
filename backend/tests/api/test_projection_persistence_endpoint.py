# Tests API du statut de persistance des projections.
"""Couvre le contrat HTTP de retour quand `persist=true`."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.public.projections import get_projection_endpoint_service
from app.core.auth_context import AuthenticatedUser
from app.main import app
from app.services.api_contracts.public.projections import (
    ProjectionCommandMetadata,
    ProjectionCommandResponse,
)


class _PersistedProjectionService:
    """Service factice qui retourne une projection persistee."""

    def generate(self, **kwargs: Any) -> ProjectionCommandResponse:
        """Retourne la reponse persistee minimale attendue."""
        request = kwargs["request"]
        return ProjectionCommandResponse(
            chart_id=request.chart_id,
            projection_type="beginner_summary_v1",
            projection_version="v1",
            persisted=True,
            projection_hash="a" * 64,
            payload={"projection_id": "beginner_summary_v1"},
            metadata=ProjectionCommandMetadata(
                source="chart_id",
                plan_code="free",
                request_id=kwargs["request_id"],
                persisted_id=1,
            ),
        )


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> None:
    """Isole les overrides FastAPI afin de ne pas polluer les autres tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_projection_endpoint_exposes_projection_hash_when_persisted() -> None:
    """La reponse persistee expose le hash public et les metadonnees d'identite."""
    client = _client_with(_PersistedProjectionService())

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-123",
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
            "persist": True,
        },
    )

    body = response.json()
    assert response.status_code == 201
    assert body["projection_hash"] == "a" * 64
    assert body["metadata"]["persisted_id"] == 1


def _client_with(service: _PersistedProjectionService) -> TestClient:
    """Configure les overrides FastAPI strictement necessaires au test."""
    app.dependency_overrides[require_authenticated_user] = lambda: AuthenticatedUser(
        id=10,
        role="user",
        email="user@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_projection_endpoint_service] = lambda: service
    return TestClient(app)

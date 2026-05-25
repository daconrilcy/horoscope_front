# Tests API du endpoint public generique de projections.
"""Verifie la route canonique et la selection de source chart_id/birth_input."""

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


class _FakeProjectionService:
    """Service de route factice pour isoler le contrat HTTP."""

    def __init__(self, *, persisted: bool = False) -> None:
        self.persisted = persisted
        self.last_request: Any = None

    def generate(self, **kwargs: Any) -> ProjectionCommandResponse:
        """Retourne une projection publique minimale et conserve la requete."""
        self.last_request = kwargs["request"]
        return ProjectionCommandResponse(
            chart_id=self.last_request.chart_id or "generated-chart",
            projection_type="beginner_summary_v1",
            projection_version="v1",
            persisted=self.persisted,
            projection_hash="a" * 64,
            payload={"projection_id": "beginner_summary_v1"},
            metadata=ProjectionCommandMetadata(
                source="chart_id" if self.last_request.chart_id else "birth_input",
                plan_code="free",
                request_id=kwargs["request_id"],
                persisted_id=1 if self.persisted else None,
            ),
        )


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> None:
    """Isole les overrides FastAPI afin de ne pas polluer les autres tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_projection_endpoint_accepts_existing_chart_id() -> None:
    """Le POST canonique transmet chart_id au service applicatif."""
    service = _FakeProjectionService()
    client = _client_with(service)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-123",
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
        },
    )

    assert response.status_code == 200
    assert response.json()["chart_id"] == "chart-123"
    assert response.json()["metadata"]["source"] == "chart_id"
    assert service.last_request.chart_id == "chart-123"


def test_projection_endpoint_accepts_birth_input_source() -> None:
    """Le POST canonique transmet birth_input quand aucun chart_id n'est fourni."""
    service = _FakeProjectionService()
    client = _client_with(service)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "birth_input": {
                "birth_date": "1990-01-01",
                "birth_time": "12:00",
                "birth_place": "Paris",
                "birth_timezone": "Europe/Paris",
            },
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
        },
    )

    assert response.status_code == 200
    assert response.json()["metadata"]["source"] == "birth_input"
    assert service.last_request.birth_input.birth_place == "Paris"


def test_projection_endpoint_returns_created_when_persisted() -> None:
    """Une projection persistee retourne le statut HTTP 201."""
    client = _client_with(_FakeProjectionService(persisted=True))

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-123",
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
            "persist": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["persisted"] is True
    assert response.json()["metadata"]["persisted_id"] == 1


def _client_with(service: _FakeProjectionService) -> TestClient:
    """Configure les overrides FastAPI strictement necessaires au test."""
    app.dependency_overrides[require_authenticated_user] = lambda: AuthenticatedUser(
        id=10,
        role="user",
        email="user@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    app.dependency_overrides[get_projection_endpoint_service] = lambda: service
    return TestClient(app)

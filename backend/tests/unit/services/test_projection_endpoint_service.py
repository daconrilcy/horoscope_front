# Tests unitaires de l'orchestrateur de projections publiques.
"""Verifie dispatch, droits par plan et reutilisation de la persistance CS-264."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from app.core.auth_context import AuthenticatedUser
from app.services.api_contracts.public.projections import ProjectionCommandRequest
from app.services.entitlement.entitlement_types import EffectiveEntitlementsSnapshot
from app.services.projections.projection_endpoint_service import (
    ProjectionEndpointService,
    ProjectionEndpointServiceError,
    _ResolvedChart,
)


class _StructuredBuilder:
    """Builder structured_facts factice qui represente le builder public livre."""

    def build(self, *_: Any, **__: Any) -> dict[str, Any]:
        """Produit un payload structured_facts minimal."""
        return {
            "projection_id": "structured_facts_v1",
            "source_versions": {"structured_facts_contract": "test"},
        }


class _BeginnerBuilder:
    """Builder beginner_summary factice."""

    def build(self, structured_facts: dict[str, Any]) -> dict[str, Any]:
        """Produit un payload dependant de structured_facts."""
        assert structured_facts["projection_id"] == "structured_facts_v1"
        return {"projection_id": "beginner_summary_v1"}


class _ClientBuilder:
    """Builder client_interpretation factice avec capture du plan."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def build(
        self,
        structured_facts: dict[str, Any],
        *,
        requested_plan: str,
        current_plan: str,
    ) -> dict[str, Any]:
        """Produit un payload par plan sans lire un plan client."""
        assert structured_facts["projection_id"] == "structured_facts_v1"
        self.calls.append({"requested_plan": requested_plan, "current_plan": current_plan})
        return {"projection_id": "client_interpretation_projection_v1", "plan": current_plan}


class _PersistenceService:
    """Persistance factice qui verifie le passage par le service CS-264."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def persist_from_builder(self, **kwargs: Any) -> Any:
        """Capture les arguments et retourne une identite persistee."""
        self.calls.append(kwargs)
        return SimpleNamespace(id=42, projection_hash="b" * 64)


def test_service_dispatches_public_builder_with_resolved_plan() -> None:
    """Le plan vient du resolver entitlement et pilote la profondeur client."""
    service, client_builder, _ = _service(plan_code="premium")

    response = service.generate(
        request=ProjectionCommandRequest(
            chart_id="chart-123",
            projection_type="client_interpretation_projection_v1",
            projection_version="v1",
        ),
        current_user=_user(),
        request_id="req-1",
    )

    assert response.payload["projection_id"] == "client_interpretation_projection_v1"
    assert response.payload["plan"] == "premium"
    assert client_builder.calls == [{"requested_plan": "premium", "current_plan": "premium"}]


def test_service_denies_internal_projection_identifier() -> None:
    """Les projections internes sont refusees avant tout dispatch de builder."""
    service, _, _ = _service(plan_code="premium")

    with pytest.raises(ProjectionEndpointServiceError) as error:
        service.generate(
            request=ProjectionCommandRequest(
                chart_id="chart-123",
                projection_type="expert_technical_projection_v1",
                projection_version="v1",
            ),
            current_user=_user(),
            request_id="req-1",
        )

    assert error.value.code == "projection.unauthorized"


def test_service_reuses_projection_persistence_service_when_requested() -> None:
    """`persist=true` passe par le service de persistance canonique."""
    service, _, persistence = _service(plan_code="basic")

    response = service.generate(
        request=ProjectionCommandRequest(
            chart_id="chart-123",
            projection_type="beginner_summary_v1",
            projection_version="v1",
            persist=True,
        ),
        current_user=_user(),
        request_id="req-1",
    )

    assert response.persisted is True
    assert response.projection_hash == "b" * 64
    assert response.metadata.persisted_id == 42
    assert persistence.calls[0]["projection_type"] == "beginner_summary_v1"
    assert persistence.calls[0]["builder"].__class__ is _BeginnerBuilder


def test_service_rejects_client_supplied_plan_field() -> None:
    """Le schema refuse un plan client au lieu de le faire confiance."""
    with pytest.raises(ValueError):
        ProjectionCommandRequest.model_validate(
            {
                "chart_id": "chart-123",
                "projection_type": "client_interpretation_projection_v1",
                "projection_version": "v1",
                "plan": "premium",
            }
        )


def _service(
    *,
    plan_code: str,
) -> tuple[ProjectionEndpointService, _ClientBuilder, _PersistenceService]:
    """Construit un service avec dependances isolees."""
    persistence = _PersistenceService()
    service = ProjectionEndpointService(
        SimpleNamespace(),
        persistence_service=persistence,  # type: ignore[arg-type]
        entitlement_resolver=lambda _db, user_id: EffectiveEntitlementsSnapshot(
            subject_type="b2c_user",
            subject_id=user_id,
            plan_code=plan_code,
            billing_status="active",
            entitlements={},
        ),
    )
    service._resolve_chart = lambda **_: _ResolvedChart(  # type: ignore[method-assign]
        chart_id="chart-123",
        natal_result=SimpleNamespace(),
        source="chart_result",
    )
    service.structured_builder = _StructuredBuilder()
    service.beginner_builder = _BeginnerBuilder()
    client_builder = _ClientBuilder()
    service.client_builder = client_builder
    return service, client_builder, persistence


def _user() -> AuthenticatedUser:
    """Retourne un utilisateur B2C authentifie minimal."""
    return AuthenticatedUser(
        id=10,
        role="user",
        email="user@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )

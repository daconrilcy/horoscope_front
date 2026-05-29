# Tests API realistes du endpoint public de projections.
"""Prouve le contrat HTTP B2C avec TestClient, routeur et builders publics."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.public.projections import get_projection_endpoint_service
from app.core.auth_context import AuthenticatedUser
from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.natal_calculation import AspectResult, NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.main import app
from app.services.entitlement.entitlement_types import EffectiveEntitlementsSnapshot
from app.services.projections.projection_endpoint_service import (
    ProjectionEndpointService,
    _ResolvedChart,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference
from tests.unit.domain.astrology.interpretation.support import interpretable_chart_object


@dataclass(frozen=True, slots=True)
class _NatalSource:
    """Source natale minimale consommee par les builders publics reels."""

    chart_objects: tuple[object, ...]
    aspects: tuple[object, ...]
    dominant_planets: DominantPlanetsResult | None = None
    advanced_condition_facts: tuple[object, ...] = ()
    chart_balance: object | None = None


class _ChartRepository:
    """Depot factice qui laisse le service produire un 404 public stable."""

    def get_by_chart_id(self, _chart_id: str) -> None:
        """Retourne une absence explicite de theme persiste."""
        return None


class _PersistedChartRepository:
    """Depot factice qui simule un theme persiste sans chart_objects internes."""

    def __init__(self, natal_result: NatalResult) -> None:
        self._payload = natal_result.model_dump(mode="json")

    def get_by_chart_id(self, chart_id: str) -> SimpleNamespace:
        """Retourne le payload stocke pour un chart_id connu."""
        return SimpleNamespace(user_id=10, result_payload=self._payload)


class _PersistenceService:
    """Persistance factice necessaire a l'initialisation du service."""

    def persist_from_builder(self, **_: Any) -> Any:
        """Retourne une identite stable si un test active `persist=true`."""
        return SimpleNamespace(id=99, projection_hash="c" * 64)


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> None:
    """Isole les overrides FastAPI afin de ne pas polluer les autres tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("projection_type", "expected_payload_id"),
    (
        ("structured_facts_v1", "structured_facts_v1"),
        ("beginner_summary_v1", "beginner_summary_v1"),
        ("client_interpretation_projection_v1", "client_interpretation_projection_v1"),
    ),
)
def test_projection_endpoint_returns_public_shapes_for_supported_types(
    projection_type: str,
    expected_payload_id: str,
) -> None:
    """Chaque projection publique traverse le endpoint canonique en HTTP."""
    client = _client_with_service(plan_code="premium")

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-realistic",
            "projection_type": projection_type,
            "projection_version": "v1",
        },
        headers={"X-Request-Id": "req-real-conditions"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["projection_type"] == projection_type
    assert body["projection_version"] == "v1"
    assert body["projection_hash"]
    assert body["payload"]["projection_id"] == expected_payload_id
    assert body["metadata"] == {
        "source": "chart_id",
        "plan_code": "premium",
        "request_id": "req-real-conditions",
        "persisted_id": None,
    }


@pytest.mark.parametrize("plan_code", ("free", "basic", "premium"))
def test_projection_endpoint_accepts_supported_b2c_plans(plan_code: str) -> None:
    """La matrice free/basic/premium vient du resolver entitlement existant."""
    client = _client_with_service(plan_code=plan_code)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-realistic",
            "projection_type": "client_interpretation_projection_v1",
            "projection_version": "v1",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["metadata"]["plan_code"] == plan_code
    assert body["payload"]["projection_id"] == "client_interpretation_projection_v1"


def test_projection_endpoint_rejects_invalid_payload_shape() -> None:
    """Les payloads invalides restent des erreurs FastAPI explicites."""
    client = _client_with_service(plan_code="free")

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-realistic",
            "projection_type": "structured_facts_v1",
            "projection_version": "v1",
            "unexpected": "not-public",
        },
    )

    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "invalid_request_payload"
    assert body["error"]["details"]["errors"][0]["type"] == "extra_forbidden"
    assert body["error"]["details"]["errors"][0]["loc"] == ["body", "unexpected"]


def test_projection_endpoint_returns_public_error_for_missing_chart() -> None:
    """Un chart_id inexistant devient un 404 public sans fuite interne."""
    client = _client_with_service(plan_code="free", resolve_chart=False)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "unknown-chart",
            "projection_type": "structured_facts_v1",
            "projection_version": "v1",
        },
    )

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["request_id"]
    assert error | {"request_id": None} == {
        "code": "projection.chart_not_found",
        "message": "chart result was not found for this user",
        "details": {"chart_id": "unknown-chart"},
        "request_id": None,
    }


def test_projection_endpoint_exposes_degraded_birth_input_without_time() -> None:
    """Une naissance sans heure reste visible comme projection degradee."""
    client = _client_with_service(plan_code="basic", no_time=True)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "birth_input": {
                "birth_date": "1990-01-01",
                "birth_place": "Paris",
                "birth_timezone": "Europe/Paris",
            },
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["metadata"]["source"] == "birth_input"
    assert body["payload"]["state"] == "degraded"
    assert body["payload"]["degraded_reason"] == "no_time"
    assert body["payload"]["missing_data"] == ["no_time"]


def test_projection_endpoint_persisted_chart_returns_normal_state() -> None:
    """Un chart_id persiste complet ne doit plus retourner state=degraded."""
    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )
    persisted = NatalResult.model_validate(result.model_dump(mode="json"))
    assert persisted.chart_objects == []

    service = ProjectionEndpointService(
        SimpleNamespace(),
        chart_repository=_PersistedChartRepository(persisted),  # type: ignore[arg-type]
        persistence_service=_PersistenceService(),  # type: ignore[arg-type]
        entitlement_resolver=lambda _db, user_id: EffectiveEntitlementsSnapshot(
            subject_type="b2c_user",
            subject_id=user_id,
            plan_code="basic",
            billing_status="active",
            entitlements={},
        ),
    )
    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_projection_endpoint_service] = lambda: service
    client = TestClient(app)

    response = client.post(
        "/v1/astrology/projections",
        json={
            "chart_id": "chart-persisted",
            "projection_type": "beginner_summary_v1",
            "projection_version": "v1",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["metadata"]["source"] == "chart_id"
    assert body["metadata"]["plan_code"] == "basic"
    assert body["payload"]["state"] == "normal"


def _client_with_service(
    *,
    plan_code: str,
    no_time: bool = False,
    resolve_chart: bool = True,
) -> TestClient:
    """Configure un TestClient authentifie avec l'orchestrateur applicatif."""
    service = ProjectionEndpointService(
        SimpleNamespace(),
        chart_repository=_ChartRepository(),  # type: ignore[arg-type]
        persistence_service=_PersistenceService(),  # type: ignore[arg-type]
        entitlement_resolver=lambda _db, user_id: EffectiveEntitlementsSnapshot(
            subject_type="b2c_user",
            subject_id=user_id,
            plan_code=plan_code,
            billing_status="active",
            entitlements={},
        ),
    )
    if resolve_chart:
        service._resolve_chart = lambda request, current_user: _ResolvedChart(  # type: ignore[method-assign]
            chart_id="chart-realistic",
            natal_result=_natal_source(no_time=no_time),
            source="birth_input" if request.birth_input is not None else "chart_result",
        )
    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_projection_endpoint_service] = lambda: service
    return TestClient(app)


def _authenticated_user() -> AuthenticatedUser:
    """Retourne un utilisateur B2C authentifie minimal."""
    return AuthenticatedUser(
        id=10,
        role="user",
        email="user@example.test",
        created_at=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )


def _natal_source(*, no_time: bool) -> _NatalSource:
    """Construit une source runtime coherente sans recalcul astronomique."""
    chart_object = (
        _chart_object_without_house_time() if no_time else interpretable_chart_object("mars")
    )
    return _NatalSource(
        chart_objects=(chart_object,),
        aspects=()
        if no_time
        else (
            AspectResult(
                aspect_code="trine",
                planet_a="sun",
                planet_b="moon",
                angle=120.0,
                orb=1.0,
                orb_used=1.0,
                orb_max=6.0,
                family="major",
                is_major=True,
                is_minor=False,
            ),
        ),
        dominant_planets=None
        if no_time
        else DominantPlanetsResult(
            score_profile_code="fixture.profile",
            tradition_code="fixture",
            reference_version_code="v1",
            planets=(
                PlanetDominanceResult(
                    planet_code="mars",
                    total_score=0.82,
                    rank=1,
                    dominance_level="dominant",
                    factors=(
                        PlanetDominanceFactor(
                            factor_code="angularity",
                            raw_value=1.0,
                            normalized_value=1.0,
                            weight=0.5,
                            weighted_score=0.5,
                            reason="fixture",
                        ),
                    ),
                    explanation_facts=("fixture",),
                ),
            ),
            top_planet_code="mars",
            chart_ruler_code=None,
            most_elevated_planet_code=None,
        ),
    )


def _chart_object_without_house_time() -> object:
    """Conserve les positions mais retire les maisons dependantes de l'heure."""
    chart_object = interpretable_chart_object("sun")
    return replace(
        chart_object,
        capabilities=replace(chart_object.capabilities, supports_house_position=False),
        payloads=replace(chart_object.payloads, house_position=None),
    )

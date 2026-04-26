"""Tests d'intégration pour les endpoints d'interprétation du thème natal V2."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.domain.astrology.natal_calculation import (
    AspectResult,
    HouseResult,
    NatalResult,
    PlanetPosition,
)
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.domain.llm.runtime.contracts import (
    GatewayConfigError,
    GatewayMeta,
    GatewayResult,
    UsageInfo,
)
from app.infra.db.session import get_db_session
from app.main import app
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from app.services.user_profile.natal_chart_service import (
    UserNatalChartMetadata,
    UserNatalChartReadData,
)


def _make_natal_result() -> NatalResult:
    """Crée un NatalResult de test."""
    return NatalResult(
        reference_version="v1.0",
        ruleset_version="r1.0",
        house_system="placidus",
        prepared_input=BirthPreparedData(
            birth_datetime_local="1990-06-15T14:30:00+02:00",
            birth_datetime_utc="1990-06-15T12:30:00+00:00",
            timestamp_utc=645364200,
            julian_day=2448073.02,
            birth_timezone="Europe/Paris",
        ),
        planet_positions=[
            PlanetPosition(planet_code="sun", longitude=84.5, sign_code="gemini", house_number=10),
            PlanetPosition(
                planet_code="moon", longitude=112.3, sign_code="cancer", house_number=11
            ),
        ],
        houses=[
            HouseResult(number=1, cusp_longitude=195.5),
            HouseResult(number=10, cusp_longitude=105.3),
            HouseResult(number=7, cusp_longitude=15.5),
            HouseResult(number=4, cusp_longitude=285.2),
        ],
        aspects=[
            AspectResult(
                aspect_code="conjunction", planet_a="sun", planet_b="moon", angle=0.0, orb=2.0
            ),
        ],
    )


def _make_chart_read_data() -> UserNatalChartReadData:
    """Crée un UserNatalChartReadData de test."""
    return UserNatalChartReadData(
        chart_id="chart-test-123",
        result=_make_natal_result(),
        metadata=UserNatalChartMetadata(
            reference_version="v1.0",
            ruleset_version="r1.0",
        ),
        created_at=datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc),
    )


def _make_birth_profile() -> UserBirthProfileData:
    """Crée un UserBirthProfileData de test."""
    return UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_lat=48.8566,
        birth_lon=2.3522,
        birth_timezone="Europe/Paris",
    )


def _make_gateway_result(use_case: str, persona_id: str | None = None) -> GatewayResult:
    """Crée un GatewayResult de test."""
    if use_case == "natal_interpretation":
        # Story 30-8: Premium V3 data
        structured_output = {
            "title": "Thème natal test V3",
            "summary": "Résumé de test long..." * 100,  # > 900 chars
            "sections": [
                {
                    "key": "overall",
                    "heading": "Vue d'ensemble",
                    "content": "Contenu très long et dense pour la section overall..." * 50,
                },
                {
                    "key": "career",
                    "heading": "Carrière",
                    "content": "Contenu très long et dense pour la section career..." * 50,
                },
                {
                    "key": "relationships",
                    "heading": "Relations",
                    "content": "Contenu très long et dense pour la section relationships..." * 50,
                },
                {
                    "key": "inner_life",
                    "heading": "Vie intérieure",
                    "content": "Contenu très long et dense pour la section inner_life..." * 50,
                },
                {
                    "key": "daily_life",
                    "heading": "Vie quotidienne",
                    "content": "Contenu très long et dense pour la section daily_life..." * 50,
                },
            ],
            "highlights": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
            "advice": ["Conseil 1", "Conseil 2", "Conseil 3", "Conseil 4", "Conseil 5"],
            "evidence": ["SUN_TAURUS", "MOON_SCORPIO"],
            # NB: AstroResponseV3 DOES NOT have disclaimers
        }
    else:
        # AstroResponseV1
        structured_output = {
            "title": "Thème natal test",
            "summary": "Résumé de test concis.",
            "sections": [
                {"key": "overall", "heading": "Vue d'ensemble", "content": "Contenu..."},
                {"key": "career", "heading": "Carrière", "content": "Contenu..."},
            ],
            "highlights": ["Point 1", "Point 2", "Point 3"],
            "advice": ["Conseil 1", "Conseil 2", "Conseil 3"],
            "evidence": ["SUN_TAURUS", "MOON_SCORPIO"],
            "disclaimers": ["Mock disclaimer"],
        }
    raw_output = json.dumps(structured_output)
    return GatewayResult(
        use_case=use_case,
        request_id="test-req-id",
        trace_id="test-trace-id",
        raw_output=raw_output,
        structured_output=structured_output,
        usage=UsageInfo(
            input_tokens=100, output_tokens=200, total_tokens=300, estimated_cost_usd=0.001
        ),
        meta=GatewayMeta(
            latency_ms=500,
            cached=False,
            prompt_version_id=str(uuid.uuid4()),
            persona_id=persona_id,
            model="gpt-4o-mini",
            output_schema_id=str(uuid.uuid4()),
            validation_status="valid",
            repair_attempted=False,
            fallback_triggered=False,
        ),
    )


def _override_auth() -> AuthenticatedUser:
    """Override de l'authentification pour les tests."""
    return AuthenticatedUser(
        id=1,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def mock_db():
    mock = MagicMock()
    # Cache lookup path uses db.execute(...).scalars().all(); default to no cache hit.
    mock.execute.return_value.scalars.return_value.all.return_value = []
    # Persona lookup path still uses scalar_one_or_none().
    mock.execute.return_value.scalar_one_or_none.return_value = None
    return mock


@pytest.fixture
def test_client(mock_db):
    """Client de test avec dépendances mockées."""
    app.dependency_overrides[require_authenticated_user] = _override_auth
    app.dependency_overrides[get_db_session] = lambda: mock_db

    # Mock gate by default to avoid entitlement service side effects with mock_db
    from app.services.entitlement.natal_chart_long_entitlement_gate import (
        NatalChartLongEntitlementResult,
    )

    result = NatalChartLongEntitlementResult(
        path="canonical_unlimited", variant_code="single_astrologer"
    )

    with (
        patch(
            "app.api.v1.routers.public.natal_interpretation.NatalChartLongEntitlementGate.check_and_consume",
            return_value=result,
        ),
        patch(
            "app.services.entitlement.effective_entitlement_resolver_service."
            "EffectiveEntitlementResolverService.resolve_b2c_user_snapshot",
            return_value=MagicMock(plan_code="free"),
        ),
    ):
        client = TestClient(app)
        yield client
    app.dependency_overrides.clear()


class TestNatalInterpretationEndpointV2:
    """Tests pour POST /v1/natal/interpretation."""

    def test_short_success(self, test_client, mock_db) -> None:
        use_case = "natal_interpretation_short"
        # 1st call: cache check -> None (default from fixture)

        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
                new_callable=AsyncMock,
                return_value=_make_gateway_result(use_case),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation", json={"use_case_level": "short", "locale": "fr-FR"}
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["use_case"] == use_case
        assert data["interpretation"]["title"] == "Thème natal test"
        assert data["meta"]["level"] == "short"

    def test_complete_success(self, test_client, mock_db) -> None:
        use_case = "natal_interpretation"
        persona_id = str(uuid.uuid4())
        persona_mock = MagicMock()
        persona_mock.name = "Test Persona"
        persona_mock.description = "Test"
        persona_mock.tone = "warm"
        persona_mock.verbosity = "medium"
        persona_mock.style_markers = []
        persona_mock.boundaries = []
        persona_mock.allowed_topics = []

        mock_db.execute.return_value.scalar_one_or_none.return_value = persona_mock
        mock_db.get.return_value = persona_mock
        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
                new_callable=AsyncMock,
                return_value=_make_gateway_result(use_case, persona_id=persona_id),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation",
                json={
                    "use_case_level": "complete",
                    "persona_id": persona_id,
                    "question": "Quelle est ma mission de vie ?",
                },
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["use_case"] == use_case
        assert data["meta"]["level"] == "complete"
        assert data["meta"]["persona_name"] == "Test Persona"
        assert data["meta"]["persona_id"] == persona_id

    def test_complete_persona_missing(self, test_client, mock_db) -> None:
        # mock_db.execute.return_value.scalar_one_or_none.return_value = None (from fixture)
        from app.domain.llm.runtime.contracts import InputValidationError

        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.adapter.AIEngineAdapter.generate_natal_interpretation",
                side_effect=InputValidationError("Persona missing"),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation",
                json={"use_case_level": "complete", "persona_id": str(uuid.uuid4())},
            )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "natal_input_invalid"

    def test_chart_not_found(self, test_client) -> None:
        from app.services.user_profile.natal_chart_service import UserNatalChartServiceError

        with patch(
            "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
            side_effect=UserNatalChartServiceError(
                code="natal_chart_not_found", message="not found"
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation", json={"use_case_level": "short"}
            )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "natal_chart_not_found"

    def test_gateway_config_error(self, test_client, mock_db) -> None:
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
                side_effect=GatewayConfigError("Invalid gateway config"),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation", json={"use_case_level": "short"}
            )
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "gateway_config_error"

    def test_unknown_use_case(self, test_client, mock_db) -> None:
        from app.domain.llm.runtime.contracts import UnknownUseCaseError

        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
                side_effect=UnknownUseCaseError("Unknown use case"),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation", json={"use_case_level": "short"}
            )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "unknown_use_case"

    def test_upstream_timeout(self, test_client, mock_db) -> None:
        from app.domain.llm.runtime.errors import UpstreamTimeoutError

        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.domain.llm.runtime.gateway.LLMGateway.execute_request",
                side_effect=UpstreamTimeoutError("LLM Timeout"),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation", json={"use_case_level": "short"}
            )
        assert response.status_code == 504
        assert response.json()["error"]["code"] == "llm_upstream_timeout"

    def test_empty_complete_interpretation_returns_502(self, test_client, mock_db) -> None:
        persona_id = str(uuid.uuid4())
        persona_mock = MagicMock()
        persona_mock.name = "Test Persona"
        mock_db.execute.return_value.scalar_one_or_none.return_value = persona_mock

        with (
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.public.natal_interpretation.NatalInterpretationService.interpret",
                new_callable=AsyncMock,
                side_effect=RuntimeError("empty complete interpretation"),
            ),
        ):
            response = test_client.post(
                "/v1/natal/interpretation",
                json={
                    "use_case_level": "complete",
                    "persona_id": persona_id,
                    "locale": "fr-FR",
                },
            )

        assert response.status_code == 502
        assert response.json()["error"]["code"] == "interpretation_failed"

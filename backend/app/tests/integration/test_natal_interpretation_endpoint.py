"""Tests d'intégration pour les endpoints d'interprétation du thème natal."""

from __future__ import annotations

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
from app.infra.db.session import get_db_session
from app.main import app
from app.services.natal_interpretation_service import (
    NatalInterpretationData,
    NatalInterpretationMetadata,
    NatalInterpretationServiceError,
)
from app.services.user_astro_profile_service import UserAstroProfileServiceError
from app.services.user_birth_profile_service import UserBirthProfileData
from app.services.user_natal_chart_service import (
    UserNatalChartMetadata,
    UserNatalChartReadData,
)


def _make_natal_result() -> NatalResult:
    """Crée un NatalResult de test."""
    return NatalResult(
        reference_version="v1.0",
        ruleset_version="r1.0",
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
            HouseResult(number=4, cusp_longitude=285.2),
            HouseResult(number=7, cusp_longitude=15.5),
            HouseResult(number=10, cusp_longitude=105.3),
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
        birth_timezone="Europe/Paris",
    )


def _make_interpretation() -> NatalInterpretationData:
    """Crée un NatalInterpretationData de test."""
    return NatalInterpretationData(
        chart_id="chart-test-123",
        text="1. Synthèse\n2. Points clés\n3. Conseils\n4. Disclaimer",
        summary="Synthèse",
        key_points=["Point A", "Point B"],
        advice=["Conseil A"],
        disclaimer="Disclaimer important",
        metadata=NatalInterpretationMetadata(
            generated_at=datetime(2026, 2, 22, 10, 0, 0, tzinfo=timezone.utc),
            cached=False,
            degraded_mode=None,
            tokens_used=500,
            latency_ms=1200,
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


def _override_db() -> MagicMock:
    """Override de la session DB pour les tests."""
    return MagicMock()


@pytest.fixture
def test_client():
    """Client de test avec dépendances mockées."""
    app.dependency_overrides[require_authenticated_user] = _override_auth
    app.dependency_overrides[get_db_session] = _override_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    """Client de test sans authentification."""
    app.dependency_overrides[get_db_session] = _override_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _mock_astro_profile_service():
    """Évite les appels réels au calcul astro dans ce module de tests d'interprétation."""
    with patch(
        "app.api.v1.routers.users.UserAstroProfileService.get_for_user",
        side_effect=UserAstroProfileServiceError(
            code="astro_profile_unavailable",
            message="astro profile unavailable in test scope",
        ),
    ):
        yield


class TestGetMeNatalChartInterpretationAuth:
    """Tests d'authentification pour GET /v1/users/me/natal-chart/interpretation."""

    def test_unauthenticated_returns_401(self, unauthenticated_client) -> None:
        """Vérifie que l'endpoint retourne 401 sans authentification."""
        response = unauthenticated_client.get("/v1/users/me/natal-chart/interpretation")
        assert response.status_code == 401


class TestGetMeNatalChartInterpretation:
    """Tests pour GET /v1/users/me/natal-chart/interpretation."""

    def test_success(self, test_client) -> None:
        with (
            patch(
                "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.users.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.users.NatalInterpretationService.interpret_chart",
                new_callable=AsyncMock,
                return_value=_make_interpretation(),
            ),
        ):
            response = test_client.get("/v1/users/me/natal-chart/interpretation")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["chart_id"] == "chart-test-123"
        assert "summary" in data["data"]
        assert "key_points" in data["data"]
        assert "meta" in data

    def test_chart_not_found(self, test_client) -> None:
        from app.services.user_natal_chart_service import UserNatalChartServiceError

        with patch(
            "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
            side_effect=UserNatalChartServiceError(
                code="natal_chart_not_found",
                message="natal chart not found",
            ),
        ):
            response = test_client.get("/v1/users/me/natal-chart/interpretation")

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "natal_chart_not_found"

    def test_ai_engine_timeout(self, test_client) -> None:
        with (
            patch(
                "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.users.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.users.NatalInterpretationService.interpret_chart",
                new_callable=AsyncMock,
                side_effect=NatalInterpretationServiceError(
                    code="ai_engine_timeout",
                    message="AI Engine timeout",
                ),
            ),
        ):
            response = test_client.get("/v1/users/me/natal-chart/interpretation")

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "ai_engine_timeout"

    def test_rate_limit(self, test_client) -> None:
        with (
            patch(
                "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.users.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.users.NatalInterpretationService.interpret_chart",
                new_callable=AsyncMock,
                side_effect=NatalInterpretationServiceError(
                    code="rate_limit_exceeded",
                    message="Rate limit exceeded",
                ),
            ),
        ):
            response = test_client.get("/v1/users/me/natal-chart/interpretation")

        assert response.status_code == 429
        assert response.json()["error"]["code"] == "rate_limit_exceeded"


class TestGetMeLatestNatalChartWithInterpretation:
    """Tests pour GET /v1/users/me/natal-chart/latest avec include_interpretation."""

    def test_without_interpretation(self, test_client) -> None:
        with patch(
            "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
            return_value=_make_chart_read_data(),
        ):
            response = test_client.get("/v1/users/me/natal-chart/latest")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["interpretation"] is None

    def test_with_interpretation_calls_service(self, test_client) -> None:
        """Vérifie que le service d'interprétation est appelé avec include_interpretation=true."""
        mock_interpret = AsyncMock(return_value=_make_interpretation())

        with (
            patch(
                "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.users.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.users.NatalInterpretationService.interpret_chart",
                mock_interpret,
            ),
        ):
            response = test_client.get(
                "/v1/users/me/natal-chart/latest?include_interpretation=true"
            )

        assert response.status_code == 200
        mock_interpret.assert_called_once()
        call_args = mock_interpret.call_args
        assert call_args.kwargs["natal_chart"].chart_id == "chart-test-123"
        assert call_args.kwargs["user_id"] == 1

    def test_interpretation_error_graceful(self, test_client) -> None:
        with (
            patch(
                "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
                return_value=_make_chart_read_data(),
            ),
            patch(
                "app.api.v1.routers.users.UserBirthProfileService.get_for_user",
                return_value=_make_birth_profile(),
            ),
            patch(
                "app.api.v1.routers.users.NatalInterpretationService.interpret_chart",
                new_callable=AsyncMock,
                side_effect=NatalInterpretationServiceError(
                    code="ai_engine_timeout",
                    message="Timeout",
                ),
            ),
        ):
            response = test_client.get(
                "/v1/users/me/natal-chart/latest?include_interpretation=true"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["interpretation"] is None

    def test_include_interpretation_false(self, test_client) -> None:
        with patch(
            "app.api.v1.routers.users.UserNatalChartService.get_latest_for_user",
            return_value=_make_chart_read_data(),
        ):
            response = test_client.get(
                "/v1/users/me/natal-chart/latest?include_interpretation=false"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["interpretation"] is None

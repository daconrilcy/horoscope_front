# Commentaire global: garde de non-generation pour l'ancien endpoint natal public.
"""Verifie que POST /v1/natal/interpretation est readonly et non generateur."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app


def _override_auth() -> AuthenticatedUser:
    """Retourne un utilisateur public stable pour le test d'endpoint gone."""
    return AuthenticatedUser(
        id=1,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def test_client() -> TestClient:
    """Installe les overrides minimaux sans activer les services legacy."""
    app.dependency_overrides[require_authenticated_user] = _override_auth
    app.dependency_overrides[get_db_session] = lambda: MagicMock()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_old_public_endpoint_returns_410_with_replacement(test_client: TestClient) -> None:
    """L'ancien endpoint publie une erreur centralisee et le chemin de remplacement."""
    response = test_client.post(
        "/v1/natal/interpretation",
        json={"use_case_level": "short", "locale": "fr-FR"},
    )

    assert response.status_code == 410
    payload = response.json()
    assert payload["error"]["code"] == "natal_interpretation_endpoint_gone"
    assert payload["error"]["details"]["state"] == "readonly"
    assert payload["error"]["details"]["replacement"] == "/v1/theme-natal/readings"
    assert payload["error"]["details"]["chart_request_locale"] == "fr-FR"


def test_old_public_endpoint_does_not_call_generation_owners(test_client: TestClient) -> None:
    """Aucun owner chart, entitlement, gateway ou generation legacy n'est appele."""
    with (
        patch(
            "app.services.user_profile.natal_chart_service.UserNatalChartService.get_latest_for_user"
        ) as chart_mock,
        patch(
            "app.services.user_profile.birth_profile_service.UserBirthProfileService.get_for_user"
        ) as profile_mock,
        patch(
            "app.services.entitlement.natal_chart_long_entitlement_gate."
            "NatalChartLongEntitlementGate.check_access_for_complete_generation"
        ) as gate_mock,
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "NatalInterpretationService.interpret",
            new_callable=AsyncMock,
        ) as interpret_mock,
        patch("app.domain.llm.runtime.gateway.LLMGateway.execute_request") as gateway_mock,
    ):
        response = test_client.post(
            "/v1/natal/interpretation",
            json={"use_case_level": "complete", "locale": "fr-FR"},
        )

    assert response.status_code == 410
    chart_mock.assert_not_called()
    profile_mock.assert_not_called()
    gate_mock.assert_not_called()
    interpret_mock.assert_not_called()
    gateway_mock.assert_not_called()


def test_old_public_endpoint_openapi_documents_only_gone_response() -> None:
    """OpenAPI ne publie plus de schema de succes generateur sur l'ancien POST."""
    operation = app.openapi()["paths"]["/v1/natal/interpretation"]["post"]

    assert "200" not in operation["responses"]
    assert "410" in operation["responses"]
    assert "requestBody" not in operation

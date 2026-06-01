# Commentaire global: garde quota natal long apres neutralisation de l'ancien endpoint.
"""Verifie que POST /v1/natal/interpretation ne touche plus au quota legacy."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app

COMPLETE_PAYLOAD = {"use_case_level": "complete", "locale": "fr-FR"}
SHORT_PAYLOAD = {"use_case_level": "short", "locale": "fr-FR"}


def _override_auth() -> AuthenticatedUser:
    """Retourne l'utilisateur stable pour les preuves d'absence de debit quota."""
    return AuthenticatedUser(
        id=42,
        role="user",
        email="test-user@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def client() -> TestClient:
    """Installe une session mockee pour prouver qu'aucune transaction quota ne part."""
    app.dependency_overrides[require_authenticated_user] = _override_auth
    app.dependency_overrides[get_db_session] = lambda: MagicMock()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize("payload", [SHORT_PAYLOAD, COMPLETE_PAYLOAD])
def test_old_endpoint_returns_gone_before_quota_gate(
    client: TestClient,
    payload: dict[str, str],
) -> None:
    """Short et complete sortent en 410 sans gate entitlement."""
    with (
        patch(
            "app.services.entitlement.natal_chart_long_entitlement_gate."
            "NatalChartLongEntitlementGate.check_access_for_complete_generation"
        ) as check_mock,
        patch(
            "app.services.entitlement.natal_chart_long_entitlement_gate."
            "NatalChartLongEntitlementGate.consume_on_acceptance"
        ) as consume_mock,
        patch(
            "app.services.entitlement.natal_chart_long_entitlement_gate."
            "NatalChartLongEntitlementGate.release_corrective_regeneration_claim"
        ) as release_mock,
    ):
        response = client.post("/v1/natal/interpretation", json=payload)

    assert response.status_code == 410
    assert response.json()["error"]["details"]["state"] == "readonly"
    check_mock.assert_not_called()
    consume_mock.assert_not_called()
    release_mock.assert_not_called()


def test_old_endpoint_returns_gone_before_generation_service(client: TestClient) -> None:
    """L'ancien endpoint ne peut plus consommer un quota via retour accepte ou cache."""
    with patch(
        "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.interpret",
        new_callable=AsyncMock,
    ) as interpret_mock:
        response = client.post("/v1/natal/interpretation", json=COMPLETE_PAYLOAD)

    assert response.status_code == 410
    interpret_mock.assert_not_called()

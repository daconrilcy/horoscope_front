"""Tests d'integration du contrat public accepted-only theme natal."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal.theme_natal_basic_full_runtime import (
    ThemeNatalBasicFullReadingRuntime,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartMetadata,
    UserNatalChartReadData,
)
from app.tests.helpers.natal_result_factory import make_natal_result

TARGET_PATH = "/v1/theme-natal/readings"


@pytest.fixture
def client() -> TestClient:
    """Installe un client public authentifie sans dependre du cwd de pytest."""
    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_db_session] = lambda: MagicMock(spec=Session)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_public_read_action_exposes_only_accepted_payload(client: TestClient) -> None:
    """La route moderne expose le payload public seulement pour un run accepte."""
    accepted_result = SimpleNamespace(
        accepted=True,
        public_payload={
            "schema_version": "theme_natal_basic_full_public_v1",
            "title": "Lecture acceptee",
            "chapters": [{"key": "overall", "title": "Vue", "text": "Contenu public."}],
        },
        rejection_reason=None,
        decision=SimpleNamespace(
            status=SimpleNamespace(value="allowed"),
            reason_code=None,
            contract=SimpleNamespace(
                action=SimpleNamespace(value="generate_full"),
                output_variant=SimpleNamespace(value="basic_full_reading"),
            ),
        ),
    )
    rejected_result = SimpleNamespace(
        accepted=False,
        public_payload=None,
        rejection_reason={"code": "theme_natal_basic_provider_rejected", "raw": "secret"},
        decision=accepted_result.decision,
    )

    with (
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "UserNatalChartService.get_latest_for_user",
            return_value=_chart(),
        ),
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "NatalChartLongEntitlementGate.check_access_for_complete_generation",
            return_value=NatalChartLongEntitlementResult(
                path="canonical_quota",
                variant_code="single_astrologer",
                usage_states=[],
            ),
        ),
        patch.object(
            ThemeNatalBasicFullReadingRuntime,
            "generate",
            side_effect=[accepted_result, rejected_result],
        ),
    ):
        accepted_response = client.post(
            TARGET_PATH,
            json={
                "chart_id": "chart-public-read",
                "action": "generate_full",
                "locale": "fr-FR",
                "client_request_id": "accepted-public-read",
            },
        )
        rejected_response = client.post(
            TARGET_PATH,
            json={
                "chart_id": "chart-public-read",
                "action": "generate_full",
                "locale": "fr-FR",
                "client_request_id": "rejected-public-read",
            },
        )

    assert accepted_response.status_code == 200
    assert accepted_response.json()["state"] == "accepted"
    assert accepted_response.json()["data"]["title"] == "Lecture acceptee"
    assert rejected_response.status_code == 200
    assert rejected_response.json()["state"] == "rejected"
    assert rejected_response.json()["data"] is None
    assert "secret" not in str(rejected_response.json())


def _authenticated_user() -> AuthenticatedUser:
    """Retourne l'utilisateur public stable du contrat theme natal."""
    return AuthenticatedUser(
        id=435,
        role="user",
        email="cs-443-public-read@example.com",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )


def _chart() -> UserNatalChartReadData:
    """Construit un theme natal public correspondant a la commande de test."""
    return UserNatalChartReadData(
        chart_id="chart-public-read",
        result=make_natal_result(),
        metadata=UserNatalChartMetadata(reference_version="v1", ruleset_version="r1"),
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )

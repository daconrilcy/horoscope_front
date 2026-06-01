# Commentaire global: preuves d'integration de la surface publique product-action theme natal.
"""Valide le cutover public vers les actions produit de lecture theme natal."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.domain.theme_natal.product_action_resolver import resolve_theme_natal_reading_action
from app.domain.theme_natal.product_contract import (
    ThemeNatalEntitlementTier,
    ThemeNatalReadingAction,
    ThemeNatalReadingActionRequest,
    ThemeNatalReadingProductEntitlement,
)
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
    """Installe les overrides FastAPI minimaux pour les tests de contrat public."""
    app.dependency_overrides[require_authenticated_user] = _authenticated_user
    app.dependency_overrides[get_db_session] = lambda: MagicMock(spec=Session)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_runtime_route_and_openapi_expose_product_action_contract() -> None:
    """Le runtime FastAPI publie la route action-based et masque les anciens champs."""
    route_methods = {
        (getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", set()) or set())))
        for route in app.routes
    }
    openapi = app.openapi()

    assert (TARGET_PATH, ("POST",)) in route_methods
    assert TARGET_PATH in openapi["paths"]
    request_schema = openapi["paths"][TARGET_PATH]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    schema_name = request_schema["$ref"].rsplit("/", 1)[-1]
    properties = openapi["components"]["schemas"][schema_name]["properties"]

    assert {"chart_id", "action", "persona_profile_id", "locale", "client_request_id"} <= set(
        properties
    )
    assert "use_case" not in properties
    assert "use_case_level" not in properties
    assert "variant_code" not in properties
    assert "plan" not in properties
    assert "forceRefresh" not in properties


def test_generate_full_accepts_product_command_and_returns_accepted_slot(
    client: TestClient,
) -> None:
    """Basic generate_full passe par le runtime basic_full_reading et expose le slot accepte."""
    runtime_result = SimpleNamespace(
        accepted=True,
        public_payload={
            "schema_version": "theme_natal_basic_full_public_v1",
            "title": "Lecture Basic",
            "chapters": [],
        },
        rejection_reason=None,
        decision=_basic_decision(),
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
            return_value=runtime_result,
        ) as generate_mock,
    ):
        response = client.post(
            TARGET_PATH,
            json={
                "chart_id": "chart-product-action",
                "action": "generate_full",
                "locale": "fr-FR",
                "client_request_id": "client-request-432",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "accepted"
    assert payload["data"]["schema_version"] == "theme_natal_basic_full_public_v1"
    assert payload["details"]["output_variant"] == "basic_full_reading"
    assert "raw_provider_response" not in json.dumps(payload, ensure_ascii=False)
    runtime_request = generate_mock.call_args.kwargs["request"]
    assert runtime_request.client_request_id == "client-request-432"
    assert runtime_request.chart_id == "chart-product-action"


def test_preview_returns_controlled_state_without_short_generation(client: TestClient) -> None:
    """La preview Basic reste une decision produit et n'appelle aucun generateur short."""
    with (
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "UserNatalChartService.get_latest_for_user",
            return_value=_chart(),
        ),
        patch.object(ThemeNatalBasicFullReadingRuntime, "generate") as generate_mock,
        patch(
            "app.services.llm_generation.natal.interpretation_service."
            "NatalInterpretationService.interpret",
            new_callable=AsyncMock,
        ) as old_interpret_mock,
    ):
        response = client.post(
            TARGET_PATH,
            json={"chart_id": "chart-product-action", "action": "preview", "locale": "fr-FR"},
        )

    assert response.status_code == 200
    assert response.json()["state"] == "readonly"
    assert response.json()["data"] is None
    assert response.json()["details"]["output_variant"] == "free_preview"
    generate_mock.assert_not_called()
    old_interpret_mock.assert_not_called()


def test_new_route_rejects_legacy_generation_fields(client: TestClient) -> None:
    """Les anciens champs techniques sont rejetes par l'enveloppe d'erreur centralisee."""
    response = client.post(
        TARGET_PATH,
        json={
            "chart_id": "chart-product-action",
            "action": "generate_full",
            "locale": "fr-FR",
            "use_case": "natal_interpretation",
            "use_case_level": "complete",
            "variant_code": "single_astrologer",
            "plan": "basic",
            "forceRefresh": True,
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_request_payload"
    serialized_errors = json.dumps(payload["error"]["details"], ensure_ascii=False)
    for field_name in ("use_case", "use_case_level", "variant_code", "plan", "forceRefresh"):
        assert field_name in serialized_errors


def test_rejected_run_returns_controlled_state_without_provider_payload(
    client: TestClient,
) -> None:
    """Un run rejete reste un etat public controle sans fuite provider."""
    runtime_result = SimpleNamespace(
        accepted=False,
        public_payload=None,
        rejection_reason={
            "code": "theme_natal_basic_provider_rejected",
            "raw_provider_response": {"debug": "secret"},
        },
        decision=_basic_decision(),
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
        patch.object(ThemeNatalBasicFullReadingRuntime, "generate", return_value=runtime_result),
    ):
        response = client.post(
            TARGET_PATH,
            json={
                "chart_id": "chart-product-action",
                "action": "generate_full",
                "locale": "fr-FR",
                "client_request_id": "client-request-rejected",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "rejected"
    assert payload["data"] is None
    assert payload["details"]["reason_code"] == "theme_natal_basic_provider_rejected"
    assert "raw_provider_response" not in json.dumps(payload, ensure_ascii=False)
    assert "secret" not in json.dumps(payload, ensure_ascii=False)


def test_old_public_endpoint_is_non_generative(client: TestClient) -> None:
    """POST /v1/natal/interpretation renvoie 410 sans appeler l'ancien service generateur."""
    with patch(
        "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.interpret",
        new_callable=AsyncMock,
    ) as interpret_mock:
        response = client.post(
            "/v1/natal/interpretation",
            json={"use_case_level": "short", "locale": "fr-FR"},
        )

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "natal_interpretation_endpoint_gone"
    assert response.json()["error"]["details"]["state"] == "readonly"
    interpret_mock.assert_not_called()


def test_users_latest_include_interpretation_is_non_generative(client: TestClient) -> None:
    """Le flag historique include_interpretation est refuse sans appel provider legacy."""
    with patch(
        "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.interpret_chart",
        new_callable=AsyncMock,
    ) as interpret_chart_mock:
        response = client.get("/v1/users/me/natal-chart/latest?include_interpretation=true")

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "natal_interpretation_endpoint_gone"
    assert response.json()["error"]["details"]["replacement"] == "/v1/theme-natal/readings"
    interpret_chart_mock.assert_not_called()


def test_users_interpretation_endpoint_is_non_generative(client: TestClient) -> None:
    """L'ancien endpoint users d'interpretation renvoie 410 sans appeler le service legacy."""
    with patch(
        "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.interpret_chart",
        new_callable=AsyncMock,
    ) as interpret_chart_mock:
        response = client.get("/v1/users/me/natal-chart/interpretation")

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "natal_interpretation_endpoint_gone"
    assert response.json()["error"]["details"]["state"] == "readonly"
    interpret_chart_mock.assert_not_called()


def _authenticated_user() -> AuthenticatedUser:
    """Retourne l'utilisateur public stable des tests d'API."""
    return AuthenticatedUser(
        id=432,
        role="user",
        email="theme-natal-product-actions@example.com",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _chart() -> UserNatalChartReadData:
    """Construit le theme natal correspondant a la commande publique."""
    return UserNatalChartReadData(
        chart_id="chart-product-action",
        result=make_natal_result(),
        metadata=UserNatalChartMetadata(reference_version="v1", ruleset_version="r1"),
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _basic_decision() -> object:
    """Retourne la decision produit Basic attendue pour generate_full."""
    return resolve_theme_natal_reading_action(
        ThemeNatalReadingActionRequest(
            user_id=432,
            chart_id=432,
            action=ThemeNatalReadingAction.GENERATE_FULL,
            entitlement=ThemeNatalReadingProductEntitlement(
                tier=ThemeNatalEntitlementTier.BASIC,
                granted=True,
            ),
            locale="fr-FR",
        )
    )

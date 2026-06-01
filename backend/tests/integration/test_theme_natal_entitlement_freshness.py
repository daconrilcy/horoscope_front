# Commentaire global: preuves d'entitlement frais pour l'action Basic payante.
"""Verifie que generate_full utilise le gate Basic backend et ne retombe pas en Free."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.services.api_contracts.public.theme_natal_readings import (
    ThemeNatalReadingCommandRequest,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal.theme_natal_product_actions import (
    execute_theme_natal_reading_product_action,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartMetadata,
    UserNatalChartReadData,
)
from app.tests.helpers.natal_result_factory import make_natal_result


def test_paid_basic_generate_full_uses_fresh_basic_entitlement_without_free_plan_log(
    caplog,
) -> None:
    """Une action payante Basic transmet le resultat du gate au runtime sans plan=free."""
    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[],
    )
    runtime_result = SimpleNamespace(
        accepted=True,
        public_payload={"schema_version": "theme_natal_basic_full_public_v1"},
        rejection_reason=None,
        decision=SimpleNamespace(
            status=SimpleNamespace(value="generate_with_contract_key"),
            reason_code=None,
            contract=SimpleNamespace(
                action=SimpleNamespace(value="generate_full"),
                output_variant=SimpleNamespace(value="basic_full_reading"),
            ),
        ),
    )
    chart = UserNatalChartReadData(
        chart_id="chart-cs-435-entitlement",
        result=make_natal_result(),
        metadata=UserNatalChartMetadata(reference_version="v1", ruleset_version="r1"),
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )

    caplog.set_level(logging.INFO)
    with (
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "UserNatalChartService.get_latest_for_user",
            return_value=chart,
        ),
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "NatalChartLongEntitlementGate.check_access_for_complete_generation",
            return_value=access_result,
        ) as access_mock,
        patch(
            "app.services.llm_generation.natal.theme_natal_product_actions."
            "ThemeNatalBasicFullReadingRuntime.generate",
            return_value=runtime_result,
        ) as runtime_mock,
    ):
        response = execute_theme_natal_reading_product_action(
            MagicMock(spec=Session),
            user_id=435,
            command=ThemeNatalReadingCommandRequest(
                chart_id="chart-cs-435-entitlement",
                action="generate_full",
                locale="fr-FR",
                client_request_id="cs-435-entitlement-basic",
            ),
        )

    runtime_request = runtime_mock.call_args.kwargs["request"]
    assert response.state == "accepted"
    assert response.details["output_variant"] == "basic_full_reading"
    assert runtime_request.access_result is access_result
    assert runtime_request.access_result.variant_code == "single_astrologer"
    access_mock.assert_called_once()
    assert "plan=free" not in caplog.text

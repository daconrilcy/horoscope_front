# Commentaire global: preuves d'integration du runtime Basic full-reading fake provider.
"""Valide le chemin Basic theme natal sans provider live ni use case legacy."""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant
from app.infra.db.models.llm_generation_run import (
    LLM_GENERATION_RUN_STATUS_ACCEPTED,
    LLM_GENERATION_RUN_STATUS_REJECTED,
    LlmGenerationRunModel,
)
from app.infra.db.models.theme_natal_reading_slot import (
    THEME_NATAL_SLOT_STATUS_ACCEPTED,
    THEME_NATAL_SLOT_STATUS_REJECTED,
    ThemeNatalReadingSlotModel,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal.theme_natal_basic_full_runtime import (
    ThemeNatalBasicFullReadingRuntime,
    ThemeNatalBasicFullReadingRuntimeRequest,
    ThemeNatalFakeProviderMode,
    build_contractual_theme_natal_free_preview,
)
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)
from app.tests.helpers.natal_result_factory import make_natal_result

RUNTIME_PATH = (
    Path(__file__).resolve().parents[2]
    / "app/services/llm_generation/natal/theme_natal_basic_full_runtime.py"
)
CONTRACT_KEY = "theme_natal.reading.basic_full_reading.v1"
INVALID_MODES = (
    ThemeNatalFakeProviderMode.INVALID_JSON,
    ThemeNatalFakeProviderMode.UNKNOWN_FIELD,
    ThemeNatalFakeProviderMode.EMPTY_SOURCE,
    ThemeNatalFakeProviderMode.INVENTED_FACT,
    ThemeNatalFakeProviderMode.TECHNICAL_LEAK,
    ThemeNatalFakeProviderMode.MECHANICAL_PHRASE,
    ThemeNatalFakeProviderMode.ASTROLOGICAL_CONTRADICTION,
    ThemeNatalFakeProviderMode.SHORT_SECTION,
)


def _request(
    *,
    chart_id: str = "chart-basic-runtime",
    client_request_id: str = "client-basic-runtime",
    mode: ThemeNatalFakeProviderMode = ThemeNatalFakeProviderMode.VALID,
    access_result: NatalChartLongEntitlementResult | None = None,
) -> ThemeNatalBasicFullReadingRuntimeRequest:
    """Construit une requete Basic runtime stable pour les tests."""
    return ThemeNatalBasicFullReadingRuntimeRequest(
        user_id=430,
        chart_id=chart_id,
        chart_numeric_id=430,
        locale="fr-FR",
        client_request_id=client_request_id,
        provider_mode=mode,
        access_result=access_result,
    )


def _slot_key(chart_id: str) -> ThemeNatalReadingSlotKey:
    """Retourne la cle publique attendue pour le runtime Basic."""
    return ThemeNatalReadingSlotKey(
        user_id=430,
        chart_id=chart_id,
        product_plan="basic",
        output_variant=ThemeNatalOutputVariant.BASIC_FULL_READING,
        contract_version=CONTRACT_KEY,
    )


def _count_runs(db: Session) -> int:
    """Compte les runs techniques dans la session d'integration."""
    return db.execute(select(func.count()).select_from(LlmGenerationRunModel)).scalar_one()


def test_basic_generate_full_accepts_fake_provider_and_persists_public_slot(
    db: Session,
) -> None:
    """Le chemin Basic accepte le fake valide, persiste run/slot et debite apres acceptation."""
    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[],
    )
    slot_key = _slot_key("chart-basic-runtime-accepted")

    def consume_after_publication(
        db_arg: Session,
        *,
        user_id: int,
        access_result: NatalChartLongEntitlementResult,
    ) -> NatalChartLongEntitlementResult:
        persisted = ThemeNatalReadingSlotService.get_public_slot_by_key(db_arg, key=slot_key)
        assert persisted is not None
        assert persisted.status == THEME_NATAL_SLOT_STATUS_ACCEPTED
        return access_result

    with patch(
        "app.services.entitlement.natal_chart_long_entitlement_gate."
        "NatalChartLongEntitlementGate.consume_on_acceptance",
        side_effect=consume_after_publication,
    ) as quota_mock:
        result = ThemeNatalBasicFullReadingRuntime().generate(
            db,
            natal_result=make_natal_result(),
            request=_request(chart_id=slot_key.chart_id, access_result=access_result),
        )

    assert result.accepted is True
    assert result.cached is False
    assert result.decision.contract is not None
    assert result.decision.contract.contract_key == CONTRACT_KEY
    assert result.generation_contract_key == CONTRACT_KEY
    assert result.generation_contract_hash
    assert result.generation_contract_snapshot_id.startswith(CONTRACT_KEY)
    assert result.prompt_payload["sections"]
    assert result.public_payload is not None
    assert result.public_payload["schema_version"] == "theme_natal_basic_full_public_v1"
    assert "raw_provider_response" not in result.public_payload
    assert "parsed_raw_response" not in result.public_payload
    assert "provider_mode" not in result.public_payload

    run = db.get(LlmGenerationRunModel, result.run_id)
    slot = db.get(ThemeNatalReadingSlotModel, result.slot_id)
    assert run is not None
    assert slot is not None
    assert run.status == LLM_GENERATION_RUN_STATUS_ACCEPTED
    assert run.generation_contract_key == CONTRACT_KEY
    assert run.generation_contract_hash == result.generation_contract_hash
    assert run.generation_contract_snapshot_id == result.generation_contract_snapshot_id
    assert run.provider_mode == ThemeNatalFakeProviderMode.VALID.value
    assert run.output_schema_version == "theme_natal.output_contract.v1"
    assert run.data_hash == result.data_hash
    assert run.raw_provider_response is not None
    assert run.raw_provider_response["provider"] == "fake_provider"
    assert slot.status == THEME_NATAL_SLOT_STATUS_ACCEPTED
    assert slot.public_payload == result.public_payload
    quota_mock.assert_called_once()


@pytest.mark.parametrize("mode", INVALID_MODES)
def test_basic_fake_provider_invalid_modes_are_rejected_before_public_projection(
    db: Session,
    mode: ThemeNatalFakeProviderMode,
) -> None:
    """Chaque mode fake invalide reste technique et n'alimente aucun payload public."""
    chart_id = f"chart-basic-runtime-{mode.value}"
    with patch(
        "app.services.entitlement.natal_chart_long_entitlement_gate."
        "NatalChartLongEntitlementGate.consume_on_acceptance"
    ) as quota_mock:
        result = ThemeNatalBasicFullReadingRuntime().generate(
            db,
            natal_result=make_natal_result(),
            request=_request(
                chart_id=chart_id,
                client_request_id=f"client-{mode.value}",
                mode=mode,
                access_result=NatalChartLongEntitlementResult(
                    path="canonical_quota",
                    variant_code="single_astrologer",
                    usage_states=[],
                ),
            ),
        )

    public_slot = ThemeNatalReadingSlotService.get_public_slot_by_key(db, key=_slot_key(chart_id))
    run = db.get(LlmGenerationRunModel, result.run_id)
    slot = db.get(ThemeNatalReadingSlotModel, result.slot_id)

    assert result.accepted is False
    assert result.public_payload is None
    assert result.rejection_reason is not None
    assert result.rejection_reason["code"] == "theme_natal_basic_provider_rejected"
    assert result.rejection_reason["provider_mode"] == mode.value
    assert result.rejection_reason["contract_reason"]
    assert public_slot is None
    assert run is not None
    assert run.status == LLM_GENERATION_RUN_STATUS_REJECTED
    assert run.provider_mode == mode.value
    assert run.validation_errors
    assert slot is not None
    assert slot.status == THEME_NATAL_SLOT_STATUS_REJECTED
    quota_mock.assert_not_called()


def test_basic_runtime_is_idempotent_for_same_logical_request(db: Session) -> None:
    """Une demande deja acceptee relit le slot public sans nouveau run ni debit quota."""
    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[],
    )
    runtime = ThemeNatalBasicFullReadingRuntime()
    run_count_before = _count_runs(db)

    with patch(
        "app.services.entitlement.natal_chart_long_entitlement_gate."
        "NatalChartLongEntitlementGate.consume_on_acceptance",
        return_value=access_result,
    ) as quota_mock:
        first = runtime.generate(
            db,
            natal_result=make_natal_result(),
            request=_request(
                chart_id="chart-basic-runtime-idempotent",
                client_request_id="client-idempotent",
                access_result=access_result,
            ),
        )
        second = runtime.generate(
            db,
            natal_result=make_natal_result(),
            request=_request(
                chart_id="chart-basic-runtime-idempotent",
                client_request_id="client-idempotent",
                mode=ThemeNatalFakeProviderMode.INVALID_JSON,
                access_result=access_result,
            ),
        )

    assert first.accepted is True
    assert second.accepted is True
    assert second.cached is True
    assert second.slot_id == first.slot_id
    assert second.run_id == first.run_id
    assert second.public_payload == first.public_payload
    assert _count_runs(db) == run_count_before + 1
    quota_mock.assert_called_once()


def test_basic_runtime_rejected_idempotency_key_keeps_terminal_run(db: Session) -> None:
    """Une cle client deja rejetee conserve son audit et ne republie pas en Basic."""
    runtime = ThemeNatalBasicFullReadingRuntime()
    chart_id = "chart-basic-runtime-rejected-idempotent"
    client_request_id = "client-rejected-idempotent"
    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[],
    )

    first = runtime.generate(
        db,
        natal_result=make_natal_result(),
        request=_request(
            chart_id=chart_id,
            client_request_id=client_request_id,
            mode=ThemeNatalFakeProviderMode.INVALID_JSON,
            access_result=access_result,
        ),
    )
    original_run = db.get(LlmGenerationRunModel, first.run_id)
    assert original_run is not None
    original_raw_provider_response = dict(original_run.raw_provider_response or {})

    with patch(
        "app.services.entitlement.natal_chart_long_entitlement_gate."
        "NatalChartLongEntitlementGate.consume_on_acceptance"
    ) as quota_mock:
        second = runtime.generate(
            db,
            natal_result=make_natal_result(),
            request=_request(
                chart_id=chart_id,
                client_request_id=client_request_id,
                mode=ThemeNatalFakeProviderMode.VALID,
                access_result=access_result,
            ),
        )

    public_slot = ThemeNatalReadingSlotService.get_public_slot_by_key(db, key=_slot_key(chart_id))
    persisted_run = db.get(LlmGenerationRunModel, first.run_id)

    assert second.accepted is False
    assert second.cached is True
    assert second.run_id == first.run_id
    assert second.provider_mode == ThemeNatalFakeProviderMode.INVALID_JSON
    assert public_slot is None
    assert persisted_run is not None
    assert persisted_run.status == LLM_GENERATION_RUN_STATUS_REJECTED
    assert persisted_run.provider_mode == ThemeNatalFakeProviderMode.INVALID_JSON.value
    assert persisted_run.raw_provider_response == original_raw_provider_response
    assert _count_runs(db) == 1
    quota_mock.assert_not_called()


def test_free_preview_traversal_uses_contractual_fake_projection() -> None:
    """La preview Free de parcours reste contractuelle et sans appel natal_long_free."""
    preview = build_contractual_theme_natal_free_preview()

    assert preview["schema_version"] == "theme_natal_free_preview_public_v1"
    assert preview["highlights"]
    assert "raw_provider_response" not in preview


def test_basic_runtime_ast_guard_does_not_call_legacy_natal_use_cases() -> None:
    """Le runtime Basic ne reference pas les anciens use cases generation natale."""
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_names = {
        "natal_interpretation",
        "natal_interpretation_short",
        "natal_long_free",
        "generate_" + "natal_interpretation",
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    called_attrs = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert forbidden_names.isdisjoint(called_names)
    assert forbidden_names.isdisjoint(called_attrs)
    assert "natal_long_free" not in source
    assert "natal_interpretation_short" not in source

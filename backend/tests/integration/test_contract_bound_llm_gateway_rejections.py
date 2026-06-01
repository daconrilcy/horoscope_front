# Commentaire global: preuves integration des rejets gateway et de la frontiere publique.
"""Verifie que les rejets contractuels restent dans les runs techniques."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant
from app.infra.db.models.llm_generation_run import (
    LLM_GENERATION_RUN_STATUS_ACCEPTED,
    LLM_GENERATION_RUN_STATUS_REJECTED,
    LlmGenerationRunModel,
)
from app.services.llm_generation.natal.theme_natal_basic_full_runtime import (
    ThemeNatalBasicFullReadingRuntime,
    ThemeNatalBasicFullReadingRuntimeRequest,
    ThemeNatalFakeProviderMode,
)
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)
from app.tests.helpers.natal_result_factory import make_natal_result

CONTRACT_KEY = "theme_natal.reading.basic_full_reading.v1"


def test_contract_bound_rejection_is_persisted_only_as_generation_run(db: Session) -> None:
    """Un rejet contractuel cree un run rejete sans payload public accepted-only."""
    result = ThemeNatalBasicFullReadingRuntime().generate(
        db,
        natal_result=make_natal_result(),
        request=_request(
            chart_id="contract-bound-rejected-only",
            client_request_id="contract-bound-rejected-only",
            mode=ThemeNatalFakeProviderMode.TECHNICAL_LEAK,
        ),
    )

    run = db.get(LlmGenerationRunModel, result.run_id)
    public_slot = ThemeNatalReadingSlotService.get_public_slot_by_key(
        db,
        key=_slot_key("contract-bound-rejected-only"),
    )

    assert result.accepted is False
    assert public_slot is None
    assert run is not None
    assert run.status == LLM_GENERATION_RUN_STATUS_REJECTED
    assert run.rejection_reason is not None
    assert run.rejection_reason["contract_reason"]["category"] == "contract_policy_rejection"
    assert run.parsed_raw_response is None


def test_contract_bound_runs_log_contract_versions_and_hashes(db: Session) -> None:
    """Les versions et hash du snapshot restent auditables dans llm_generation_runs."""
    result = ThemeNatalBasicFullReadingRuntime().generate(
        db,
        natal_result=make_natal_result(),
        request=_request(
            chart_id="contract-bound-metadata",
            client_request_id="contract-bound-metadata",
            mode=ThemeNatalFakeProviderMode.ASTROLOGICAL_CONTRADICTION,
        ),
    )

    run = db.get(LlmGenerationRunModel, result.run_id)

    assert run is not None
    assert run.generation_contract_key == CONTRACT_KEY
    assert run.generation_contract_hash == result.generation_contract_hash
    assert run.generation_contract_snapshot_id == result.generation_contract_snapshot_id
    assert run.engine_profile_version == "theme_natal.engine.basic_full_reading.v1"
    assert run.output_schema_version == "theme_natal.output_contract.v1"
    assert run.raw_provider_response is not None

    metadata = run.raw_provider_response["contract_metadata"]
    assert metadata["generation_contract_key"] == CONTRACT_KEY
    assert metadata["generation_contract_hash"] == result.generation_contract_hash
    assert metadata["generation_contract_version"] == "1.0.0"
    assert metadata["prompt_contract_version"] == "theme_natal.prompt.basic_full_reading.v1"
    assert metadata["data_contract_version"] == "theme_natal.data.basic_full_reading.v1"
    assert metadata["engine_profile_version"] == "theme_natal.engine.basic_full_reading.v1"


def test_public_slot_listing_remains_accepted_only_after_rejected_attempt(
    db: Session,
) -> None:
    """La liste publique ignore les slots rejetes et relit seulement les lectures acceptees."""
    runtime = ThemeNatalBasicFullReadingRuntime()
    rejected = runtime.generate(
        db,
        natal_result=make_natal_result(),
        request=_request(
            chart_id="contract-bound-public-rejected",
            client_request_id="contract-bound-public-rejected",
            mode=ThemeNatalFakeProviderMode.INVENTED_FACT,
        ),
    )
    accepted = runtime.generate(
        db,
        natal_result=make_natal_result(),
        request=_request(
            chart_id="contract-bound-public-accepted",
            client_request_id="contract-bound-public-accepted",
            mode=ThemeNatalFakeProviderMode.VALID,
        ),
    )

    public_slots, total = ThemeNatalReadingSlotService.list_public_slots(db, user_id=431)
    runs = db.execute(select(LlmGenerationRunModel)).scalars().all()

    assert rejected.accepted is False
    assert accepted.accepted is True
    assert total == 1
    assert [slot.chart_id for slot in public_slots] == ["contract-bound-public-accepted"]
    assert {run.status for run in runs} == {
        LLM_GENERATION_RUN_STATUS_ACCEPTED,
        LLM_GENERATION_RUN_STATUS_REJECTED,
    }


def _request(
    *,
    chart_id: str,
    client_request_id: str,
    mode: ThemeNatalFakeProviderMode,
) -> ThemeNatalBasicFullReadingRuntimeRequest:
    return ThemeNatalBasicFullReadingRuntimeRequest(
        user_id=431,
        chart_id=chart_id,
        chart_numeric_id=431,
        locale="fr-FR",
        client_request_id=client_request_id,
        provider_mode=mode,
    )


def _slot_key(chart_id: str) -> ThemeNatalReadingSlotKey:
    return ThemeNatalReadingSlotKey(
        user_id=431,
        chart_id=chart_id,
        product_plan="basic",
        output_variant=ThemeNatalOutputVariant.BASIC_FULL_READING,
        contract_version=CONTRACT_KEY,
    )

# Commentaire global: preuves replay Free vers Basic du Big Bang theme natal.
"""Verifie le replay contractuel Free preview puis Basic full reading."""

from __future__ import annotations

from collections import Counter
from unittest.mock import patch

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant
from app.infra.db.models.llm_generation_run import LlmGenerationRunModel
from app.infra.db.models.theme_natal_reading_slot import (
    THEME_NATAL_SLOT_STATUS_ACCEPTED,
    ThemeNatalReadingSlotModel,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal.theme_natal_basic_full_runtime import (
    ThemeNatalBasicFullReadingRuntime,
    ThemeNatalBasicFullReadingRuntimeRequest,
    build_contractual_theme_natal_free_preview,
)
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)
from app.tests.helpers.natal_result_factory import make_natal_result

USER_ID = 435
CHART_ID = "chart-cs-435-replay"
FREE_CONTRACT = "theme_natal.reading.free_preview.v1"
BASIC_CONTRACT = "theme_natal.reading.basic_full_reading.v1"


def test_free_to_basic_replay_persists_one_preview_and_one_basic_full_reading(
    db: Session,
) -> None:
    """Le replay public cree au plus un slot Free et un slot Basic accepte par chart."""
    free_key = ThemeNatalReadingSlotKey(
        user_id=USER_ID,
        chart_id=CHART_ID,
        product_plan="free",
        output_variant=ThemeNatalOutputVariant.FREE_PREVIEW,
        contract_version=FREE_CONTRACT,
    )
    free_claim = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=free_key,
        client_request_id="cs-435-free-preview-1",
        generation_contract_key=FREE_CONTRACT,
        generation_contract_hash="free-preview-contract-hash",
        generation_contract_snapshot_id=f"{FREE_CONTRACT}:snapshot",
        output_schema_version="theme_natal_free_preview_public_v1",
        data_hash="free-preview-data-hash",
    )
    ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=free_claim.run.id,
        public_payload=build_contractual_theme_natal_free_preview(),
    )
    second_free_claim = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=free_key,
        client_request_id="cs-435-free-preview-2",
    )

    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[],
    )
    with patch(
        "app.services.entitlement.natal_chart_long_entitlement_gate."
        "NatalChartLongEntitlementGate.consume_on_acceptance",
        return_value=access_result,
    ) as quota_mock:
        basic_result = ThemeNatalBasicFullReadingRuntime().generate(
            db,
            natal_result=make_natal_result(),
            request=ThemeNatalBasicFullReadingRuntimeRequest(
                user_id=USER_ID,
                chart_id=CHART_ID,
                chart_numeric_id=435,
                locale="fr-FR",
                client_request_id="cs-435-basic-full-1",
                access_result=access_result,
            ),
        )

    slots = list(
        db.execute(
            select(ThemeNatalReadingSlotModel).where(
                ThemeNatalReadingSlotModel.user_id == USER_ID,
                ThemeNatalReadingSlotModel.chart_id == CHART_ID,
                ThemeNatalReadingSlotModel.status == THEME_NATAL_SLOT_STATUS_ACCEPTED,
            )
        )
        .scalars()
        .all()
    )
    grouped = Counter((slot.chart_id, slot.output_variant) for slot in slots)
    basic_run = db.get(LlmGenerationRunModel, basic_result.run_id)

    assert second_free_claim.slot.id == free_claim.slot.id
    assert grouped[(CHART_ID, ThemeNatalOutputVariant.FREE_PREVIEW.value)] == 1
    assert grouped[(CHART_ID, ThemeNatalOutputVariant.BASIC_FULL_READING.value)] == 1
    assert basic_result.accepted is True
    assert basic_result.generation_contract_key == BASIC_CONTRACT
    assert basic_result.generation_contract_hash
    assert basic_result.data_hash
    assert basic_result.public_payload is not None
    assert basic_result.public_payload["schema_version"] == "theme_natal_basic_full_public_v1"
    assert basic_run is not None
    assert basic_run.generation_contract_key == BASIC_CONTRACT
    assert basic_run.generation_contract_hash == basic_result.generation_contract_hash
    assert basic_run.output_schema_version == "theme_natal.output_contract.v1"
    assert basic_run.data_hash == basic_result.data_hash
    quota_mock.assert_called_once()

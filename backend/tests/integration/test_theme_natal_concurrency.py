# Commentaire global: preuves de concurrence du slot public Basic theme natal.
"""Verifie que deux generate_full ne publient pas deux lectures publiques."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant
from app.infra.db.models.theme_natal_reading_slot import ThemeNatalReadingSlotModel
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)
from app.services.llm_generation.natal import theme_natal_reading_slots as slot_module
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)

USER_ID = 435
CHART_ID = "chart-cs-435-concurrency"
CONTRACT_VERSION = "theme_natal.reading.basic_full_reading.v1"


def _slot_key() -> ThemeNatalReadingSlotKey:
    """Retourne la cle Basic partagee par les clics concurrents."""
    return ThemeNatalReadingSlotKey(
        user_id=USER_ID,
        chart_id=CHART_ID,
        product_plan="basic",
        output_variant=ThemeNatalOutputVariant.BASIC_FULL_READING,
        contract_version=CONTRACT_VERSION,
    )


def test_concurrent_generate_full_attempts_share_one_slot_and_one_public_acceptance(
    db: Session,
) -> None:
    """Deux tentatives du meme produit gardent un seul payload accepted et un seul debit quota."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="cs-435-generate-full-a",
    )
    second = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="cs-435-generate-full-b",
    )
    first_publication = ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=first.run.id,
        public_payload={"schema_version": "theme_natal_basic_full_public_v1", "title": "A"},
    )
    second_publication = ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=second.run.id,
        public_payload={"schema_version": "theme_natal_basic_full_public_v1", "title": "B"},
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
        debit_first = ThemeNatalReadingSlotService.consume_quota_after_publication(
            db,
            user_id=USER_ID,
            access_result=access_result,
            publication=first_publication,
        )
        debit_second = ThemeNatalReadingSlotService.consume_quota_after_publication(
            db,
            user_id=USER_ID,
            access_result=access_result,
            publication=second_publication,
        )

    slots = list(
        db.execute(
            select(ThemeNatalReadingSlotModel).where(
                ThemeNatalReadingSlotModel.user_id == USER_ID,
                ThemeNatalReadingSlotModel.chart_id == CHART_ID,
            )
        )
        .scalars()
        .all()
    )

    assert first.slot.id == second.slot.id
    assert first_publication.accepted_now is True
    assert second_publication.accepted_now is False
    assert len(slots) == 1
    assert slots[0].public_payload == {
        "schema_version": "theme_natal_basic_full_public_v1",
        "title": "A",
    }
    assert debit_first is access_result
    assert debit_second is None
    quota_mock.assert_called_once()


def test_slot_claim_section_is_serialized_for_simultaneous_generate_full(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le verrou applicatif interdit deux claims actifs du meme slot."""
    start = Barrier(2)
    active_guard = Lock()
    active_claims = 0
    max_active_claims = 0

    def fake_get_or_create_slot(
        db: Session,
        key: ThemeNatalReadingSlotKey,
    ) -> tuple[SimpleNamespace, bool]:
        nonlocal active_claims, max_active_claims
        with active_guard:
            active_claims += 1
            max_active_claims = max(max_active_claims, active_claims)
        time.sleep(0.05)
        with active_guard:
            active_claims -= 1
        return SimpleNamespace(id=435), False

    def fake_get_or_create_generation_run(
        db: Session,
        *,
        slot_id: int,
        client_request_id: str,
        prompt_hash: str | None,
        data_hash: str | None,
        engine_profile_version: str | None,
        output_schema_version: str | None,
        generation_contract_key: str | None,
        generation_contract_hash: str | None,
        generation_contract_snapshot_id: str | None,
        provider_mode: str | None,
    ) -> tuple[SimpleNamespace, bool]:
        return SimpleNamespace(id=client_request_id, slot_id=slot_id), True

    def claim(client_request_id: str) -> None:
        start.wait(timeout=2)
        ThemeNatalReadingSlotService.claim_generation_run(
            MagicMock(),
            key=_slot_key(),
            client_request_id=client_request_id,
        )

    monkeypatch.setattr(slot_module, "_get_or_create_slot", fake_get_or_create_slot)
    monkeypatch.setattr(
        slot_module,
        "_get_or_create_generation_run",
        fake_get_or_create_generation_run,
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(claim, "cs-435-concurrent-a"),
            executor.submit(claim, "cs-435-concurrent-b"),
        ]
        for future in futures:
            future.result(timeout=2)

    assert max_active_claims == 1

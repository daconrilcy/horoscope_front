# Commentaire global: tests d'integration des slots publics theme natal et runs LLM.
"""Prouve l'idempotence SQLite et la frontiere accepted-only des slots publics."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from app.domain.theme_natal.product_contract import ThemeNatalOutputVariant
from app.infra.db.models.llm_generation_run import LlmGenerationRunModel
from app.infra.db.models.theme_natal_reading_slot import (
    THEME_NATAL_SLOT_STATUS_ACCEPTED,
    THEME_NATAL_SLOT_STATUS_GENERATING,
    ThemeNatalReadingSlotModel,
)
from app.services.llm_generation.natal.theme_natal_reading_slots import (
    ThemeNatalReadingSlotKey,
    ThemeNatalReadingSlotService,
)


def _slot_key(
    *,
    chart_id: str = "chart-theme-natal-1",
    output_variant: ThemeNatalOutputVariant = ThemeNatalOutputVariant.BASIC_FULL_READING,
) -> ThemeNatalReadingSlotKey:
    """Construit une cle produit stable pour les tests de slots."""
    return ThemeNatalReadingSlotKey(
        user_id=428,
        chart_id=chart_id,
        product_plan="basic",
        output_variant=output_variant,
        contract_version="theme_natal.reading.basic_full_reading.v1",
    )


def _count_slots(db: Session) -> int:
    """Compte les slots publics crees dans la session de test."""
    return db.execute(select(func.count()).select_from(ThemeNatalReadingSlotModel)).scalar_one()


def _count_runs(db: Session) -> int:
    """Compte les runs LLM techniques crees dans la session de test."""
    return db.execute(select(func.count()).select_from(LlmGenerationRunModel)).scalar_one()


def test_theme_natal_slot_schema_exposes_public_and_run_contract(db: Session) -> None:
    """Le schema separe slot public et run LLM avec les contraintes attendues."""
    inspector = inspect(db.bind)

    slot_columns = {column["name"] for column in inspector.get_columns("theme_natal_reading_slots")}
    run_columns = {column["name"] for column in inspector.get_columns("llm_generation_runs")}
    slot_indexes = {
        index["name"]: index for index in inspector.get_indexes("theme_natal_reading_slots")
    }
    run_indexes = {index["name"]: index for index in inspector.get_indexes("llm_generation_runs")}

    assert {
        "user_id",
        "chart_id",
        "feature",
        "reading_kind",
        "product_plan",
        "output_variant",
        "persona_profile_id",
        "contract_version",
        "status",
        "public_payload",
        "accepted_at",
        "source_generation_run_id",
        "created_at",
    } <= slot_columns
    assert {
        "slot_id",
        "client_request_id",
        "status",
        "raw_provider_response",
        "parsed_raw_response",
        "validation_errors",
        "rejection_reason",
        "prompt_hash",
        "data_hash",
        "engine_profile_version",
        "output_schema_version",
    } <= run_columns
    assert slot_indexes["uq_theme_natal_reading_slots_null_persona"]["unique"] == 1
    assert "chart_id" in slot_indexes["uq_theme_natal_reading_slots_null_persona"]["column_names"]
    assert "chart_id" in slot_indexes["uq_theme_natal_reading_slots_with_persona"]["column_names"]
    assert run_indexes["uq_llm_generation_runs_slot_client_request"]["unique"] == 1


def test_theme_natal_slot_reuses_run_for_same_client_request_id(db: Session) -> None:
    """Une meme idempotency key retourne le meme slot et le meme run."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-428",
    )
    second = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-428",
    )

    assert first.created_slot is True
    assert first.created_run is True
    assert second.created_slot is False
    assert second.created_run is False
    assert second.slot.id == first.slot.id
    assert second.run.id == first.run.id
    assert _count_slots(db) == 1
    assert _count_runs(db) == 1


def test_theme_natal_slot_unique_key_includes_chart_id(db: Session) -> None:
    """Deux charts differents ne partagent pas le meme slot public."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(chart_id="chart-theme-natal-a"),
        client_request_id="client-request-a",
    )
    second = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(chart_id="chart-theme-natal-b"),
        client_request_id="client-request-b",
    )

    assert first.slot.id != second.slot.id
    assert _count_slots(db) == 2


def test_theme_natal_slot_claims_share_product_slot_without_same_client_id(
    db: Session,
) -> None:
    """Deux demandes du meme produit restent protegees par l'unicite du slot."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-first",
    )
    second = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-second",
    )

    assert first.slot.id == second.slot.id
    assert first.run.id != second.run.id
    assert second.slot.status == THEME_NATAL_SLOT_STATUS_GENERATING
    assert _count_slots(db) == 1
    assert _count_runs(db) == 2


def test_theme_natal_slot_public_get_and_list_return_accepted_only(db: Session) -> None:
    """Les lectures publiques ignorent les slots non acceptes et les runs rejetes."""
    hidden = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(chart_id="chart-hidden"),
        client_request_id="client-request-hidden",
    )
    accepted = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(chart_id="chart-accepted"),
        client_request_id="client-request-accepted",
    )
    ThemeNatalReadingSlotService.record_rejected_run(
        db,
        run_id=hidden.run.id,
        rejection_reason={"code": "provider_rejected"},
    )
    ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=accepted.run.id,
        public_payload={"title": "Lecture acceptee"},
    )

    rows, total = ThemeNatalReadingSlotService.list_public_slots(db, user_id=428)
    hidden_lookup = ThemeNatalReadingSlotService.get_public_slot_by_key(
        db,
        key=_slot_key(chart_id="chart-hidden"),
    )
    accepted_lookup = ThemeNatalReadingSlotService.get_public_slot_by_key(
        db,
        key=_slot_key(chart_id="chart-accepted"),
    )

    assert total == 1
    assert [row.id for row in rows] == [accepted.slot.id]
    assert hidden_lookup is None
    assert accepted_lookup is not None
    assert accepted_lookup.status == THEME_NATAL_SLOT_STATUS_ACCEPTED


def test_theme_natal_slot_rejected_run_does_not_replace_accepted_payload(
    db: Session,
) -> None:
    """Une regeneration rejetee conserve le payload public et accepted_at existants."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-accepted",
    )
    accepted_time = datetime(2026, 6, 1, 10, 30, tzinfo=timezone.utc)
    publication = ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=first.run.id,
        public_payload={"title": "Payload public stable"},
        accepted_at=accepted_time,
    )
    created_at = publication.slot.created_at
    accepted_at = publication.slot.accepted_at

    retry = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-rejected",
    )
    ThemeNatalReadingSlotService.record_rejected_run(
        db,
        run_id=retry.run.id,
        raw_provider_response={"raw": "technique"},
        parsed_raw_response={"status": "rejected"},
        validation_errors=[{"code": "semantic_rejection"}],
        rejection_reason={"code": "semantic_rejection"},
    )
    public_slot = ThemeNatalReadingSlotService.get_public_slot_by_key(db, key=_slot_key())

    assert public_slot is not None
    assert public_slot.public_payload == {"title": "Payload public stable"}
    assert public_slot.accepted_at == accepted_at
    assert public_slot.created_at == created_at
    assert public_slot.source_generation_run_id == first.run.id


def test_theme_natal_slot_publication_reports_acceptance_once(db: Session) -> None:
    """La publication indique si un debit quota peut etre fait une seule fois."""
    first = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-quota-1",
    )
    first_publication = ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=first.run.id,
        public_payload={"title": "Premiere lecture"},
    )
    second = ThemeNatalReadingSlotService.claim_generation_run(
        db,
        key=_slot_key(),
        client_request_id="client-request-quota-2",
    )
    second_publication = ThemeNatalReadingSlotService.publish_accepted_payload(
        db,
        run_id=second.run.id,
        public_payload={"title": "Ne doit pas remplacer"},
    )

    assert first_publication.accepted_now is True
    assert second_publication.accepted_now is False
    assert second_publication.slot.public_payload == {"title": "Premiere lecture"}

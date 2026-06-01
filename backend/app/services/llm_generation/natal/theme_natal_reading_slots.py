# Commentaire global: service de persistance des slots publics et runs LLM theme natal.
"""Orchestre les claims idempotents, runs techniques et lectures publiques acceptees."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from threading import Lock, RLock

from sqlalchemy import Select, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_provider import utc_now
from app.domain.theme_natal.product_contract import (
    THEME_NATAL_READING_FEATURE,
    ThemeNatalOutputVariant,
    ThemeNatalReadingKind,
)
from app.infra.db.models.llm_generation_run import (
    LLM_GENERATION_RUN_STATUS_ACCEPTED,
    LLM_GENERATION_RUN_STATUS_GENERATING,
    LLM_GENERATION_RUN_STATUS_REJECTED,
    LlmGenerationRunModel,
)
from app.infra.db.models.theme_natal_reading_slot import (
    THEME_NATAL_SLOT_STATUS_ACCEPTED,
    THEME_NATAL_SLOT_STATUS_GENERATING,
    ThemeNatalReadingSlotModel,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementGate,
    NatalChartLongEntitlementResult,
)

_SLOT_LOCKS_GUARD = Lock()
_SLOT_LOCKS: dict[tuple[object, ...], RLock] = {}
_PUBLICATION_LOCKS: dict[int, RLock] = {}


@dataclass(frozen=True, slots=True)
class ThemeNatalReadingSlotKey:
    """Identite complete d'un slot public theme natal."""

    user_id: int
    chart_id: str
    product_plan: str
    output_variant: ThemeNatalOutputVariant | str
    contract_version: str
    reading_kind: ThemeNatalReadingKind | str = ThemeNatalReadingKind.NATAL_READING
    feature: str = THEME_NATAL_READING_FEATURE
    persona_profile_id: uuid.UUID | None = None

    def as_filter_values(self) -> dict[str, object]:
        """Retourne les valeurs normalisees utilisees par les requetes DB."""
        return {
            "user_id": self.user_id,
            "chart_id": self.chart_id,
            "feature": self.feature,
            "reading_kind": str(self.reading_kind),
            "product_plan": self.product_plan,
            "output_variant": str(self.output_variant),
            "persona_profile_id": self.persona_profile_id,
            "contract_version": self.contract_version,
        }


@dataclass(frozen=True, slots=True)
class ThemeNatalGenerationClaim:
    """Resultat d'un claim de generation idempotent."""

    slot: ThemeNatalReadingSlotModel
    run: LlmGenerationRunModel
    created_slot: bool
    created_run: bool


@dataclass(frozen=True, slots=True)
class ThemeNatalAcceptedPublication:
    """Resultat d'une publication publique acceptee."""

    slot: ThemeNatalReadingSlotModel
    run: LlmGenerationRunModel
    accepted_now: bool


class ThemeNatalReadingSlotService:
    """Expose la persistance publique acceptee separee des tentatives LLM."""

    @staticmethod
    def claim_generation_run(
        db: Session,
        *,
        key: ThemeNatalReadingSlotKey,
        client_request_id: str,
        prompt_hash: str | None = None,
        data_hash: str | None = None,
        engine_profile_version: str | None = None,
        output_schema_version: str | None = None,
    ) -> ThemeNatalGenerationClaim:
        """Cree ou relit le slot et le run idempotent d'une demande client."""
        request_id = _require_client_request_id(client_request_id)
        with _slot_lock_for_key(key):
            slot, created_slot = _get_or_create_slot(db, key)
            run, created_run = _get_or_create_generation_run(
                db,
                slot_id=slot.id,
                client_request_id=request_id,
                prompt_hash=prompt_hash,
                data_hash=data_hash,
                engine_profile_version=engine_profile_version,
                output_schema_version=output_schema_version,
            )
        return ThemeNatalGenerationClaim(
            slot=slot,
            run=run,
            created_slot=created_slot,
            created_run=created_run,
        )

    @staticmethod
    def publish_accepted_payload(
        db: Session,
        *,
        run_id: int,
        public_payload: dict[str, object],
        accepted_at: datetime | None = None,
    ) -> ThemeNatalAcceptedPublication:
        """Publie le payload public uniquement lors de la premiere acceptation."""
        run = db.get(LlmGenerationRunModel, run_id)
        if run is None:
            raise ValueError("generation run does not exist")

        with _publication_lock_for_slot(run.slot_id):
            slot = db.get(ThemeNatalReadingSlotModel, run.slot_id)
            if slot is None:
                raise ValueError("generation run is detached from its slot")

            publication_time = accepted_at or utc_now()
            result = db.execute(
                update(ThemeNatalReadingSlotModel)
                .where(
                    ThemeNatalReadingSlotModel.id == run.slot_id,
                    ThemeNatalReadingSlotModel.status != THEME_NATAL_SLOT_STATUS_ACCEPTED,
                )
                .values(
                    status=THEME_NATAL_SLOT_STATUS_ACCEPTED,
                    public_payload=dict(public_payload),
                    accepted_at=publication_time,
                    source_generation_run_id=run.id,
                )
            )
            accepted_now = result.rowcount == 1
            if accepted_now:
                run.status = LLM_GENERATION_RUN_STATUS_ACCEPTED
                run.completed_at = publication_time
            db.commit()
            db.refresh(slot)
            db.refresh(run)
            return ThemeNatalAcceptedPublication(slot=slot, run=run, accepted_now=accepted_now)

    @staticmethod
    def record_rejected_run(
        db: Session,
        *,
        run_id: int,
        raw_provider_response: dict[str, object] | None = None,
        parsed_raw_response: dict[str, object] | None = None,
        validation_errors: list[dict[str, object]] | None = None,
        rejection_reason: dict[str, object] | None = None,
    ) -> LlmGenerationRunModel:
        """Marque un run rejete sans modifier le payload public du slot."""
        run = db.get(LlmGenerationRunModel, run_id)
        if run is None:
            raise ValueError("generation run does not exist")
        run.status = LLM_GENERATION_RUN_STATUS_REJECTED
        run.raw_provider_response = raw_provider_response
        run.parsed_raw_response = parsed_raw_response
        run.validation_errors = validation_errors
        run.rejection_reason = rejection_reason
        run.completed_at = utc_now()
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_public_slot_by_key(
        db: Session,
        *,
        key: ThemeNatalReadingSlotKey,
    ) -> ThemeNatalReadingSlotModel | None:
        """Retourne uniquement le slot public accepte pour cette identite."""
        return db.execute(_slot_key_stmt(key).where(_accepted_slot_filter())).scalar_one_or_none()

    @staticmethod
    def list_public_slots(
        db: Session,
        *,
        user_id: int,
        chart_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ThemeNatalReadingSlotModel], int]:
        """Liste seulement les slots acceptes, jamais les runs techniques."""
        stmt = select(ThemeNatalReadingSlotModel).where(
            ThemeNatalReadingSlotModel.user_id == user_id,
            _accepted_slot_filter(),
        )
        if chart_id is not None:
            stmt = stmt.where(ThemeNatalReadingSlotModel.chart_id == chart_id)
        total = db.execute(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        ).scalar_one()
        rows = list(
            db.execute(
                stmt.order_by(ThemeNatalReadingSlotModel.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return rows, total

    @staticmethod
    def consume_quota_after_publication(
        db: Session,
        *,
        user_id: int,
        access_result: NatalChartLongEntitlementResult,
        publication: ThemeNatalAcceptedPublication,
    ) -> NatalChartLongEntitlementResult | None:
        """Debite le quota uniquement apres une nouvelle publication acceptee."""
        if not publication.accepted_now:
            return None
        return NatalChartLongEntitlementGate.consume_on_acceptance(
            db,
            user_id=user_id,
            access_result=access_result,
        )


def _require_client_request_id(client_request_id: str) -> str:
    request_id = client_request_id.strip()
    if not request_id:
        raise ValueError("client_request_id is required")
    return request_id


def _slot_key_stmt(key: ThemeNatalReadingSlotKey) -> Select[tuple[ThemeNatalReadingSlotModel]]:
    values = key.as_filter_values()
    stmt = select(ThemeNatalReadingSlotModel).where(
        ThemeNatalReadingSlotModel.user_id == values["user_id"],
        ThemeNatalReadingSlotModel.chart_id == values["chart_id"],
        ThemeNatalReadingSlotModel.feature == values["feature"],
        ThemeNatalReadingSlotModel.reading_kind == values["reading_kind"],
        ThemeNatalReadingSlotModel.product_plan == values["product_plan"],
        ThemeNatalReadingSlotModel.output_variant == values["output_variant"],
        ThemeNatalReadingSlotModel.contract_version == values["contract_version"],
    )
    persona_profile_id = values["persona_profile_id"]
    if persona_profile_id is None:
        return stmt.where(ThemeNatalReadingSlotModel.persona_profile_id.is_(None))
    return stmt.where(ThemeNatalReadingSlotModel.persona_profile_id == persona_profile_id)


def _accepted_slot_filter() -> object:
    return ThemeNatalReadingSlotModel.status == THEME_NATAL_SLOT_STATUS_ACCEPTED


def _slot_lock_for_key(key: ThemeNatalReadingSlotKey) -> RLock:
    """Retourne le verrou applicatif local associe a une identite de slot."""
    values = key.as_filter_values()
    lock_key = (
        values["user_id"],
        values["chart_id"],
        values["feature"],
        values["reading_kind"],
        values["product_plan"],
        values["output_variant"],
        values["persona_profile_id"],
        values["contract_version"],
    )
    with _SLOT_LOCKS_GUARD:
        lock = _SLOT_LOCKS.get(lock_key)
        if lock is None:
            lock = RLock()
            _SLOT_LOCKS[lock_key] = lock
        return lock


def _publication_lock_for_slot(slot_id: int) -> RLock:
    """Retourne le verrou applicatif local associe a la publication d'un slot."""
    with _SLOT_LOCKS_GUARD:
        lock = _PUBLICATION_LOCKS.get(slot_id)
        if lock is None:
            lock = RLock()
            _PUBLICATION_LOCKS[slot_id] = lock
        return lock


def _get_or_create_slot(
    db: Session,
    key: ThemeNatalReadingSlotKey,
) -> tuple[ThemeNatalReadingSlotModel, bool]:
    existing = db.execute(_slot_key_stmt(key)).scalar_one_or_none()
    if existing is not None:
        return existing, False

    values = key.as_filter_values()
    slot = ThemeNatalReadingSlotModel(
        user_id=values["user_id"],
        chart_id=str(values["chart_id"]),
        feature=str(values["feature"]),
        reading_kind=str(values["reading_kind"]),
        product_plan=str(values["product_plan"]),
        output_variant=str(values["output_variant"]),
        persona_profile_id=values["persona_profile_id"],
        contract_version=str(values["contract_version"]),
        status=THEME_NATAL_SLOT_STATUS_GENERATING,
    )
    db.add(slot)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(_slot_key_stmt(key)).scalar_one()
        return existing, False
    db.refresh(slot)
    return slot, True


def _get_or_create_generation_run(
    db: Session,
    *,
    slot_id: int,
    client_request_id: str,
    prompt_hash: str | None,
    data_hash: str | None,
    engine_profile_version: str | None,
    output_schema_version: str | None,
) -> tuple[LlmGenerationRunModel, bool]:
    stmt = select(LlmGenerationRunModel).where(
        LlmGenerationRunModel.slot_id == slot_id,
        LlmGenerationRunModel.client_request_id == client_request_id,
    )
    existing = db.execute(stmt).scalar_one_or_none()
    if existing is not None:
        return existing, False

    run = LlmGenerationRunModel(
        slot_id=slot_id,
        client_request_id=client_request_id,
        status=LLM_GENERATION_RUN_STATUS_GENERATING,
        prompt_hash=prompt_hash,
        data_hash=data_hash,
        engine_profile_version=engine_profile_version,
        output_schema_version=output_schema_version,
    )
    db.add(run)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(stmt).scalar_one()
        return existing, False
    db.refresh(run)
    return run, True

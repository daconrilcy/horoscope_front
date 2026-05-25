# Repository d'audit narratif persistant adosse au stockage existant des interpretations.
"""Centralise la creation et la lecture des audits `narrative_answer_audit_v1`."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    build_audit_source_proofs,
    validate_evidence_refs_by_section,
)
from app.infra.db.models.user_natal_interpretation import (
    ALLOWED_NARRATIVE_ANSWER_TYPES,
    ALLOWED_NARRATIVE_GROUNDING_STATUSES,
    InterpretationLevel,
    UserNatalInterpretationModel,
)

NarrativeAnswerType = Literal["basic", "premium", "long", "sensitive", "free_short"]
NarrativeGroundingStatus = Literal["grounded", "partial", "ungrounded", "rejected", "not_checked"]


@dataclass(frozen=True, slots=True)
class NarrativeAnswerAuditCreate:
    """Porte les champs CS-259 requis pour creer une ligne auditée."""

    answer_id: str
    answer_type: NarrativeAnswerType
    chart_id: str
    user_id: int
    plan: str
    projection_version: str
    projection_hash: str
    llm_input_version: str
    llm_input_hash: str
    prompt_version: str
    provider: str
    model: str
    grounding_status: NarrativeGroundingStatus
    interpretation_payload: dict[str, object]
    use_case: str = "narrative_answer_audit_v1"
    evidence_refs: list[dict[str, object]] = field(default_factory=list)
    section_evidence_requirements: tuple[EvidenceSectionRequirement, ...] = ()
    rejection_reason: dict[str, object] | None = None
    validation_context: dict[str, object] | list[dict[str, object]] | None = None
    raw_answer_storage: dict[str, object] | None = None
    client_message: str | None = None
    prompt_ref: str | None = None
    prompt_snapshot_ref: str | None = None
    created_at: datetime | None = None


class NarrativeAnswerAuditRepository:
    """Persiste l'audit narratif sur le proprietaire `UserNatalInterpretationModel`."""

    def __init__(self, db: Session) -> None:
        """Initialise le repository avec la session SQLAlchemy active."""
        self.db = db

    def create(self, payload: NarrativeAnswerAuditCreate) -> UserNatalInterpretationModel:
        """Cree une reponse narrative auditée avec toutes les ancres CS-259."""
        _validate_closed_value(
            "answer_type",
            payload.answer_type,
            ALLOWED_NARRATIVE_ANSWER_TYPES,
        )
        _validate_closed_value(
            "grounding_status",
            payload.grounding_status,
            ALLOWED_NARRATIVE_GROUNDING_STATUSES,
        )
        grounding_status = payload.grounding_status
        evidence_refs = payload.evidence_refs
        if payload.section_evidence_requirements:
            validation_result = validate_evidence_refs_by_section(
                section_requirements=payload.section_evidence_requirements,
                evidence_refs=payload.evidence_refs,
                authorized_sources=build_audit_source_proofs(
                    projection_version=payload.projection_version,
                    projection_hash=payload.projection_hash,
                    llm_input_version=payload.llm_input_version,
                    llm_input_hash=payload.llm_input_hash,
                ),
            )
            grounding_status = validation_result.grounding_status
            evidence_refs = validation_result.to_audit_payload()
        interpretation_payload = payload.interpretation_payload
        if grounding_status == "rejected":
            _validate_rejected_payload(payload)
            interpretation_payload = {
                **payload.interpretation_payload,
                "status": "rejected",
                "rejection_reason": payload.rejection_reason,
                "validation_context": payload.validation_context,
                "raw_answer_storage": payload.raw_answer_storage,
                "client_message": payload.client_message,
                "retry_policy": "out_of_scope",
            }
            if isinstance(payload.validation_context, list):
                evidence_refs = payload.validation_context
            elif isinstance(payload.validation_context, dict):
                evidence_refs = [payload.validation_context]

        model = UserNatalInterpretationModel(
            answer_id=payload.answer_id,
            answer_type=payload.answer_type,
            chart_id=payload.chart_id,
            user_id=payload.user_id,
            plan=payload.plan,
            projection_version=payload.projection_version,
            projection_hash=payload.projection_hash,
            llm_input_version=payload.llm_input_version,
            llm_input_hash=payload.llm_input_hash,
            prompt_version=payload.prompt_version,
            prompt_ref=payload.prompt_ref,
            prompt_snapshot_ref=payload.prompt_snapshot_ref,
            provider=payload.provider,
            model=payload.model,
            grounding_status=grounding_status,
            evidence_refs=evidence_refs,
            level=_level_for_answer_type(payload.answer_type),
            use_case=payload.use_case,
            interpretation_payload=interpretation_payload,
        )
        if payload.created_at is not None:
            model.created_at = payload.created_at
        self.db.add(model)
        self.db.flush()
        return model

    def get_by_answer_id(self, answer_id: str) -> UserNatalInterpretationModel | None:
        """Relit une ligne d'audit narrative par identifiant de reponse."""
        return self.db.scalar(
            select(UserNatalInterpretationModel).where(
                UserNatalInterpretationModel.answer_id == answer_id
            )
        )


def _level_for_answer_type(answer_type: str) -> InterpretationLevel:
    """Traduit la categorie d'audit vers la granularite de stockage existante."""
    if answer_type in {"basic", "free_short"}:
        return InterpretationLevel.SHORT
    return InterpretationLevel.COMPLETE


def _validate_closed_value(field_name: str, value: str, allowed_values: tuple[str, ...]) -> None:
    """Bloque les valeurs hors vocabulaire avant la contrainte SQL."""
    if value not in allowed_values:
        raise ValueError(f"{field_name} must be one of: {', '.join(allowed_values)}")


def _validate_rejected_payload(payload: NarrativeAnswerAuditCreate) -> None:
    """Garantit que le rejet reste structure et exploitable par l'audit interne."""
    if not isinstance(payload.rejection_reason, dict) or not payload.rejection_reason.get("code"):
        raise ValueError("rejection_reason.code is required for rejected narrative answers")
    if payload.validation_context in (None, {}, []):
        raise ValueError("validation_context is required for rejected narrative answers")
    if payload.raw_answer_storage in (None, {}):
        raise ValueError("raw_answer_storage is required for rejected narrative answers")
    if not payload.client_message or not payload.client_message.strip():
        raise ValueError("client_message is required for rejected narrative answers")

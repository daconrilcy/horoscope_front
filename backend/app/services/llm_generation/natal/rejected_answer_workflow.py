# Commentaire global: ce module applique le rejet interne des reponses narratives non ancrees.
"""Workflow canonique de rejet des reponses narratives non ancrees."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceRefsValidationResult,
    EvidenceSectionRequirement,
    build_audit_source_proofs,
    validate_evidence_refs_by_section,
)

CONTROLLED_REJECTED_CLIENT_MESSAGE = (
    "Nous n'avons pas assez de preuves fiables pour afficher cette interpretation. "
    "Votre demande reste enregistree pour analyse interne."
)
REJECTED_NARRATIVE_LOG_EVENT = "narrative_answer_rejected"

RejectionGroundingStatus = Literal["grounded", "partial", "ungrounded", "not_checked"]


@dataclass(frozen=True, slots=True)
class RejectedNarrativeAnswerOutcome:
    """Expose le payload interne et le message client d'une reponse rejetee."""

    answer_id: str
    answer_type: str
    status: Literal["rejected"]
    grounding_status: Literal["ungrounded"]
    rejection_reason: dict[str, object]
    validation_context: list[dict[str, object]]
    raw_answer_storage: dict[str, object]
    client_message: str
    log_event: str
    retry_policy: Literal["out_of_scope"] = "out_of_scope"

    def to_persisted_payload(self) -> dict[str, object]:
        """Prepare le fragment stocke dans l'audit narratif interne."""
        return {
            "status": self.status,
            "rejection_reason": self.rejection_reason,
            "validation_context": self.validation_context,
            "raw_answer_storage": self.raw_answer_storage,
            "client_message": self.client_message,
            "retry_policy": self.retry_policy,
        }

    def to_client_payload(self) -> dict[str, object]:
        """Retourne uniquement le wording controle autorise cote client."""
        return {
            "status": self.status,
            "message": self.client_message,
        }


def build_rejected_narrative_answer_outcome(
    *,
    answer_id: str,
    answer_type: str,
    validation_result: EvidenceRefsValidationResult,
    raw_answer: dict[str, object],
) -> RejectedNarrativeAnswerOutcome | None:
    """Construit un rejet si la validation CS-289 conclut a `ungrounded`."""
    if validation_result.grounding_status != "ungrounded":
        return None
    validation_context = validation_result.to_audit_payload()
    return RejectedNarrativeAnswerOutcome(
        answer_id=answer_id,
        answer_type=answer_type,
        status="rejected",
        grounding_status="ungrounded",
        rejection_reason=_build_rejection_reason(validation_context),
        validation_context=validation_context,
        raw_answer_storage={"structured_output": raw_answer},
        client_message=CONTROLLED_REJECTED_CLIENT_MESSAGE,
        log_event=REJECTED_NARRATIVE_LOG_EVENT,
    )


def build_rejected_narrative_answer_outcome_from_payload(
    *,
    answer_id: str,
    answer_type: str,
    raw_answer: Mapping[str, object],
    projection_version: str,
    projection_hash: str,
    llm_input_version: str,
    llm_input_hash: str,
) -> RejectedNarrativeAnswerOutcome | None:
    """Reutilise CS-289 pour rejeter un payload porteur de `evidence_refs`."""
    if answer_type == "basic" and "evidence_refs" not in raw_answer:
        return None

    section_requirements = _section_requirements(raw_answer)
    if not section_requirements:
        return None
    evidence_refs = raw_answer.get("evidence_refs", ())
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)):
        evidence_refs = ()
    validation_result = validate_evidence_refs_by_section(
        section_requirements=section_requirements,
        evidence_refs=evidence_refs,
        authorized_sources=build_audit_source_proofs(
            projection_version=projection_version,
            projection_hash=projection_hash,
            llm_input_version=llm_input_version,
            llm_input_hash=llm_input_hash,
        ),
    )
    return build_rejected_narrative_answer_outcome(
        answer_id=answer_id,
        answer_type=answer_type,
        validation_result=validation_result,
        raw_answer=dict(raw_answer),
    )


def emit_rejected_narrative_answer_log(
    logger: logging.Logger,
    *,
    outcome: RejectedNarrativeAnswerOutcome,
    request_id: str,
    trace_id: str,
    use_case: str,
) -> None:
    """Emet un log interne sans exposer le payload narratif brut."""
    logger.info(
        "narrative_answer_rejected request_id=%s trace_id=%s answer_id=%s "
        "answer_type=%s use_case=%s reason_code=%s",
        request_id,
        trace_id,
        outcome.answer_id,
        outcome.answer_type,
        use_case,
        outcome.rejection_reason["code"],
        extra={
            "event": outcome.log_event,
            "request_id": request_id,
            "trace_id": trace_id,
            "answer_id": outcome.answer_id,
            "answer_type": outcome.answer_type,
            "use_case": use_case,
            "rejection_reason": outcome.rejection_reason,
        },
    )


def _build_rejection_reason(validation_context: list[dict[str, object]]) -> dict[str, object]:
    """Derive une raison structuree a partir du contexte de validation."""
    validation_errors: list[str] = []
    failed_sections: list[str] = []
    for section in validation_context:
        if section.get("section_status") != "grounded":
            failed_sections.append(str(section.get("section_id", "unknown")))
        refs = section.get("evidence_refs", [])
        if isinstance(refs, list):
            for ref in refs:
                if isinstance(ref, dict):
                    for error in ref.get("validation_errors", []) or []:
                        validation_errors.append(str(error))
    return {
        "code": "ungrounded_evidence_refs",
        "failed_sections": failed_sections,
        "validation_errors": sorted(set(validation_errors)),
    }


def _section_requirements(
    raw_answer: Mapping[str, object],
) -> tuple[EvidenceSectionRequirement, ...]:
    """Deduit les sections narratives qui doivent porter des preuves."""
    sections = raw_answer.get("sections")
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes)):
        return ()
    requirements: list[EvidenceSectionRequirement] = []
    for index, section in enumerate(sections):
        section_id = ""
        if isinstance(section, Mapping):
            section_id = str(section.get("key") or section.get("section_id") or "").strip()
        if not section_id:
            section_id = f"section_{index}"
        requirements.append(EvidenceSectionRequirement(section_id, requires_evidence=True))
    return tuple(requirements)

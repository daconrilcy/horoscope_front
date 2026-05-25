# Commentaire global: ces tests prouvent la persistance interne des rejets narratifs.
"""Controle l'audit persistant des reponses narratives rejetees."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    validate_evidence_refs_by_section,
)
from app.infra.db.repositories.llm.narrative_answer_audit_repository import (
    NarrativeAnswerAuditCreate,
    NarrativeAnswerAuditRepository,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    CONTROLLED_REJECTED_CLIENT_MESSAGE,
    build_rejected_narrative_answer_outcome,
)


def test_rejected_answer_is_persisted_with_reason_context_and_raw_storage(db: Session) -> None:
    """Le repository canonique stocke le rejet complet sans table parallele."""
    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=(),
        authorized_sources=(),
    )
    outcome = build_rejected_narrative_answer_outcome(
        answer_id="answer-cs290-audit",
        answer_type="premium",
        validation_result=validation_result,
        raw_answer={"summary": "RAW_REJECTED_INTERNAL_ONLY"},
    )
    assert outcome is not None

    repository = NarrativeAnswerAuditRepository(db)
    repository.create(
        NarrativeAnswerAuditCreate(
            answer_id=outcome.answer_id,
            answer_type="premium",
            chart_id="chart-cs290",
            user_id=290,
            plan="premium",
            projection_version="client_interpretation_projection_v1",
            projection_hash="a" * 64,
            llm_input_version="llm_runtime_gateway_input.v1",
            llm_input_hash="b" * 64,
            prompt_version="prompt-v1",
            provider="openai",
            model="gpt-test",
            grounding_status="rejected",
            interpretation_payload={"client_message": outcome.client_message},
            rejection_reason=outcome.rejection_reason,
            validation_context=outcome.validation_context,
            raw_answer_storage=outcome.raw_answer_storage,
            client_message=outcome.client_message,
        )
    )
    db.commit()

    persisted = repository.get_by_answer_id("answer-cs290-audit")
    assert persisted is not None
    assert persisted.grounding_status == "rejected"
    assert persisted.interpretation_payload["status"] == "rejected"
    assert persisted.interpretation_payload["rejection_reason"]["code"] == (
        "ungrounded_evidence_refs"
    )
    assert persisted.interpretation_payload["validation_context"][0]["section_status"] == (
        "ungrounded"
    )
    assert persisted.interpretation_payload["raw_answer_storage"] == {
        "structured_output": {"summary": "RAW_REJECTED_INTERNAL_ONLY"}
    }
    assert persisted.interpretation_payload["client_message"] == CONTROLLED_REJECTED_CLIENT_MESSAGE
    assert persisted.interpretation_payload["retry_policy"] == "out_of_scope"

# Commentaire global: ces tests prouvent le masquage client des reponses rejetees.
"""Controle la projection client d'une reponse narrative rejetee."""

from __future__ import annotations

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    validate_evidence_refs_by_section,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    CONTROLLED_REJECTED_CLIENT_MESSAGE,
    build_rejected_narrative_answer_outcome,
)


def test_rejected_answer_client_response_masks_raw_ai_answer() -> None:
    """La projection client contient seulement le message controle."""
    raw_answer = {"summary": "RAW_AI_ANSWER_MUST_STAY_INTERNAL"}
    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=(),
        authorized_sources=(),
    )

    outcome = build_rejected_narrative_answer_outcome(
        answer_id="answer-response",
        answer_type="premium",
        validation_result=validation_result,
        raw_answer=raw_answer,
    )

    assert outcome is not None
    client_payload = outcome.to_client_payload()
    assert client_payload["message"] == CONTROLLED_REJECTED_CLIENT_MESSAGE
    assert "RAW_AI_ANSWER_MUST_STAY_INTERNAL" not in str(client_payload)
    assert "raw_answer_storage" not in client_payload
    assert "validation_context" not in client_payload

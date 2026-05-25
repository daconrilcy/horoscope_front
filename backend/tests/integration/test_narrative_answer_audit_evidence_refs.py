# Commentaire global: ces tests prouvent l'integration des preuves dans l'audit narratif.
"""Controle la persistance des resultats `evidence_refs` dans l'audit."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
)
from app.infra.db.repositories.llm.narrative_answer_audit_repository import (
    NarrativeAnswerAuditCreate,
    NarrativeAnswerAuditRepository,
)


def test_narrative_answer_audit_persists_section_validation_results(db: Session) -> None:
    """Le repository canonique stocke les statuts de preuve par section."""
    projection_hash = "1" * 64
    llm_input_hash = "2" * 64

    repository = NarrativeAnswerAuditRepository(db)
    row = repository.create(
        NarrativeAnswerAuditCreate(
            answer_id="answer-cs289",
            answer_type="premium",
            chart_id="chart-cs289",
            user_id=289,
            plan="premium",
            projection_version="structured_facts_v1",
            projection_hash=projection_hash,
            llm_input_version="llm_runtime_gateway_input.v1",
            llm_input_hash=llm_input_hash,
            prompt_version="prompt-v1",
            provider="test-provider",
            model="test-model",
            grounding_status="not_checked",
            interpretation_payload={"summary": "texte audite"},
            section_evidence_requirements=(
                EvidenceSectionRequirement("summary", requires_evidence=True),
                EvidenceSectionRequirement("llm.context", requires_evidence=True),
            ),
            evidence_refs=[
                {
                    "section_id": "summary",
                    "source_type": "projection_version",
                    "source_id": "projection",
                    "source_version": "structured_facts_v1",
                    "source_hash": projection_hash,
                },
                {
                    "section_id": "llm.context",
                    "source_type": "llm_input",
                    "source_id": "llm_input",
                    "source_version": "llm_runtime_gateway_input.v1",
                    "source_hash": llm_input_hash,
                },
            ],
        )
    )

    db.commit()
    persisted = repository.get_by_answer_id(row.answer_id)

    assert persisted is not None
    assert persisted.grounding_status == "grounded"
    assert [section["section_status"] for section in persisted.evidence_refs] == [
        "grounded",
        "grounded",
    ]
    assert persisted.evidence_refs[0]["evidence_refs"][0]["validation_state"] == "valid"

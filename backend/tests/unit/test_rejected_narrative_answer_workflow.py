# Commentaire global: ces tests valident la decision de rejet des reponses narratives.
"""Controle le workflow CS-290 de rejet des reponses non ancrees."""

from __future__ import annotations

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    validate_evidence_refs_by_section,
)
from app.services.llm_generation.natal.rejected_answer_workflow import (
    CONTROLLED_REJECTED_CLIENT_MESSAGE,
    build_rejected_narrative_answer_outcome,
    build_rejected_narrative_answer_outcome_from_payload,
)


def test_ungrounded_validation_becomes_rejected_outcome() -> None:
    """Un resultat CS-289 non ancre devient un rejet structure."""
    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=(),
        authorized_sources=(),
    )

    outcome = build_rejected_narrative_answer_outcome(
        answer_id="answer-cs290",
        answer_type="premium",
        validation_result=validation_result,
        raw_answer={"summary": "texte brut a masquer"},
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.grounding_status == "ungrounded"
    assert outcome.rejection_reason["code"] == "ungrounded_evidence_refs"
    assert outcome.validation_context[0]["section_status"] == "ungrounded"
    assert outcome.raw_answer_storage["structured_output"] == {"summary": "texte brut a masquer"}


def test_grounded_validation_does_not_create_rejection() -> None:
    """Une reponse ancree reste hors du workflow de rejet."""
    proof_hash = "a" * 64
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-grounded",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte prouve"}],
            "evidence_refs": [
                {
                    "section_id": "summary",
                    "source_type": "projection_version",
                    "source_id": "projection",
                    "source_version": "v1",
                    "source_hash": proof_hash,
                }
            ],
        },
        projection_version="v1",
        projection_hash=proof_hash,
        llm_input_version="llm_runtime_gateway_input.v1",
        llm_input_hash="b" * 64,
    )

    assert outcome is None


def test_missing_evidence_refs_on_required_sections_becomes_rejected() -> None:
    """L'absence de preuves sur une section obligatoire produit un rejet."""
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-missing-refs",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte sans preuve"}],
        },
        projection_version="v1",
        projection_hash="a" * 64,
        llm_input_version="llm_runtime_gateway_input.v1",
        llm_input_hash="b" * 64,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.validation_context[0]["section_status"] == "ungrounded"
    assert outcome.rejection_reason["validation_errors"] == ["missing_required_evidence_ref"]


def test_unsupported_generated_claim_becomes_rejected() -> None:
    """Une assertion hors sources internes produit un rejet sans appel provider."""
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-unsupported-claim",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte avec invention"}],
            "unsupported_claims": ["Maison XII dominante sans donnee maison"],
        },
        projection_version="v1",
        projection_hash="a" * 64,
        llm_input_version="llm_runtime_gateway_input.v1",
        llm_input_hash="b" * 64,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.rejection_reason["code"] == "natal_output_policy_violation"
    assert outcome.rejection_reason["validation_errors"] == ["unsupported_generated_claim"]


def test_ignored_critical_limit_becomes_rejected() -> None:
    """Une reponse qui ignore une limite critique est marquee non conforme."""
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-ignored-limit",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte sans signaler la limite"}],
            "ignored_critical_limits": ["birth_time_missing"],
        },
        projection_version="v1",
        projection_hash="a" * 64,
        llm_input_version="llm_runtime_gateway_input.v1",
        llm_input_hash="b" * 64,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.rejection_reason["code"] == "natal_output_policy_violation"
    assert outcome.rejection_reason["validation_errors"] == ["critical_limit_ignored"]


def test_basic_legacy_payload_without_evidence_refs_is_not_rejected() -> None:
    """Le format court historique reste en audit `not_checked` sans rejet client."""
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-basic-legacy",
        answer_type="basic",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte court historique"}],
        },
        projection_version="v1",
        projection_hash="a" * 64,
        llm_input_version="llm_runtime_gateway_input.v1",
        llm_input_hash="b" * 64,
    )

    assert outcome is None


def test_client_payload_contains_controlled_wording_only() -> None:
    """Le payload client ne contient jamais le contenu narratif rejete."""
    validation_result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("overview", requires_evidence=True),),
        evidence_refs=("texte decoratif",),
        authorized_sources=(),
    )

    outcome = build_rejected_narrative_answer_outcome(
        answer_id="answer-mask",
        answer_type="basic",
        validation_result=validation_result,
        raw_answer={"summary": "CONTENU IA REJETE UNIQUE"},
    )

    assert outcome is not None
    assert outcome.to_client_payload() == {
        "status": "rejected",
        "message": CONTROLLED_REJECTED_CLIENT_MESSAGE,
    }
    assert "CONTENU IA REJETE UNIQUE" not in str(outcome.to_client_payload())

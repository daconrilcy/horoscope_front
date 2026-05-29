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
from tests.unit.domain.astrology.test_llm_astrology_input_v1 import _build_payload


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
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-grounded",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "texte prouve"}],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is None


def test_known_fact_output_evidence_id_is_grounded() -> None:
    """Un ID de fait du theme cite par le LLM reste rattache a la projection hashee."""
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-fact-evidence",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "Mars en Aries donne l'elan."}],
            "evidence": ["MARS"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is None


def test_unknown_output_evidence_id_becomes_rejected() -> None:
    """Une evidence de sortie inconnue ne peut pas etre ancree par le backend."""
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-fake-evidence",
        answer_type="premium",
        raw_answer={
            "sections": [{"key": "summary", "content": "Mars en Aries reste coherent."}],
            "evidence": ["TOTALLY_FAKE_EVIDENCE"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.rejection_reason["validation_errors"] == ["unsupported_source_type"]


def test_single_output_evidence_does_not_ground_multiple_sections() -> None:
    """Une evidence unique ne couvre pas implicitement plusieurs sections."""
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-under-evidenced",
        answer_type="premium",
        raw_answer={
            "sections": [
                {"key": "summary", "content": "Mars en Aries donne l'elan."},
                {"key": "career", "content": "Mars en Aries colore l'action."},
            ],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert "missing_required_evidence_ref" in outcome.rejection_reason["validation_errors"]


def test_missing_evidence_on_required_sections_becomes_rejected() -> None:
    """L'absence d'evidence de sortie sur une section obligatoire produit un rejet."""
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
    """Une assertion marquee hors sources internes produit un rejet sans appel provider."""
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


def test_backend_detects_unsupported_generated_claim_without_llm_marker() -> None:
    """Une invention lisible dans le texte est controlee contre les faits internes."""
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-backend-unsupported-claim",
        answer_type="premium",
        raw_answer={
            "sections": [
                {
                    "key": "summary",
                    "content": "Venus en Balance structure toute la lecture.",
                }
            ],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.rejection_reason["code"] == "natal_output_policy_violation"
    assert outcome.rejection_reason["validation_errors"] == ["unsupported_generated_claim"]


def test_backend_accepts_supported_french_astrology_aliases() -> None:
    """Les libelles astrologiques francais supportes ne sont pas des inventions."""
    llm_input = _build_payload()
    llm_input["facts"]["positions"].extend(
        [
            {
                "code": "venus",
                "object_type": "planet",
                "zodiac_sign": "taurus",
                "house_number": 2,
            },
            {
                "code": "saturn",
                "object_type": "planet",
                "zodiac_sign": "capricorn",
                "house_number": 10,
            },
        ]
    )
    llm_input["facts"]["major_aspects"].extend(
        [
            {"code": "square", "participant_codes": ["sun", "saturn"], "family": "major"},
            {"code": "conjunction", "participant_codes": ["sun", "venus"], "family": "major"},
        ]
    )
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-supported-french-aliases",
        answer_type="premium",
        raw_answer={
            "sections": [
                {
                    "key": "summary",
                    "content": (
                        "Le Soleil, Vénus et Saturne dialoguent avec un trigone, "
                        "un carré et une conjonction."
                    ),
                }
            ],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is None


def test_backend_detects_unknown_astrology_marker_without_llm_marker() -> None:
    """Un marqueur astrologique hors donnees internes est rejete."""
    llm_input = _build_payload()
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-backend-unknown-marker",
        answer_type="premium",
        raw_answer={
            "sections": [
                {
                    "key": "summary",
                    "content": "Votre kiron karmique est dominant dans cette dynamique.",
                }
            ],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
    )

    assert outcome is not None
    assert outcome.status == "rejected"
    assert outcome.rejection_reason["code"] == "natal_output_policy_violation"
    assert outcome.rejection_reason["validation_errors"] == ["unsupported_generated_claim"]


def test_ignored_critical_limit_becomes_rejected() -> None:
    """Une reponse marquee comme ignorant une limite critique est non conforme."""
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


def test_backend_detects_ignored_critical_limit_without_llm_marker() -> None:
    """Une redaction sur une surface absente est controlee contre `limits`."""
    llm_input = _build_payload(with_payloads=False)
    outcome = build_rejected_narrative_answer_outcome_from_payload(
        answer_id="answer-backend-ignored-limit",
        answer_type="premium",
        raw_answer={
            "sections": [
                {
                    "key": "summary",
                    "content": "Les maisons relationnelles expliquent la relation.",
                }
            ],
            "evidence": ["LLM_ASTROLOGY_INPUT_V1.PROJECTION"],
        },
        projection_version=llm_input["evidence"]["evidence_refs"][0]["source_version"],
        projection_hash=llm_input["provenance"]["projection_hash"],
        llm_input_version=llm_input["contract_version"],
        llm_input_hash=llm_input["provenance"]["llm_input_hash"],
        llm_astrology_input_v1=llm_input,
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

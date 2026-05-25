# Commentaire global: ces tests prouvent la validation unitaire des preuves narratives.
"""Valide les references `evidence_refs` contre des sources autorisees."""

from __future__ import annotations

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    EvidenceSourceProof,
    validate_evidence_refs_by_section,
)


def test_decorative_evidence_ref_is_rejected() -> None:
    """Une chaine decorative ne peut jamais devenir une preuve valide."""
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", requires_evidence=True),),
        evidence_refs=("voir le Soleil en Lion",),
        authorized_sources=(),
    )

    reference = result.sections[0].references[0]
    assert reference.validation_state == "unsupported_source_type"
    assert reference.validation_errors == ("decorative_evidence_ref",)
    assert result.sections[0].section_status == "ungrounded"


def test_hash_backed_projection_source_is_accepted() -> None:
    """Une projection autorisee avec hash identique fonde la section."""
    projection_hash = "a" * 64
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("overview", requires_evidence=True),),
        evidence_refs=(
            {
                "section_id": "overview",
                "evidence_ref_id": "overview.ref.001",
                "source_type": "projection_version",
                "source_id": "projection",
                "source_version": "structured_facts_v1",
                "source_hash": projection_hash,
            },
        ),
        authorized_sources=(
            EvidenceSourceProof(
                source_type="projection_version",
                source_id="projection",
                source_version="structured_facts_v1",
                source_hash=projection_hash,
            ),
        ),
    )

    assert result.sections[0].references[0].validation_state == "valid"
    assert result.sections[0].section_status == "grounded"
    assert result.grounding_status == "grounded"


def test_hash_backed_llm_input_source_is_accepted() -> None:
    """Une entree LLM hashee peut servir d'ancre interne d'audit."""
    input_hash = "b" * 64
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("llm.context", requires_evidence=True),),
        evidence_refs=(
            {
                "section_id": "llm.context",
                "evidence_ref_id": "llm.context.ref.001",
                "source_type": "llm_input",
                "source_id": "llm_input",
                "source_version": "llm_runtime_gateway_input.v1",
                "source_hash": input_hash,
            },
        ),
        authorized_sources=(
            EvidenceSourceProof(
                source_type="llm_input",
                source_id="llm_input",
                source_version="llm_runtime_gateway_input.v1",
                source_hash=input_hash,
            ),
        ),
    )

    assert result.sections[0].references[0].validation_state == "valid"
    assert result.sections[0].section_status == "grounded"


def test_hash_mismatch_is_rejected() -> None:
    """Un hash different de la source persistee invalide la reference."""
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("overview", requires_evidence=True),),
        evidence_refs=(
            {
                "section_id": "overview",
                "source_type": "projection_version",
                "source_id": "projection",
                "source_version": "structured_facts_v1",
                "source_hash": "c" * 64,
            },
        ),
        authorized_sources=(
            EvidenceSourceProof(
                source_type="projection_version",
                source_id="projection",
                source_version="structured_facts_v1",
                source_hash="d" * 64,
            ),
        ),
    )

    assert result.sections[0].references[0].validation_state == "hash_mismatch"
    assert result.sections[0].section_status == "ungrounded"


def test_non_hex_hash_is_rejected() -> None:
    """Un hash de longueur correcte mais non hexadecimal reste invalide."""
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("overview", requires_evidence=True),),
        evidence_refs=(
            {
                "section_id": "overview",
                "source_type": "projection_version",
                "source_id": "projection",
                "source_version": "structured_facts_v1",
                "source_hash": "z" * 64,
            },
        ),
        authorized_sources=(),
    )

    assert result.sections[0].references[0].validation_state == "missing_hash"
    assert result.sections[0].references[0].validation_errors == ("invalid_hash",)

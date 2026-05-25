# Commentaire global: ces tests verrouillent les statuts de section des preuves narratives.
"""Controle l'agregation des statuts `evidence_refs` par section."""

from __future__ import annotations

from app.domain.astrology.interpretation.evidence_refs_validation import (
    EvidenceSectionRequirement,
    EvidenceSourceProof,
    validate_evidence_refs_by_section,
)


def test_no_proof_required_section_stays_distinct() -> None:
    """Une section non exigeante n'est pas classee invalide sans preuve."""
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("disclaimer", requires_evidence=False),),
        evidence_refs=(),
        authorized_sources=(),
    )

    assert result.sections[0].section_status == "not_required"
    assert result.grounding_status == "not_checked"


def test_missing_required_proof_is_ungrounded() -> None:
    """Une section exigeante sans preuve reste explicitement non fondee."""
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("summary", True),),
        evidence_refs=(),
        authorized_sources=(),
    )

    assert result.sections[0].section_status == "ungrounded"
    assert result.sections[0].references[0].validation_state == "missing_source"
    assert result.grounding_status == "ungrounded"


def test_grounded_partial_and_ungrounded_statuses_are_produced() -> None:
    """Les trois statuts de grounding observables restent stables."""
    valid_hash = "e" * 64
    result = validate_evidence_refs_by_section(
        section_requirements=(
            EvidenceSectionRequirement("grounded", True),
            EvidenceSectionRequirement("partial", True),
            EvidenceSectionRequirement("ungrounded", True),
        ),
        evidence_refs=(
            _ref("grounded", "projection_version", "projection", "v1", valid_hash),
            _ref("partial", "projection_version", "projection", "v1", valid_hash),
            _ref("partial", "projection_version", "projection", "v1", "f" * 64),
            _ref("ungrounded", "unknown", "projection", "v1", valid_hash),
        ),
        authorized_sources=(
            EvidenceSourceProof("projection_version", "projection", "v1", valid_hash),
        ),
    )

    statuses = {section.section_id: section.section_status for section in result.sections}
    assert statuses == {
        "grounded": "grounded",
        "partial": "partial",
        "ungrounded": "ungrounded",
    }
    assert result.grounding_status == "partial"


def test_unknown_section_ref_is_reported_as_ungrounded() -> None:
    """Une preuve rattachee a une section inconnue ne peut pas etre ignoree."""
    valid_hash = "a" * 64
    result = validate_evidence_refs_by_section(
        section_requirements=(EvidenceSectionRequirement("known", True),),
        evidence_refs=(
            _ref("known", "projection_version", "projection", "v1", valid_hash),
            _ref("unknown", "projection_version", "projection", "v1", valid_hash),
        ),
        authorized_sources=(
            EvidenceSourceProof("projection_version", "projection", "v1", valid_hash),
        ),
    )

    statuses = {section.section_id: section.section_status for section in result.sections}
    assert statuses == {"known": "grounded", "unknown": "ungrounded"}
    assert result.sections[1].references[0].validation_errors == ("unknown_section",)
    assert result.grounding_status == "partial"


def test_unscoped_decorative_ref_in_multi_section_audit_is_reported() -> None:
    """Une reference decorative non rattachee reste visible en audit multi-section."""
    result = validate_evidence_refs_by_section(
        section_requirements=(
            EvidenceSectionRequirement("summary", False),
            EvidenceSectionRequirement("analysis", False),
        ),
        evidence_refs=("decorative only",),
        authorized_sources=(),
    )

    assert result.sections[-1].section_id == "__unscoped__"
    assert result.sections[-1].section_status == "ungrounded"
    assert result.sections[-1].references[0].validation_errors == (
        "decorative_evidence_ref",
        "unscoped_evidence_ref",
    )
    assert result.grounding_status == "ungrounded"


def _ref(
    section_id: str,
    source_type: str,
    source_id: str,
    source_version: str,
    source_hash: str,
) -> dict[str, object]:
    """Construit une reference de test concise."""
    return {
        "section_id": section_id,
        "source_type": source_type,
        "source_id": source_id,
        "source_version": source_version,
        "source_hash": source_hash,
    }

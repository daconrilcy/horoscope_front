"""Tests de provenance et priorisation semantique des aspects."""

import pytest

from app.domain.astrology.interpretation.aspect_semantic_provenance import (
    AspectSemanticCandidate,
    SemanticProvenance,
    prioritize_semantic_candidates,
)


def test_semantic_provenance_requires_source_system() -> None:
    """La provenance conserve systeme, tradition et reference source."""
    provenance = SemanticProvenance(
        source_system="modern",
        source_tradition="reference_profile",
        source_authority="astral_aspect_interpretation_profiles",
        origin_reference="trine",
    )

    assert provenance.source_system == "modern"
    assert provenance.source_tradition == "reference_profile"


def test_semantic_candidate_keeps_confidence_and_axes() -> None:
    """Un candidat conserve ses axes semantiques et sa confiance."""
    candidate = AspectSemanticCandidate(
        semantic_axes=("flow", "integration"),
        provenance=SemanticProvenance(source_system="modern", source_tradition="profile"),
        confidence=0.7,
    )

    assert candidate.confidence == 0.7
    assert candidate.semantic_axes == ("flow", "integration")


def test_prioritization_keeps_competing_candidates() -> None:
    """La priorisation selectionne sans supprimer les candidats concurrents."""
    low = AspectSemanticCandidate(
        semantic_axes=("support",),
        provenance=SemanticProvenance(source_system="modern", source_tradition="profile"),
        confidence=0.4,
    )
    high = AspectSemanticCandidate(
        semantic_axes=("activation",),
        provenance=SemanticProvenance(source_system="traditional", source_tradition="profile"),
        confidence=0.9,
    )

    result = prioritize_semantic_candidates((low, high))

    assert len(result) == 2
    assert result[0].selected is True
    assert result[0].semantic_axes == ("activation",)
    assert result[1].selected is False


def test_unknown_source_authority_is_rejected() -> None:
    """Une autorite inconnue explicite n'est pas une provenance valide."""
    with pytest.raises(ValueError, match="unknown source_authority"):
        SemanticProvenance(
            source_system="modern",
            source_tradition="profile",
            source_authority=" UNKNOWN ",
        )


def test_semantic_candidate_requires_positive_context_weight() -> None:
    """Le poids de contexte nul ne doit pas masquer un candidat artificiel."""
    with pytest.raises(ValueError, match="context_weight must be positive"):
        AspectSemanticCandidate(
            semantic_axes=("activation",),
            provenance=SemanticProvenance(source_system="modern", source_tradition="profile"),
            confidence=0.7,
            context_weight=0.0,
        )


def test_semantic_candidate_rejects_blank_axes() -> None:
    """Un candidat semantique ne conserve pas d'axe vide."""
    with pytest.raises(ValueError, match="requires semantic_axes"):
        AspectSemanticCandidate(
            semantic_axes=(" ",),
            provenance=SemanticProvenance(source_system="modern", source_tradition="profile"),
            confidence=0.7,
        )

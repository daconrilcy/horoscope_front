"""Provenance et priorisation des candidats semantiques d'aspect.

Les candidats concurrents restent conserves afin que la selection semantique
ne devienne pas une sortie unique arbitraire.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class SemanticProvenance:
    """Origine tracee d'une lecture semantique d'aspect."""

    source_system: str
    source_tradition: str
    source_authority: str | None = None
    origin_reference: str | None = None

    def __post_init__(self) -> None:
        """Refuse les sources vides ou explicitement inconnues."""
        if not self.source_system.strip() or not self.source_tradition.strip():
            raise ValueError("semantic provenance requires source_system and source_tradition")
        if self.source_authority is not None:
            normalized_authority = self.source_authority.strip().lower()
            if not normalized_authority or normalized_authority == "unknown":
                raise ValueError("semantic provenance cannot use unknown source_authority")


@dataclass(frozen=True, slots=True)
class AspectSemanticCandidate:
    """Lecture semantique candidate avec confiance et provenance."""

    semantic_axes: tuple[str, ...]
    provenance: SemanticProvenance
    confidence: float
    context_weight: float = 1.0
    priority_rank: int | None = None
    selected: bool = False

    def __post_init__(self) -> None:
        """Valide la presence d'axes et borne la confiance."""
        if not self.semantic_axes or any(not axis.strip() for axis in self.semantic_axes):
            raise ValueError("aspect semantic candidate requires semantic_axes")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("aspect semantic candidate confidence must be between 0 and 1")
        if self.context_weight <= 0.0:
            raise ValueError("aspect semantic candidate context_weight must be positive")

    @property
    def priority_score(self) -> float:
        """Score interne de priorisation non produit."""
        return round(self.confidence * self.context_weight, 4)


def prioritize_semantic_candidates(
    candidates: tuple[AspectSemanticCandidate, ...],
) -> tuple[AspectSemanticCandidate, ...]:
    """Classe les candidats et selectionne le premier sans supprimer les autres."""
    if not candidates:
        raise ValueError("semantic prioritization requires at least one candidate")
    ordered = sorted(
        candidates,
        key=lambda candidate: (
            -candidate.priority_score,
            candidate.provenance.source_system,
            candidate.provenance.source_tradition,
        ),
    )
    return tuple(
        replace(candidate, priority_rank=index + 1, selected=index == 0)
        for index, candidate in enumerate(ordered)
    )

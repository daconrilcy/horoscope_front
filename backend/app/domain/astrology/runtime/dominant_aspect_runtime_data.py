"""Contrat runtime des aspects dominants.

La dominance est un classement astrologique structurel derive du runtime aspect,
distinct du score de force technique et du scoring produit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.astrology.runtime.aspect_runtime_data import AspectRuntimeData


class DominantAspectReason(StrEnum):
    """Raison canonique contribuant au classement dominant."""

    TIGHT_ORB = "tight_orb"
    EXACT_ORB = "exact_orb"
    MAJOR_ASPECT = "major_aspect"
    LUMINARY_INVOLVED = "luminary_involved"
    HIGH_STRENGTH = "high_strength"


@dataclass(frozen=True, slots=True)
class DominantAspectRuntimeData:
    """Aspect classe avec score de dominance et facteurs explicites."""

    aspect_runtime: AspectRuntimeData
    dominance_score: float
    rank: int
    reasons: tuple[DominantAspectReason, ...]
    score_factors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Garantit un classement borne et justifie."""
        if not 0.0 <= self.dominance_score <= 1.0:
            raise ValueError("dominant aspect score must be between 0 and 1")
        if self.rank < 1:
            raise ValueError("dominant aspect rank must be positive")
        if not self.reasons:
            raise ValueError("dominant aspect requires at least one reason")

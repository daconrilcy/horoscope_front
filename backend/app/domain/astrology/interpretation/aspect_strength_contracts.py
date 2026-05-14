"""Contrats canoniques de force astrologique des aspects.

Ce module expose une echelle normalisee et des raisons enumerees pour eviter
les seuils libres dans les consommateurs de runtime aspect.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AspectStrengthReason(StrEnum):
    """Raison canonique contribuant a la force astrologique d'un aspect."""

    MAJOR_ASPECT = "major_aspect"
    MINOR_ASPECT = "minor_aspect"
    ADVANCED_ASPECT = "advanced_aspect"
    EXACT_ORB = "exact_orb"
    TIGHT_ORB = "tight_orb"
    MODERATE_ORB = "moderate_orb"
    WIDE_ORB = "wide_orb"
    LUMINARY_PARTICIPANT = "luminary_participant"
    ANGLE_PARTICIPANT = "angle_participant"
    TRANSPERSONAL_PAIR = "transpersonal_pair"
    APPLYING_PHASE = "applying_phase"
    SEPARATING_PHASE = "separating_phase"


class AspectStrengthLevel(StrEnum):
    """Niveau qualitatif stable derive du score normalise."""

    LOW = "low"
    MODERATE = "moderate"
    STRONG = "strong"
    DOMINANT = "dominant"


@dataclass(frozen=True, slots=True)
class AspectStrengthRuntimeData:
    """Contrat de force aspect base sur score normalise et raisons enumerees."""

    normalized_score: float
    level: AspectStrengthLevel
    is_exact: bool
    is_tight: bool
    reasons: tuple[AspectStrengthReason, ...]

    def __post_init__(self) -> None:
        """Garantit une echelle bornee et des raisons strictement enumerees."""
        if not 0.0 <= self.normalized_score <= 1.0:
            raise ValueError("aspect strength normalized_score must be between 0 and 1")
        if not self.reasons:
            raise ValueError("aspect strength requires at least one reason")


def resolve_aspect_strength_level(normalized_score: float) -> AspectStrengthLevel:
    """Qualifie un score de force aspect dans l'echelle normalisee `0.0..1.0`."""
    if normalized_score >= 0.85:
        return AspectStrengthLevel.DOMINANT
    if normalized_score >= 0.65:
        return AspectStrengthLevel.STRONG
    if normalized_score >= 0.35:
        return AspectStrengthLevel.MODERATE
    return AspectStrengthLevel.LOW

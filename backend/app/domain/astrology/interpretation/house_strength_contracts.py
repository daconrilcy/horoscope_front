"""Contrats canoniques de force interpretative des maisons.

Ce module centralise les raisons, niveaux et echelles normalisees utilises par
l'interpretation astrologique pure avant toute projection produit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HouseStrengthReason(StrEnum):
    """Raison canonique contribuant a la force astrologique d'une maison."""

    BASELINE_HOUSE = "baseline_house"
    ANGULAR_HOUSE = "angular_house"
    SUCCEDENT_HOUSE = "succedent_house"
    CADENT_HOUSE = "cadent_house"
    OCCUPANTS_PRESENT = "occupants_present"
    STELLIUM_PRESENT = "stellium_present"
    LUMINARY_PRESENT = "luminary_present"
    RULER_IN_ANGULAR_HOUSE = "ruler_in_angular_house"
    RULER_IN_OWN_SIGN = "ruler_in_own_sign"
    ASC_ANGLE_PROXIMITY = "asc_angle_proximity"
    MC_ANGLE_PROXIMITY = "mc_angle_proximity"


class HouseStrengthLevel(StrEnum):
    """Niveau qualitatif stable derive du score normalise."""

    LOW = "low"
    MODERATE = "moderate"
    DOMINANT = "dominant"


@dataclass(frozen=True, slots=True)
class HouseStrengthModifiers:
    """Modificateurs astrologiques explicites appliques au score normalise."""

    angularity_modifier: float | None = None
    occupancy_modifier: float | None = None
    ruler_condition_modifier: float | None = None


def resolve_house_strength_level(normalized_score: float) -> HouseStrengthLevel:
    """Qualifie un score de force maison dans l'echelle normalisee `0.0..1.0`."""
    if normalized_score >= 0.6:
        return HouseStrengthLevel.DOMINANT
    if normalized_score >= 0.25:
        return HouseStrengthLevel.MODERATE
    return HouseStrengthLevel.LOW

"""Evaluation astrologique de la force des maisons.

Ce module transforme les faits runtime des maisons en raisons astrologiques
explicables, sans categorie produit ni poids de prediction.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.astrology.celestial_runtime_catalog import CelestialRuntimeCatalog
from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
    HouseStrengthRuntimeData,
)

from .house_strength_contracts import HouseStrengthModifiers, HouseStrengthReason


class HouseStrengthEvaluator:
    """Calcule la force astrologique d'une maison a partir du runtime natal."""

    def __init__(self, celestial_catalog: CelestialRuntimeCatalog | None = None) -> None:
        """Initialise l'evaluateur avec les classifications du referentiel."""
        self._celestial_catalog = celestial_catalog or CelestialRuntimeCatalog.empty()

    def evaluate(
        self,
        *,
        house_number: int,
        occupants: Sequence[HouseOccupantRuntimeData],
        ruler: HouseRulerRuntimeData | None,
        sign_rulerships: Mapping[str, str],
    ) -> HouseStrengthRuntimeData:
        """Retourne un score normalise et ses raisons astrologiques."""
        score = 0.05
        reasons = list((HouseStrengthReason.BASELINE_HOUSE,))
        angularity_modifier = 0.0
        occupancy_modifier = 0.0
        ruler_condition_modifier = 0.0

        if house_number in self._celestial_catalog.angular_house_numbers:
            angularity_modifier += 0.25
            reasons.append(HouseStrengthReason.ANGULAR_HOUSE)
        elif house_number in self._celestial_catalog.succedent_house_numbers:
            angularity_modifier += 0.12
            reasons.append(HouseStrengthReason.SUCCEDENT_HOUSE)
        else:
            reasons.append(HouseStrengthReason.CADENT_HOUSE)

        occupant_count = len(occupants)
        if occupant_count:
            occupancy_modifier += min(0.3, 0.1 * occupant_count)
            reasons.append(HouseStrengthReason.OCCUPANTS_PRESENT)
        if occupant_count >= 3:
            occupancy_modifier += 0.18
            reasons.append(HouseStrengthReason.STELLIUM_PRESENT)

        if any(self._celestial_catalog.is_luminary(occupant.planet) for occupant in occupants):
            occupancy_modifier += 0.15
            reasons.append(HouseStrengthReason.LUMINARY_PRESENT)

        if ruler is not None:
            if ruler.house in self._celestial_catalog.angular_house_numbers:
                ruler_condition_modifier += 0.12
                reasons.append(HouseStrengthReason.RULER_IN_ANGULAR_HOUSE)
            if ruler.sign is not None and sign_rulerships.get(ruler.sign) == ruler.planet:
                ruler_condition_modifier += 0.12
                reasons.append(HouseStrengthReason.RULER_IN_OWN_SIGN)

        if house_number == _first_angle_house(self._celestial_catalog, "asc"):
            angularity_modifier += 0.08
            reasons.append(HouseStrengthReason.ASC_ANGLE_PROXIMITY)
        elif house_number == _first_angle_house(self._celestial_catalog, "mc"):
            angularity_modifier += 0.08
            reasons.append(HouseStrengthReason.MC_ANGLE_PROXIMITY)

        normalized_score = (
            score + angularity_modifier + occupancy_modifier + ruler_condition_modifier
        )
        return HouseStrengthRuntimeData.from_parts(
            normalized_score=normalized_score,
            reasons=tuple(reasons),
            modifiers=HouseStrengthModifiers(
                angularity_modifier=round(angularity_modifier, 2),
                occupancy_modifier=round(occupancy_modifier, 2),
                ruler_condition_modifier=round(ruler_condition_modifier, 2),
            ),
        )


def _first_angle_house(celestial_catalog: CelestialRuntimeCatalog, angle_code: str) -> int | None:
    """Retourne la maison associee a un angle quand le referentiel la fournit."""
    return celestial_catalog.house_for_angle(angle_code)

"""Scoring interprétatif déterministe de la dominance des maisons."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
    HouseStrengthRuntimeData,
)

ANGULAR_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
LUMINARIES = {"sun", "moon"}
DOMINANT_THRESHOLD = 0.6


def calculate_house_strength(
    *,
    house_number: int,
    occupants: Sequence[HouseOccupantRuntimeData],
    ruler: HouseRulerRuntimeData | None,
    sign_rulerships: Mapping[str, str],
) -> HouseStrengthRuntimeData:
    """Calcule une force de maison explicable à partir du runtime natal."""
    score = 0.05
    reasons: list[str] = ["baseline_house"]

    if house_number in ANGULAR_HOUSES:
        score += 0.25
        reasons.append("angular_house")
    elif house_number in SUCCEDENT_HOUSES:
        score += 0.12
        reasons.append("succedent_house")
    else:
        reasons.append("cadent_house")

    occupant_count = len(occupants)
    if occupant_count:
        score += min(0.3, 0.1 * occupant_count)
        reasons.append("occupants_present")
    if occupant_count >= 3:
        score += 0.18
        reasons.append("stellium_present")

    if any(occupant.planet in LUMINARIES for occupant in occupants):
        score += 0.15
        reasons.append("luminary_present")

    if ruler is not None:
        if ruler.house in ANGULAR_HOUSES:
            score += 0.12
            reasons.append("ruler_in_angular_house")
        if ruler.sign is not None and sign_rulerships.get(ruler.sign) == ruler.planet:
            score += 0.12
            reasons.append("ruler_in_own_sign")

    if house_number == 1:
        score += 0.08
        reasons.append("asc_angle_proximity")
    elif house_number == 10:
        score += 0.08
        reasons.append("mc_angle_proximity")

    normalized_score = round(min(score, 1.0), 2)
    return HouseStrengthRuntimeData(
        score=normalized_score,
        dominant=normalized_score >= DOMINANT_THRESHOLD,
        reasons=reasons,
    )

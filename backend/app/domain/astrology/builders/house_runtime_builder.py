"""Assemblage des maisons natales runtime enrichies.

Ce module construit les faits de maisons et delegue leur interpretation pure.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Protocol

from app.domain.astrology.calculators.contained_signs import resolve_contained_signs
from app.domain.astrology.calculators.intercepted_signs import resolve_intercepted_signs
from app.domain.astrology.constants.house_axes import resolve_house_axis
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation import HouseStrengthEvaluator
from app.domain.astrology.runtime.house_runtime_data import (
    HouseAxisRuntimeData,
    HouseRulerRuntimeData,
    HouseRuntimeData,
    resolve_house_kind,
)
from app.domain.astrology.zodiac import sign_from_longitude

from .house_occupants_builder import PlanetRuntimeData, build_house_occupants


class HouseCuspRuntimeData(Protocol):
    """Contrat minimal d'une cuspide de maison avant enrichissement."""

    number: int
    cusp_longitude: float


def build_house_runtime_data(
    *,
    houses: Iterable[HouseCuspRuntimeData],
    planets: Iterable[PlanetRuntimeData],
    house_rulers: Iterable[HouseRulerResult],
    house_system: object,
    sign_rulerships: Mapping[str, str],
) -> list[HouseRuntimeData]:
    """Construit les maisons enrichies sans recalculer les maîtres."""
    ordered_houses = sorted(houses, key=lambda item: item.number)
    rulers_by_house = {ruler.house_number: ruler for ruler in house_rulers}
    occupants_by_house = build_house_occupants(planets)
    is_whole_sign = _normalize_house_system(house_system) == "whole_sign"
    strength_evaluator = HouseStrengthEvaluator()
    runtime_houses: list[HouseRuntimeData] = []

    for index, house in enumerate(ordered_houses):
        next_house = ordered_houses[(index + 1) % len(ordered_houses)]
        cusp_sign = sign_from_longitude(house.cusp_longitude)
        next_cusp_sign = sign_from_longitude(next_house.cusp_longitude)
        contained_signs = resolve_contained_signs(house.cusp_longitude, next_house.cusp_longitude)
        intercepted_signs = (
            []
            if is_whole_sign
            else resolve_intercepted_signs(contained_signs, cusp_sign, next_cusp_sign)
        )
        ruler = _build_runtime_ruler(rulers_by_house.get(house.number))
        occupants = occupants_by_house.get(house.number, [])
        strength = strength_evaluator.evaluate(
            house_number=house.number,
            occupants=occupants,
            ruler=ruler,
            sign_rulerships=sign_rulerships,
        )
        axis_data = resolve_house_axis(house.number)

        runtime_houses.append(
            HouseRuntimeData(
                number=house.number,
                cusp_longitude=house.cusp_longitude,
                cusp_sign=cusp_sign,
                house_kind=resolve_house_kind(house.number),
                contained_signs=contained_signs,
                intercepted_signs=intercepted_signs,
                ruler=ruler,
                occupants=occupants,
                axis=HouseAxisRuntimeData(
                    opposite_house=int(axis_data["opposite_house"]),
                    theme=str(axis_data["theme"]),
                ),
                strength=strength,
            )
        )

    return runtime_houses


def _build_runtime_ruler(ruler: HouseRulerResult | None) -> HouseRulerRuntimeData | None:
    """Projette un ruler déjà résolu dans la structure runtime de maison."""
    if ruler is None:
        return None
    return HouseRulerRuntimeData(
        planet=ruler.ruler_planet,
        sign=ruler.ruler_planet_sign,
        house=ruler.ruler_planet_house,
    )


def _normalize_house_system(house_system: object) -> str:
    """Normalise le système de maisons reçu du pipeline ou des tests."""
    value = getattr(house_system, "value", house_system)
    return str(value).strip().lower()

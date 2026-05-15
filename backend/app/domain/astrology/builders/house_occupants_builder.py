"""Construction des occupants de maisons à partir des planètes runtime."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.astrology.runtime.house_runtime_data import HouseOccupantRuntimeData

DOMINANT_PLANET_CODES = frozenset(planet_codes()[:2])


class PlanetRuntimeData(Protocol):
    """Contrat minimal des planètes utiles aux occupants de maison."""

    planet_code: str
    sign_code: str
    longitude: float
    house_number: int | None


def build_house_occupants(
    planets: Iterable[PlanetRuntimeData],
) -> dict[int, list[HouseOccupantRuntimeData]]:
    """Regroupe les planètes par maison natale assignée."""
    occupants_by_house: dict[int, list[HouseOccupantRuntimeData]] = {
        number: [] for number in range(1, 13)
    }

    for planet in planets:
        if planet.house_number is None:
            continue
        if not 1 <= planet.house_number <= 12:
            continue
        occupants_by_house[planet.house_number].append(
            HouseOccupantRuntimeData(
                planet=planet.planet_code,
                sign=planet.sign_code,
                longitude=planet.longitude,
                is_dominant=planet.planet_code in DOMINANT_PLANET_CODES,
            )
        )

    return occupants_by_house

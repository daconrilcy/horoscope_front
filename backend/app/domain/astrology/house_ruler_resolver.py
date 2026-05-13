"""Résolution runtime des maîtres de maisons pour un thème natal."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Protocol

from pydantic import BaseModel

from app.domain.astrology.zodiac import ZODIAC_SIGNS, sign_from_longitude

DEFAULT_TRADITIONAL_SIGN_RULERSHIPS: dict[str, str] = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}
"""Maîtrises traditionnelles stables utilisées pour les fixtures sans base SQL."""


class HouseRulerResult(BaseModel):
    """Placement public du maître planétaire d'une maison natale."""

    house_number: int
    cusp_sign: str
    ruler_planet: str
    ruler_planet_sign: str | None = None
    ruler_planet_house: int | None = None


class HouseLike(Protocol):
    """Contrat minimal attendu pour une cuspide de maison."""

    number: int
    cusp_longitude: float


class PlanetLike(Protocol):
    """Contrat minimal attendu pour la position d'une planète."""

    planet_code: str
    sign_code: str
    house_number: int | None


class HouseRulerResolutionError(ValueError):
    """Erreur levée quand les maîtrises de maisons ne sont pas résolubles."""


class HouseRulerResolver:
    """Déduit les maîtres de maisons à partir des cuspides et des planètes."""

    def __init__(self, sign_rulerships: Mapping[str, str] | None = None) -> None:
        """Initialise le resolver avec le mapping signe -> planète maîtresse."""
        normalized = self._normalize_rulerships(sign_rulerships or {})
        missing_signs = sorted(set(ZODIAC_SIGNS) - set(normalized))
        if missing_signs:
            raise HouseRulerResolutionError("missing sign rulerships: " + ", ".join(missing_signs))
        self._sign_rulerships = normalized

    def resolve(
        self,
        houses: Iterable[HouseLike],
        planets: Iterable[PlanetLike],
    ) -> list[HouseRulerResult]:
        """Produit le placement du maître planétaire pour chaque maison."""
        planets_by_code = {self._normalize_code(planet.planet_code): planet for planet in planets}
        house_rulers: list[HouseRulerResult] = []

        for house in sorted(houses, key=lambda item: item.number):
            if not 1 <= house.number <= 12:
                raise HouseRulerResolutionError(f"invalid house number: {house.number}")
            cusp_sign = sign_from_longitude(house.cusp_longitude)
            ruler_planet = self._sign_rulerships[cusp_sign]
            ruler_position = planets_by_code.get(ruler_planet)
            house_rulers.append(
                HouseRulerResult(
                    house_number=house.number,
                    cusp_sign=cusp_sign,
                    ruler_planet=ruler_planet,
                    ruler_planet_sign=(
                        ruler_position.sign_code if ruler_position is not None else None
                    ),
                    ruler_planet_house=(
                        ruler_position.house_number if ruler_position is not None else None
                    ),
                )
            )

        return house_rulers

    @staticmethod
    def _normalize_rulerships(sign_rulerships: Mapping[str, str]) -> dict[str, str]:
        """Normalise les codes issus du référentiel de dignités planétaires."""
        return {
            HouseRulerResolver._normalize_code(sign): HouseRulerResolver._normalize_code(planet)
            for sign, planet in sign_rulerships.items()
            if HouseRulerResolver._normalize_code(sign)
            and HouseRulerResolver._normalize_code(planet)
        }

    @staticmethod
    def _normalize_code(value: Any) -> str:
        """Retourne un code métier stable en minuscules."""
        return str(value).strip().lower()

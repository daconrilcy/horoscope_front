"""Contrat runtime des classifications celestes issues du referentiel."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


@dataclass(frozen=True, slots=True)
class CelestialRuntimeCatalog:
    """Expose les classifications celestes derivees des tables de reference."""

    light_body_codes: frozenset[str]
    outer_planet_codes: frozenset[str]
    angle_point_codes: frozenset[str]
    angular_house_numbers: frozenset[int]
    succedent_house_numbers: frozenset[int]
    body_class_by_code: Mapping[str, str]
    angle_house_by_code: Mapping[str, int]

    def __post_init__(self) -> None:
        """Fige la carte des classes pour eviter les mutations accidentelles."""
        object.__setattr__(
            self,
            "body_class_by_code",
            MappingProxyType(
                {
                    str(code).strip().lower(): str(body_class).strip().lower()
                    for code, body_class in self.body_class_by_code.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "angle_house_by_code",
            MappingProxyType(
                {
                    str(code).strip().lower(): int(house_number)
                    for code, house_number in self.angle_house_by_code.items()
                }
            ),
        )

    @classmethod
    def from_runtime_reference(
        cls,
        runtime_reference: AstrologyRuntimeReference,
    ) -> CelestialRuntimeCatalog:
        """Construit le catalogue depuis les planetes et angles persistés."""
        body_class_by_code = {
            item.code.strip().lower(): item.body_class.strip().lower()
            for item in runtime_reference.planets.items
            if item.code.strip() and item.body_class is not None and item.body_class.strip()
        }
        light_body_codes = frozenset(
            item.code.strip().lower()
            for item in runtime_reference.planets.items
            if item.code.strip()
            and (
                item.is_luminary or body_class_by_code.get(item.code.strip().lower()) == "luminary"
            )
        )
        outer_planet_codes = frozenset(
            code
            for code, body_class in body_class_by_code.items()
            if body_class == "transpersonal_planet"
        )
        angle_point_codes = frozenset(
            item.code.strip().lower()
            for item in runtime_reference.angle_points.items
            if item.code.strip()
        )
        angular_house_numbers = frozenset(
            item.associated_house for item in runtime_reference.angle_points.items
        )
        angle_house_by_code = {
            item.code.strip().lower(): item.associated_house
            for item in runtime_reference.angle_points.items
            if item.code.strip()
        }
        return cls(
            light_body_codes=light_body_codes,
            outer_planet_codes=outer_planet_codes,
            angle_point_codes=angle_point_codes,
            angular_house_numbers=angular_house_numbers,
            succedent_house_numbers=_succedent_houses(angular_house_numbers),
            body_class_by_code=body_class_by_code,
            angle_house_by_code=angle_house_by_code,
        )

    @classmethod
    def empty(cls) -> CelestialRuntimeCatalog:
        """Retourne un catalogue vide pour les tests très isolés."""
        return cls(
            light_body_codes=frozenset(),
            outer_planet_codes=frozenset(),
            angle_point_codes=frozenset(),
            angular_house_numbers=frozenset(),
            succedent_house_numbers=frozenset(),
            body_class_by_code={},
            angle_house_by_code={},
        )

    def body_type_for_code(self, code: str) -> str:
        """Retourne le type runtime d'un corps ou point astrologique."""
        normalized_code = code.strip().lower()
        if normalized_code in self.angle_point_codes:
            return "angle"
        return self.body_class_by_code.get(normalized_code, "point")

    def is_luminary(self, code: str) -> bool:
        """Indique si le code designe un luminaire du referentiel."""
        return code.strip().lower() in self.light_body_codes

    def is_transpersonal(self, code: str) -> bool:
        """Indique si le code designe une planete transpersonnelle."""
        return code.strip().lower() in self.outer_planet_codes

    def is_angle_point(self, code: str) -> bool:
        """Indique si le code designe un angle du theme."""
        return code.strip().lower() in self.angle_point_codes

    def house_for_angle(self, code: str) -> int | None:
        """Retourne la maison associee a un angle du referentiel."""
        return self.angle_house_by_code.get(code.strip().lower())


def _succedent_houses(angular_house_numbers: frozenset[int]) -> frozenset[int]:
    """Derive les maisons succedentes depuis les maisons associees aux angles."""
    return frozenset((house_number % 12) + 1 for house_number in angular_house_numbers)


def is_major_aspect_code(aspect: object) -> bool:
    """Lit le statut majeur depuis un contrat d'aspect deja valide."""
    is_major = getattr(aspect, "is_major", None)
    if isinstance(is_major, bool):
        return is_major
    raise TypeError("is_major_aspect_code requires a typed aspect contract")

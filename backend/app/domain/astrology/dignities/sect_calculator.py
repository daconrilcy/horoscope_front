"""Calcul de secte diurne ou nocturne pour les dignites accidentelles."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.dignities.contracts import PlanetDignityInput
from app.domain.astrology.runtime.runtime_reference import PlanetDignityReferenceSet


class SectCalculator:
    """Determine la secte du theme depuis la position objective du Soleil."""

    def calculate(
        self,
        planets: Iterable[PlanetDignityInput],
        dignity_reference: PlanetDignityReferenceSet,
    ) -> str:
        """Retourne la secte depuis les regles horizon du runtime."""
        above_horizon_houses = self._houses_for_rule(dignity_reference, "above_horizon")
        below_horizon_houses = self._houses_for_rule(dignity_reference, "below_horizon")
        for planet in planets:
            if planet.planet_code == "sun":
                if planet.house_number in above_horizon_houses:
                    return "day"
                if planet.house_number in below_horizon_houses:
                    return "night"
                raise ValueError("sun house is outside configured horizon dignity rules")
        raise ValueError("sect calculation requires sun position")

    def _houses_for_rule(
        self,
        dignity_reference: PlanetDignityReferenceSet,
        dignity_type_code: str,
    ) -> frozenset[int]:
        """Extrait les maisons d'horizon depuis les conditions runtime."""
        for rule in dignity_reference.accidental_rules:
            if rule.dignity_type_code != dignity_type_code:
                continue
            for condition in rule.conditions:
                if condition.key == "house_codes" and isinstance(condition.value, tuple):
                    return frozenset(int(value) for value in condition.value)
        raise ValueError(f"missing horizon dignity rule: {dignity_type_code}")

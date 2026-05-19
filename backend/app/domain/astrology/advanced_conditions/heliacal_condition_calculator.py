"""Calcul pur des conditions solaires avancees."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.domain.astrology.advanced_conditions._dignity_rule_helpers import accidental_matches
from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.dignities.contracts import PlanetDignityResult


class HeliacalConditionCalculator:
    """Projette les conditions heliacales et orientations deja gouvernees."""

    def calculate(
        self,
        positions: Sequence[Any],
        dignities_by_planet: Mapping[str, PlanetDignityResult],
        emit_condition,
        *,
        condition_type_codes: frozenset[str] | None = None,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne les conditions solaires V1."""
        conditions: list[AdvancedPlanetaryCondition] = []
        active_codes = condition_type_codes or frozenset()
        sun = self._position_by_code(positions, "sun")
        for position in positions:
            dignity = dignities_by_planet.get(position.planet_code)
            for code in accidental_matches(dignity, frozenset({"oriental", "occidental"})):
                conditions.append(
                    emit_condition(
                        condition_code=code,
                        condition_type_code=code,
                        source_planet_code=position.planet_code,
                        target_planet_code="sun",
                        reason=f"{position.planet_code} is {code} relative to sun.",
                    )
                )
            for code in accidental_matches(
                dignity,
                frozenset({"heliacal_rising", "heliacal_setting"}),
            ):
                conditions.append(
                    emit_condition(
                        condition_code=code,
                        condition_type_code=code,
                        source_planet_code=position.planet_code,
                        target_planet_code="sun",
                        reason=f"{position.planet_code} matches solar phase {code}.",
                    )
                )
            if sun is None or position.planet_code == "sun":
                continue
            inferred_code = self._heliacal_code(position.longitude, sun.longitude)
            if inferred_code is not None and inferred_code in active_codes:
                conditions.append(
                    emit_condition(
                        condition_code=inferred_code,
                        condition_type_code=inferred_code,
                        source_planet_code=position.planet_code,
                        target_planet_code="sun",
                        reason=f"{position.planet_code} has inferred solar phase {inferred_code}.",
                    )
                )
        return tuple(conditions)

    def _position_by_code(self, positions: Sequence[Any], planet_code: str) -> Any | None:
        """Retourne une position par code planetaire."""
        for position in positions:
            if position.planet_code == planet_code:
                return position
        return None

    def _heliacal_code(self, longitude: float, sun_longitude: float) -> str | None:
        """Classe une phase solaire V1 depuis l'avance zodiacale relative."""
        forward_distance = (longitude - sun_longitude) % 360.0
        if forward_distance == 0.0:
            return None
        if 0.0 < forward_distance < 180.0:
            return "heliacal_rising"
        return "heliacal_setting"

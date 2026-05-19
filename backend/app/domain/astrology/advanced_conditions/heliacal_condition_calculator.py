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
                solar_phase_code = self._solar_phase_code(code)
                if solar_phase_code is not None and solar_phase_code in active_codes:
                    conditions.append(
                        emit_condition(
                            condition_code=solar_phase_code,
                            condition_type_code=solar_phase_code,
                            source_planet_code=position.planet_code,
                            target_planet_code="sun",
                            reason=(
                                f"{position.planet_code} matches runtime solar phase "
                                f"{solar_phase_code}."
                            ),
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
        return tuple(conditions)

    def _solar_phase_code(self, orientation_code: str) -> str | None:
        """Derive la phase solaire avancee depuis la condition heliacale runtime."""
        if orientation_code == "oriental":
            return "heliacal_rising"
        if orientation_code == "occidental":
            return "heliacal_setting"
        return None

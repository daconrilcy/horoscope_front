"""Calcul pur des conditions de secte avancees."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.domain.astrology.advanced_conditions._dignity_rule_helpers import accidental_matches
from app.domain.astrology.advanced_conditions.contracts import AdvancedPlanetaryCondition
from app.domain.astrology.dignities.contracts import PlanetDignityResult


class HayzCalculator:
    """Projette hayz et hors-secte depuis les regles accidentelles runtime."""

    def calculate(
        self,
        positions: Sequence[Any],
        dignities_by_planet: Mapping[str, PlanetDignityResult],
        emit_condition,
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Retourne les conditions de secte deja prouvees par les dignites."""
        conditions: list[AdvancedPlanetaryCondition] = []
        for position in positions:
            dignity = dignities_by_planet.get(position.planet_code)
            for code in accidental_matches(dignity, frozenset({"hayz", "out_of_sect"})):
                conditions.append(
                    emit_condition(
                        condition_code=code,
                        condition_type_code=code,
                        source_planet_code=position.planet_code,
                        target_planet_code=None,
                        reason=f"{position.planet_code} matches accidental dignity {code}.",
                    )
                )
        return tuple(conditions)

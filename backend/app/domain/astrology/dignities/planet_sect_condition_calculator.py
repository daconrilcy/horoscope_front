"""Calcul pur de la condition de secte planetaire depuis le runtime."""

from __future__ import annotations

from app.domain.astrology.dignities.contracts import (
    ChartSectResult,
    PlanetDignityInput,
    PlanetSectCondition,
)
from app.domain.astrology.runtime.runtime_reference import PlanetDignityReferenceSet

_CALCULATION_BASIS = "chart_sect_vs_planet_intrinsic_sect"
_UNKNOWN_REFERENCE_SYSTEM = "runtime_accidental_sect_rules"


class PlanetSectConditionCalculator:
    """Derive le statut de secte d'une planete sans recalculer la secte globale."""

    def calculate(
        self,
        planet: PlanetDignityInput,
        *,
        chart_sect: ChartSectResult,
        dignity_reference: PlanetDignityReferenceSet,
    ) -> PlanetSectCondition:
        """Retourne la condition normalisee depuis les regles runtime de secte."""
        intrinsic_sect, reference_system = self._intrinsic_sect(
            planet.planet_code,
            dignity_reference,
        )
        condition = self._condition(chart_sect.chart_sect, intrinsic_sect)
        return PlanetSectCondition(
            planet_code=planet.planet_code,
            chart_sect=chart_sect.chart_sect,
            intrinsic_sect=intrinsic_sect,
            planet_sect_condition=condition,
            is_in_sect=condition == "in_sect",
            is_out_of_sect=condition == "out_of_sect",
            calculation_basis=_CALCULATION_BASIS,
            reference_system=reference_system,
        )

    def _intrinsic_sect(
        self,
        planet_code: str,
        dignity_reference: PlanetDignityReferenceSet,
    ) -> tuple[str, str]:
        """Lit la secte intrinseque a partir des regles accidentelles typées."""
        in_sect_codes: set[str] = set()
        reference_systems: set[str] = set()
        for rule in dignity_reference.accidental_rules:
            if rule.dignity_type_code != "in_sect" or rule.planet_code != planet_code:
                continue
            chart_sect_code = self._chart_sect_code(rule.conditions)
            if chart_sect_code is None:
                continue
            in_sect_codes.add(chart_sect_code)
            if rule.system_code.strip():
                reference_systems.add(rule.system_code)

        reference_system = (
            next(iter(sorted(reference_systems)))
            if reference_systems
            else _UNKNOWN_REFERENCE_SYSTEM
        )
        if {"day", "night"}.issubset(in_sect_codes) or "all" in in_sect_codes:
            return "common", reference_system
        if "day" in in_sect_codes:
            return "diurnal", reference_system
        if "night" in in_sect_codes:
            return "nocturnal", reference_system
        return "unknown", reference_system

    def _chart_sect_code(self, conditions: object) -> str | None:
        """Extrait le code de secte declare par une regle runtime."""
        for condition in conditions:  # type: ignore[union-attr]
            if condition.key == "chart_sect_code" and isinstance(condition.value, str):
                return condition.value
        return None

    def _condition(self, chart_sect: str, intrinsic_sect: str) -> str:
        """Compare la secte du theme et la secte intrinseque de la planete."""
        if intrinsic_sect == "diurnal":
            return "in_sect" if chart_sect == "day" else "out_of_sect"
        if intrinsic_sect == "nocturnal":
            return "in_sect" if chart_sect == "night" else "out_of_sect"
        if intrinsic_sect == "common":
            return "variable_by_condition"
        if intrinsic_sect == "neutral":
            return "neutral_to_sect"
        return "unknown"

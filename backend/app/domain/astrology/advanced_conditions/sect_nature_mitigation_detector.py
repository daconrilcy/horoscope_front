"""Detection factuelle de la mitigation des natures planetaires par la secte."""

from __future__ import annotations

from collections.abc import Callable

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    SectNatureMitigationCondition,
)
from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class SectNatureMitigationDetector:
    """Construit les faits CS-206 depuis le runtime et PlanetSectCondition."""

    condition_family = "sect_nature_mitigation"

    def detect(
        self,
        *,
        dignities: tuple[PlanetDignityResult, ...],
        runtime_reference: AstrologyRuntimeReference,
    ) -> tuple[SectNatureMitigationCondition, ...]:
        """Retourne les contrats de mitigation evaluables sans emission scoree."""
        facts: list[SectNatureMitigationCondition] = []
        for dignity in dignities:
            sect_condition = dignity.sect_condition
            if sect_condition is None:
                continue
            nature = runtime_reference.planet_natures.nature_for_planet(dignity.planet_code)
            normalized_nature = nature if nature is not None else "unknown"
            condition_code, mitigation_state = self._condition_code_and_state(
                planet_nature=normalized_nature,
                is_in_sect=sect_condition.is_in_sect,
                is_out_of_sect=sect_condition.is_out_of_sect,
            )
            facts.append(
                SectNatureMitigationCondition(
                    planet_code=dignity.planet_code,
                    planet_nature=normalized_nature,
                    chart_sect=sect_condition.chart_sect,
                    intrinsic_sect=sect_condition.intrinsic_sect,
                    planet_sect_condition=sect_condition.planet_sect_condition,
                    is_in_sect=sect_condition.is_in_sect,
                    is_out_of_sect=sect_condition.is_out_of_sect,
                    mitigation_state=mitigation_state,
                    condition_code=condition_code,
                    condition_family=self.condition_family,
                    calculation_basis="runtime_planet_nature_plus_planet_sect_condition",
                    reference_system=sect_condition.reference_system,
                    evidence=(
                        "planet nature loaded from AstrologyRuntimeReference.planet_natures",
                        "sect condition loaded from PlanetSectCondition",
                    ),
                )
            )
        return tuple(facts)

    def calculate(
        self,
        *,
        dignities: tuple[PlanetDignityResult, ...],
        runtime_reference: AstrologyRuntimeReference,
        emit_condition: Callable[..., AdvancedPlanetaryCondition],
        condition_type_codes: frozenset[str],
    ) -> tuple[AdvancedPlanetaryCondition, ...]:
        """Emet les conditions avancees uniquement si le runtime les supporte."""
        if self.condition_family not in condition_type_codes:
            return ()
        return tuple(
            emit_condition(
                condition_code=fact.condition_code,
                condition_type_code=self.condition_family,
                source_planet_code=fact.planet_code,
                target_planet_code=None,
                reason=(
                    f"{fact.planet_code} has runtime nature {fact.planet_nature} "
                    f"and sect condition {fact.planet_sect_condition}."
                ),
                calculation_facts=self.to_calculation_facts(fact),
            )
            for fact in self.detect(dignities=dignities, runtime_reference=runtime_reference)
        )

    def to_calculation_facts(self, fact: SectNatureMitigationCondition) -> dict[str, object]:
        """Convertit le contrat en faits serialisables par les couches aval."""
        return {
            "planet_code": fact.planet_code,
            "planet_nature": fact.planet_nature,
            "chart_sect": fact.chart_sect,
            "intrinsic_sect": fact.intrinsic_sect,
            "planet_sect_condition": fact.planet_sect_condition,
            "is_in_sect": fact.is_in_sect,
            "is_out_of_sect": fact.is_out_of_sect,
            "mitigation_state": fact.mitigation_state,
            "condition_code": fact.condition_code,
            "condition_family": fact.condition_family,
            "calculation_basis": fact.calculation_basis,
            "reference_system": fact.reference_system,
            "evidence": tuple(fact.evidence),
        }

    def _condition_code_and_state(
        self,
        *,
        planet_nature: str,
        is_in_sect: bool,
        is_out_of_sect: bool,
    ) -> tuple[str, str]:
        """Applique la table CS-206 sans connaitre les noms des planetes."""
        if planet_nature == "malefic" and is_in_sect:
            return "malefic_mitigated_by_sect", "mitigated"
        if planet_nature == "malefic" and is_out_of_sect:
            return "malefic_aggravated_out_of_sect", "aggravated"
        if planet_nature == "benefic" and is_in_sect:
            return "benefic_supported_by_sect", "supported"
        if planet_nature == "benefic" and is_out_of_sect:
            return "benefic_weakened_out_of_sect", "weakened"
        if planet_nature in {"mixed", "neutral", "luminary"}:
            return "sect_nature_neutral", "neutral"
        return "sect_nature_unknown", "unknown"

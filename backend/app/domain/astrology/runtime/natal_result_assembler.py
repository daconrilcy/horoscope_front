# Assemblage du resultat natal public depuis les sorties canoniques du graphe.
"""Transforme les outputs de `natal_chart_v1` en `NatalResult` compatible."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import NatalCalculationError, NatalResult
from app.domain.astrology.runtime.calculation_graph_runner import CalculationGraphContext
from app.domain.astrology.runtime.natal_calculation_nodes import (
    NatalAdvancedConditionsOutput,
    NatalDignityOutput,
    NatalDominanceOutput,
    NatalFixedStarOutput,
    NatalInterpretationOutput,
)


class NatalResultAssembler:
    """Assemble le contrat natal historique depuis les sorties du graphe."""

    def assemble(self, context: CalculationGraphContext) -> NatalResult:
        """Construit `NatalResult` et signale tout output obligatoire manquant."""
        options = self._required(context, "calculation_options")
        dignity_output = self._typed(context, "dignities", NatalDignityOutput)
        advanced_output = self._typed(
            context,
            "advanced_conditions",
            NatalAdvancedConditionsOutput,
        )
        dominance_output = self._typed(context, "dominance", NatalDominanceOutput)
        interpretation_output = self._typed(
            context,
            "interpretation_input",
            NatalInterpretationOutput,
        )
        self._typed(
            context,
            "fixed_star_conjunctions",
            NatalFixedStarOutput,
        )
        return NatalResult(
            reference_version=self._runtime_reference(context).reference_version,
            ruleset_version=str(options["ruleset_version"]),
            house_system=self._required(context, "effective_house_system"),
            engine=str(options["engine"]),
            zodiac=options["zodiac"],
            frame=options["frame"],
            ayanamsa=options["ayanamsa"],
            altitude_m=options["altitude_m"],
            ephemeris_path_version=options["ephemeris_path_version"],
            ephemeris_path_hash=options["ephemeris_path_hash"],
            time_scale=self._required(context, "prepared_birth_data").time_scale,
            aspect_school=options["aspect_school_code"],
            aspect_rules_version=str(options["aspect_rules_version"]),
            prepared_input=self._required(context, "prepared_birth_data"),
            planet_positions=list(self._required(context, "planet_positions")),
            houses=list(self._required(context, "houses_runtime")),
            signs_runtime=list(self._required(context, "signs_runtime")),
            chart_balance=self._required(context, "chart_signature"),
            house_rulers=list(self._required(context, "house_rulerships")),
            astral_points=list(self._required(context, "astral_points")),
            dignity_sect=dignity_output.dignity_sect,
            dignities=list(dignity_output.dignities),
            condition_profiles=list(advanced_output.condition_profiles),
            condition_signals=list(advanced_output.condition_signals),
            advanced_conditions=list(advanced_output.advanced_conditions),
            advanced_planetary_conditions=self._required(context, "motion_visibility_payloads"),
            chart_objects=list(dominance_output.chart_objects),
            interpretation_profiles_by_planet=dignity_output.interpretation_profiles_by_planet,
            traditional_conditions=interpretation_output.traditional_conditions,
            dominant_planets=dominance_output.dominant_planets,
            interpretation_adapter=interpretation_output.interpretation_adapter,
            aspects=list(self._required(context, "aspects_runtime")),
        )

    def _typed(self, context: CalculationGraphContext, key: str, expected_type: type):
        """Retourne un output avec un message stable en cas de surface invalide."""
        value = self._required(context, key)
        if not isinstance(value, expected_type):
            raise NatalCalculationError(
                code="missing_graph_output",
                message=f"natal graph output '{key}' has invalid type",
                details={"output_key": key, "expected_type": expected_type.__name__},
            )
        return value

    def _required(self, context: CalculationGraphContext, key: str):
        """Retourne un output obligatoire avec message stable."""
        try:
            return context.get_required(key)
        except KeyError as error:
            raise NatalCalculationError(
                code="missing_graph_output",
                message=f"natal graph output '{key}' is required",
                details={"output_key": key},
            ) from error

    def _runtime_reference(self, context: CalculationGraphContext):
        """Retourne le referentiel runtime obligatoire."""
        return self._required(context, "runtime_reference")

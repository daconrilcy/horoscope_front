# Definition declarative du graphe de calcul natal runtime.
"""Expose le graphe natal sans executer ni importer le pipeline metier."""

from __future__ import annotations

from enum import StrEnum

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationInputDefinition,
    CalculationNodeDefinition,
)

NATAL_GRAPH_CODE = "natal_chart_v1"
NATAL_GRAPH_VERSION = "1"
CANONICAL_RUNTIME_TAG = "canonical_runtime"
COMPATIBILITY_PROJECTION_TAG = "compatibility_projection"
PUBLIC_PROJECTION_TAG = "public_projection"


class NatalCalculationNodeCode(StrEnum):
    """Codes stables des nodes documentant le pipeline natal."""

    PREPARE_BIRTH_DATA = "prepare_birth_data"
    PLANET_POSITIONS = "planet_positions"
    ASTRAL_POINT_POSITIONS = "astral_points"
    HOUSES_RAW = "houses_raw"
    HOUSES_RUNTIME = "houses_runtime"
    SIGNS_RUNTIME = "signs_runtime"
    CHART_OBJECTS = "chart_objects"
    ASPECTS_RUNTIME = "aspects_runtime"
    HOUSE_POSITIONS = "house_positions"
    HOUSE_RULERSHIPS = "house_rulerships"
    FIXED_STAR_CONJUNCTIONS = "fixed_star_conjunctions"
    ADVANCED_CONDITIONS = "advanced_conditions"
    MOTION_VISIBILITY_PAYLOADS = "motion_visibility_payloads"
    DIGNITIES = "dignities"
    DOMINANCE = "dominance"
    CHART_SIGNATURE = "chart_signature"
    INTERPRETATION_INPUT = "interpretation_input"
    PLANET_POSITIONS_PROJECTION = "planet_positions_projection"
    ASTRAL_POINTS_PROJECTION = "astral_points_projection"
    HOUSES_PROJECTION = "houses_projection"
    ASPECTS_PROJECTION = "aspects_projection"
    DIGNITY_RESULTS_PROJECTION = "dignity_results_projection"
    ADVANCED_CONDITIONS_PROJECTION = "advanced_conditions_projection"
    FIXED_STAR_CONJUNCTIONS_PROJECTION = "fixed_star_conjunctions_projection"
    PUBLIC_NATAL_RESULT = "public_natal_result"


def build_natal_calculation_graph_definition() -> CalculationGraphDefinition:
    """Construit la definition inspectable du graphe natal canonique."""
    return CalculationGraphDefinition(
        graph_code=NATAL_GRAPH_CODE,
        version=NATAL_GRAPH_VERSION,
        required_inputs=_build_required_inputs(),
        nodes=_build_nodes(),
    )


def _build_required_inputs() -> tuple[CalculationInputDefinition, ...]:
    """Declare les entrees minimales et derivees disponibles au graphe."""
    return (
        CalculationInputDefinition(key="birth_datetime", value_type="datetime"),
        CalculationInputDefinition(key="timezone", value_type="str"),
        CalculationInputDefinition(key="coordinates", value_type="Coordinates"),
        CalculationInputDefinition(key="house_system", value_type="str"),
        CalculationInputDefinition(key="zodiac_mode", value_type="str"),
        CalculationInputDefinition(key="runtime_reference", value_type="AstrologyRuntimeReference"),
        CalculationInputDefinition(key="locale", value_type="str"),
        CalculationInputDefinition(key="calculation_options", value_type="Mapping[str, object]"),
        CalculationInputDefinition(key="prepared_birth_data", value_type="BirthPreparedData"),
        CalculationInputDefinition(key="julian_day", value_type="float"),
        CalculationInputDefinition(key="effective_house_system", value_type="str"),
    )


def _build_nodes() -> tuple[CalculationNodeDefinition, ...]:
    """Declare les nodes dans un ordre lisible proche du pipeline procedural."""
    return (
        _canonical_node(
            NatalCalculationNodeCode.PREPARE_BIRTH_DATA,
            output_key="prepared_birth_data",
            depends_on=("birth_datetime", "timezone", "coordinates", "calculation_options"),
            calculator="prepare_birth_data",
        ),
        _canonical_node(
            NatalCalculationNodeCode.PLANET_POSITIONS,
            output_key="planet_positions",
            depends_on=("julian_day", "runtime_reference", "zodiac_mode", "houses_raw"),
            calculator="calculate_planet_positions",
        ),
        _canonical_node(
            NatalCalculationNodeCode.ASTRAL_POINT_POSITIONS,
            output_key="astral_points",
            depends_on=("julian_day", "runtime_reference", "zodiac_mode"),
            calculator="calculate_astral_points",
        ),
        _canonical_node(
            NatalCalculationNodeCode.HOUSES_RAW,
            output_key="houses_raw",
            depends_on=("julian_day", "coordinates", "effective_house_system"),
            calculator="calculate_houses",
        ),
        _canonical_node(
            NatalCalculationNodeCode.HOUSES_RUNTIME,
            output_key="houses_runtime",
            depends_on=("houses_raw", "house_rulerships"),
            calculator="build_houses_runtime",
        ),
        _canonical_node(
            NatalCalculationNodeCode.SIGNS_RUNTIME,
            output_key="signs_runtime",
            depends_on=("planet_positions", "runtime_reference", "dignities"),
            calculator="build_sign_runtime_data",
        ),
        _canonical_node(
            NatalCalculationNodeCode.HOUSE_RULERSHIPS,
            output_key="house_rulerships",
            depends_on=("houses_raw", "planet_positions", "runtime_reference"),
            calculator="house_ruler_resolver",
        ),
        _canonical_node(
            NatalCalculationNodeCode.MOTION_VISIBILITY_PAYLOADS,
            output_key="motion_visibility_payloads",
            depends_on=("planet_positions",),
            calculator="build_motion_visibility_payloads",
        ),
        _canonical_node(
            NatalCalculationNodeCode.CHART_OBJECTS,
            output_key="chart_objects",
            depends_on=(
                "planet_positions",
                "astral_points",
                "houses_runtime",
                "house_rulerships",
                "motion_visibility_payloads",
                "runtime_reference",
            ),
            calculator="build_chart_object_runtime_data",
        ),
        _canonical_node(
            NatalCalculationNodeCode.FIXED_STAR_CONJUNCTIONS,
            output_key="fixed_star_conjunctions",
            depends_on=("chart_objects", "runtime_reference"),
            calculator="fixed_star_conjunction_calculator",
        ),
        _canonical_node(
            NatalCalculationNodeCode.ASPECTS_RUNTIME,
            output_key="aspects_runtime",
            depends_on=("chart_objects", "fixed_star_conjunctions", "runtime_reference"),
            calculator="calculate_major_aspects",
        ),
        _canonical_node(
            NatalCalculationNodeCode.HOUSE_POSITIONS,
            output_key="house_positions",
            depends_on=("houses_runtime", "chart_objects"),
            calculator="enrich_house_position_payloads",
        ),
        _canonical_node(
            NatalCalculationNodeCode.ADVANCED_CONDITIONS,
            output_key="advanced_conditions",
            depends_on=(
                "planet_positions",
                "aspects_runtime",
                "dignities",
                "runtime_reference",
            ),
            calculator="advanced_condition_engine",
        ),
        _canonical_node(
            NatalCalculationNodeCode.DIGNITIES,
            output_key="dignities",
            depends_on=("chart_objects", "fixed_star_conjunctions", "runtime_reference"),
            calculator="planet_dignity_scoring_service",
        ),
        _canonical_node(
            NatalCalculationNodeCode.CHART_SIGNATURE,
            output_key="chart_signature",
            depends_on=("signs_runtime", "houses_runtime", "aspects_runtime"),
            calculator="chart_signature_calculator",
        ),
        _canonical_node(
            NatalCalculationNodeCode.DOMINANCE,
            output_key="dominance",
            depends_on=(
                "chart_objects",
                "fixed_star_conjunctions",
                "houses_runtime",
                "house_rulerships",
                "advanced_conditions",
                "aspects_runtime",
                "dignities",
                "runtime_reference",
            ),
            calculator="planet_dominance_engine",
        ),
        _canonical_node(
            NatalCalculationNodeCode.INTERPRETATION_INPUT,
            output_key="interpretation_input",
            depends_on=("chart_objects", "aspects_runtime", "dominance", "advanced_conditions"),
            calculator="chart_interpretation_input_builder",
        ),
        _projection_node(
            NatalCalculationNodeCode.PLANET_POSITIONS_PROJECTION,
            output_key="planet_positions_projection",
            depends_on=("planet_positions",),
            calculator="project_planet_positions",
        ),
        _projection_node(
            NatalCalculationNodeCode.ASTRAL_POINTS_PROJECTION,
            output_key="astral_points_projection",
            depends_on=("astral_points",),
            calculator="project_astral_points",
        ),
        _projection_node(
            NatalCalculationNodeCode.HOUSES_PROJECTION,
            output_key="houses_projection",
            depends_on=("houses_runtime",),
            calculator="project_houses",
        ),
        _projection_node(
            NatalCalculationNodeCode.ASPECTS_PROJECTION,
            output_key="aspects_projection",
            depends_on=("aspects_runtime",),
            calculator="project_aspects",
        ),
        _projection_node(
            NatalCalculationNodeCode.DIGNITY_RESULTS_PROJECTION,
            output_key="dignity_results_projection",
            depends_on=("dignities",),
            calculator="project_dignity_results",
        ),
        _projection_node(
            NatalCalculationNodeCode.ADVANCED_CONDITIONS_PROJECTION,
            output_key="advanced_conditions_projection",
            depends_on=("advanced_conditions",),
            calculator="project_advanced_conditions",
        ),
        _projection_node(
            NatalCalculationNodeCode.FIXED_STAR_CONJUNCTIONS_PROJECTION,
            output_key="fixed_star_conjunctions_projection",
            depends_on=("fixed_star_conjunctions",),
            calculator="project_fixed_star_conjunctions",
        ),
        CalculationNodeDefinition(
            code=NatalCalculationNodeCode.PUBLIC_NATAL_RESULT.value,
            output_key="public_natal_result",
            depends_on=(
                "prepared_birth_data",
                "planet_positions_projection",
                "astral_points_projection",
                "houses_projection",
                "aspects_projection",
                "dignity_results_projection",
                "advanced_conditions_projection",
                "fixed_star_conjunctions_projection",
                "chart_signature",
                "interpretation_input",
            ),
            calculator="project_public_natal_result",
            tags=(PUBLIC_PROJECTION_TAG,),
        ),
    )


def _canonical_node(
    code: NatalCalculationNodeCode,
    *,
    output_key: str,
    depends_on: tuple[str, ...],
    calculator: str,
) -> CalculationNodeDefinition:
    """Cree un node canonique sans dependance vers les projections."""
    return CalculationNodeDefinition(
        code=code.value,
        output_key=output_key,
        depends_on=depends_on,
        calculator=calculator,
        tags=(CANONICAL_RUNTIME_TAG,),
    )


def _projection_node(
    code: NatalCalculationNodeCode,
    *,
    output_key: str,
    depends_on: tuple[str, ...],
    calculator: str,
) -> CalculationNodeDefinition:
    """Cree une projection de compatibilite terminale du graphe."""
    return CalculationNodeDefinition(
        code=code.value,
        output_key=output_key,
        depends_on=depends_on,
        calculator=calculator,
        tags=(COMPATIBILITY_PROJECTION_TAG,),
    )

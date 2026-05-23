# Registry explicite des adapters de nodes du graphe natal.
"""Expose les calculateurs autorises pour executer `natal_chart_v1`."""

from __future__ import annotations

from app.domain.astrology.runtime.calculation_graph_runner import CalculationNodeRegistry
from app.domain.astrology.runtime.natal_calculation_nodes import (
    build_chart_object_runtime_data_node,
    build_houses_runtime_node,
    build_interpretation_input_node,
    build_motion_visibility_payloads_node,
    build_sign_runtime_data_node,
    calculate_advanced_conditions_node,
    calculate_astral_points_node,
    calculate_chart_signature_node,
    calculate_dignities_node,
    calculate_dominance_node,
    calculate_fixed_star_conjunctions_node,
    calculate_houses_node,
    calculate_major_aspects_node,
    calculate_planet_positions_node,
    prepare_birth_data_node,
    project_identity_node,
    project_public_natal_result_node,
    resolve_house_rulerships_node,
)


def build_natal_calculation_node_registry() -> CalculationNodeRegistry:
    """Construit le registry explicite des calculateurs du graphe natal."""
    return CalculationNodeRegistry(
        {
            "prepare_birth_data": prepare_birth_data_node,
            "calculate_planet_positions": calculate_planet_positions_node,
            "calculate_astral_points": calculate_astral_points_node,
            "calculate_houses": calculate_houses_node,
            "build_houses_runtime": build_houses_runtime_node,
            "build_sign_runtime_data": build_sign_runtime_data_node,
            "build_chart_object_runtime_data": build_chart_object_runtime_data_node,
            "calculate_major_aspects": calculate_major_aspects_node,
            "enrich_house_position_payloads": lambda context: project_identity_node(
                context, "chart_objects"
            ),
            "house_ruler_resolver": resolve_house_rulerships_node,
            "fixed_star_conjunction_calculator": calculate_fixed_star_conjunctions_node,
            "advanced_condition_engine": calculate_advanced_conditions_node,
            "build_motion_visibility_payloads": build_motion_visibility_payloads_node,
            "planet_dignity_scoring_service": calculate_dignities_node,
            "planet_dominance_engine": calculate_dominance_node,
            "chart_signature_calculator": calculate_chart_signature_node,
            "chart_interpretation_input_builder": build_interpretation_input_node,
            "project_planet_positions": lambda context: project_identity_node(
                context, "planet_positions"
            ),
            "project_astral_points": lambda context: project_identity_node(
                context, "astral_points"
            ),
            "project_houses": lambda context: project_identity_node(context, "houses_runtime"),
            "project_aspects": lambda context: project_identity_node(context, "aspects_runtime"),
            "project_dignity_results": lambda context: project_identity_node(context, "dignities"),
            "project_advanced_conditions": lambda context: project_identity_node(
                context, "advanced_conditions"
            ),
            "project_fixed_star_conjunctions": lambda context: project_identity_node(
                context, "fixed_star_conjunctions"
            ),
            "project_public_natal_result": project_public_natal_result_node,
        }
    )

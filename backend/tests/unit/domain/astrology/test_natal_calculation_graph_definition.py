# Tests de la definition declarative du graphe de calcul natal.
"""Verifie que le graphe CS-226 documente le pipeline natal sans l'executer."""

import ast
from pathlib import Path

from app.domain.astrology.runtime.calculation_graph_validator import (
    validate_calculation_graph_definition,
)
from app.domain.astrology.runtime.natal_calculation_graph import (
    CANONICAL_RUNTIME_TAG,
    COMPATIBILITY_PROJECTION_TAG,
    NATAL_GRAPH_CODE,
    PUBLIC_PROJECTION_TAG,
    NatalCalculationNodeCode,
    build_natal_calculation_graph_definition,
)

MODULE_PATH = (
    Path(__file__).resolve().parents[5]
    / "backend/app/domain/astrology/runtime/natal_calculation_graph.py"
)

REQUIRED_INPUTS = {
    "birth_datetime",
    "timezone",
    "coordinates",
    "house_system",
    "zodiac_mode",
    "runtime_reference",
    "locale",
    "calculation_options",
}
DERIVED_INPUTS = {"prepared_birth_data", "julian_day", "effective_house_system"}
CANONICAL_OUTPUTS = {
    "prepared_birth_data",
    "planet_positions",
    "astral_points",
    "houses_raw",
    "houses_runtime",
    "signs_runtime",
    "chart_objects",
    "aspects_runtime",
    "house_positions",
    "house_rulerships",
    "fixed_star_conjunctions",
    "advanced_conditions",
    "motion_visibility_payloads",
    "dignities",
    "dominance",
    "chart_signature",
    "interpretation_input",
}
PROJECTION_OUTPUTS = {
    "planet_positions_projection",
    "astral_points_projection",
    "houses_projection",
    "aspects_projection",
    "dignity_results_projection",
    "advanced_conditions_projection",
    "fixed_star_conjunctions_projection",
    "public_natal_result",
}


def test_natal_graph_definition_is_valid() -> None:
    """Le graphe natal declare son code et passe le validator CS-225."""
    graph = build_natal_calculation_graph_definition()
    result = validate_calculation_graph_definition(graph)

    assert graph.graph_code == NATAL_GRAPH_CODE
    assert graph.version == "1"
    assert result.is_valid is True
    assert result.errors == ()


def test_natal_graph_declares_minimal_and_derived_inputs() -> None:
    """Les entrees minimales et derivees du theme natal sont explicites."""
    graph = build_natal_calculation_graph_definition()
    input_keys = {input_definition.key for input_definition in graph.required_inputs}

    assert REQUIRED_INPUTS <= input_keys
    assert DERIVED_INPUTS <= input_keys


def test_natal_graph_covers_runtime_and_projection_surfaces() -> None:
    """Les surfaces runtime documentees et les projections sont couvertes."""
    graph = build_natal_calculation_graph_definition()
    outputs = {node.output_key for node in graph.nodes}
    node_codes = {node.code for node in graph.nodes}

    assert CANONICAL_OUTPUTS <= outputs
    assert PROJECTION_OUTPUTS <= outputs
    assert {node.value for node in NatalCalculationNodeCode} == node_codes


def test_natal_graph_critical_dependencies_are_explicit() -> None:
    """Les dependances principales restent lisibles dans la definition."""
    nodes = _nodes_by_output()

    assert nodes["houses_runtime"].depends_on == (
        "houses_raw",
        "house_rulerships",
    )
    assert nodes["house_rulerships"].depends_on == (
        "houses_raw",
        "planet_positions",
        "runtime_reference",
    )
    assert nodes["chart_signature"].depends_on == (
        "signs_runtime",
        "houses_runtime",
        "aspects_runtime",
    )
    assert nodes["dignities"].depends_on == (
        "chart_objects",
        "fixed_star_conjunctions",
        "runtime_reference",
    )
    assert "dignities" in nodes["dominance"].depends_on
    assert "dominance" not in nodes["dignities"].depends_on


def test_projection_nodes_are_terminal_compatibility_surfaces() -> None:
    """Les projections legacy ne servent jamais de source de calcul canonique."""
    graph = build_natal_calculation_graph_definition()
    projection_outputs = {
        node.output_key
        for node in graph.nodes
        if COMPATIBILITY_PROJECTION_TAG in node.tags or PUBLIC_PROJECTION_TAG in node.tags
    }

    assert PROJECTION_OUTPUTS == projection_outputs
    for node in graph.nodes:
        if CANONICAL_RUNTIME_TAG in node.tags:
            assert projection_outputs.isdisjoint(node.depends_on)


def test_natal_graph_topological_order_documents_pipeline_flow() -> None:
    """L'ordre topologique place les sources canoniques avant leurs consommateurs."""
    result = validate_calculation_graph_definition(build_natal_calculation_graph_definition())
    order = {node_code: index for index, node_code in enumerate(result.topological_order)}

    assert order["houses_raw"] < order["houses_runtime"]
    assert order["chart_objects"] < order["aspects_runtime"]
    assert order["house_rulerships"] < order["houses_runtime"]
    assert order["dignities"] < order["dominance"]
    assert order["chart_signature"] < order["dominance"]
    assert order["public_natal_result"] == max(order.values())


def test_natal_graph_module_keeps_forbidden_imports_out() -> None:
    """La definition reste pure et hors API, infra, DB, LLM ou frontend."""
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_roots = {
        "app.api",
        "app.infra",
        "app.core.config",
        "fastapi",
        "sqlalchemy",
        "networkx",
        "igraph",
        "graphlib",
    }
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert all(not module.startswith(tuple(forbidden_roots)) for module in imported_modules)


def _nodes_by_output() -> dict[str, object]:
    """Indexe les nodes par sortie pour des assertions lisibles."""
    return {node.output_key: node for node in build_natal_calculation_graph_definition().nodes}

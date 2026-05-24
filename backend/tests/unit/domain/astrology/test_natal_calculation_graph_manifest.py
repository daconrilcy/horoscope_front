# Tests du manifeste du graphe natal runtime.
"""Verifie que `natal_chart_v1` expose un manifeste IO valide et stable."""

import ast
from pathlib import Path

from app.domain.astrology.runtime.calculation_graph_manifest import manifest_to_dict
from app.domain.astrology.runtime.calculation_graph_manifest_validator import (
    validate_graph_manifest,
)
from app.domain.astrology.runtime.natal_calculation_graph import (
    NATAL_GRAPH_CODE,
    build_natal_calculation_graph_definition,
    build_natal_calculation_graph_manifest,
)

MODULE_PATH = (
    Path(__file__).resolve().parents[5]
    / "backend/app/domain/astrology/runtime/calculation_graph_manifest.py"
)
API_NEUTRAL_MODULE_PATH = (
    Path(__file__).resolve().parents[5]
    / "backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py"
)


def test_natal_chart_v1_manifest_is_valid() -> None:
    """Le manifeste natal pointe vers la famille canonique et passe validation."""
    manifest = build_natal_calculation_graph_manifest()
    result = validate_graph_manifest(manifest)

    assert manifest.graph_code == NATAL_GRAPH_CODE
    assert manifest.graph_version == "1"
    assert manifest.family_code == NATAL_GRAPH_CODE
    assert result.is_valid is True
    assert result.errors == ()


def test_natal_manifest_matches_graph_definition() -> None:
    """Le manifeste reste derive du graphe réellement declare."""
    graph = build_natal_calculation_graph_definition()
    manifest = build_natal_calculation_graph_manifest()

    assert tuple(descriptor.key for descriptor in manifest.required_inputs) == tuple(
        input_definition.key for input_definition in graph.required_inputs
    )
    assert tuple(node.code for node in manifest.nodes) == tuple(node.code for node in graph.nodes)
    assert tuple(node.output_schema.key for node in manifest.nodes) == tuple(
        node.output_key for node in graph.nodes
    )


def test_each_natal_node_declares_input_and_output_schema() -> None:
    """Chaque node expose des descriptors IO non vides."""
    manifest = build_natal_calculation_graph_manifest()

    assert manifest.nodes
    for node in manifest.nodes:
        assert node.input_schema
        assert node.output_schema.key
        assert node.output_schema.value_type
        assert tuple(descriptor.key for descriptor in node.input_schema) == node.depends_on


def test_manifest_snapshot_shape_is_deterministic() -> None:
    """La preuve JSON interne garde un ordre stable entre deux constructions."""
    first = manifest_to_dict(build_natal_calculation_graph_manifest())
    second = manifest_to_dict(build_natal_calculation_graph_manifest())

    assert first == second
    assert first["graph_code"] == NATAL_GRAPH_CODE
    assert "nodes" in first


def test_manifest_modules_keep_public_api_imports_out() -> None:
    """Les contrats de manifeste restent dans le domaine runtime pur."""
    forbidden_roots = {"app.api", "fastapi", "sqlalchemy"}

    for module_path in (MODULE_PATH, API_NEUTRAL_MODULE_PATH):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
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

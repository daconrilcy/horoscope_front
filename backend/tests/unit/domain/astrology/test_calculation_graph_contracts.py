# Tests des contrats declaratifs du graphe de calcul runtime.
"""Verifie la forme des contrats CS-225 et leur documentation."""

from dataclasses import FrozenInstanceError, is_dataclass
from pathlib import Path

import pytest

from app.domain.astrology.runtime.calculation_graph_contracts import (
    CalculationGraphDefinition,
    CalculationGraphValidationError,
    CalculationGraphValidationResult,
    CalculationInputDefinition,
    CalculationNodeDefinition,
    CalculationNodeStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
DOC_PATH = REPO_ROOT / "docs/architecture/astrology-calculation-graph.md"


def test_contracts_are_immutable_dataclasses() -> None:
    """Les contrats principaux restent des dataclasses figees."""
    contracts = (
        CalculationInputDefinition,
        CalculationNodeDefinition,
        CalculationGraphDefinition,
        CalculationGraphValidationError,
        CalculationGraphValidationResult,
    )

    assert all(is_dataclass(contract) for contract in contracts)
    graph = CalculationGraphDefinition(
        graph_code="natal_chart_v1",
        version="1",
        nodes=(),
    )

    with pytest.raises(FrozenInstanceError):
        graph.graph_code = "other"  # type: ignore[misc]


def test_node_contract_exposes_stable_dependencies_and_output_key() -> None:
    """Un node declare ses dependances, sa sortie et son calculateur stable."""
    node = CalculationNodeDefinition(
        code="houses",
        output_key="houses_runtime",
        depends_on=("julian_day", "coordinates", "house_system"),
        optional_depends_on=("runtime_reference",),
        calculator="houses_runtime_builder",
        tags=("natal",),
    )

    assert node.output_key == "houses_runtime"
    assert node.depends_on == ("julian_day", "coordinates", "house_system")
    assert node.optional_depends_on == ("runtime_reference",)
    assert node.calculator == "houses_runtime_builder"


def test_input_contract_distinguishes_required_and_optional_inputs() -> None:
    """Les entrees peuvent etre obligatoires ou optionnelles."""
    required_input = CalculationInputDefinition(key="julian_day", value_type="float")
    optional_input = CalculationInputDefinition(
        key="runtime_reference",
        value_type="RuntimeReference",
        required=False,
    )

    assert required_input.required is True
    assert optional_input.required is False


def test_node_status_contract_lists_expected_lifecycle_values() -> None:
    """Les statuts attendus sont explicites avant tout runner."""
    assert tuple(status.value for status in CalculationNodeStatus) == (
        "declared",
        "ready",
        "executed",
        "failed",
        "skipped",
    )


def test_architecture_document_distinguishes_graph_surfaces() -> None:
    """La documentation distingue les graphes et chart_objects."""
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "calculation graph" in content
    assert "astrological graph" in content
    assert "`chart_objects`" in content
    assert "n'execute aucun calcul astrologique" in content

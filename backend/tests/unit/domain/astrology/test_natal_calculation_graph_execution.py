# Tests d'execution du graphe natal CS-228.
"""Verifie le branchement de `build_natal_result` sur le runner runtime."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.domain.astrology import natal_calculation
from app.domain.astrology.natal_calculation import NatalCalculationError, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.runtime.calculation_graph_runner import CalculationGraphRunner
from app.domain.astrology.runtime.natal_calculation_graph import (
    NATAL_GRAPH_CODE,
    build_natal_calculation_graph_definition,
)
from app.domain.astrology.runtime.natal_calculation_registry import (
    build_natal_calculation_node_registry,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference

REPO_ROOT = Path(__file__).resolve().parents[4]
NATAL_CALCULATION = REPO_ROOT / "app/domain/astrology/natal_calculation.py"
NATAL_NODES = REPO_ROOT / "app/domain/astrology/runtime/natal_calculation_nodes.py"
NATAL_REGISTRY = REPO_ROOT / "app/domain/astrology/runtime/natal_calculation_registry.py"


def test_build_natal_result_executes_natal_chart_v1_through_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La facade execute le graphe natal via le runner et retourne le contrat public."""
    calls: list[str] = []
    original_run = CalculationGraphRunner.run

    def _recording_run(self, definition, initial_context):
        calls.append(definition.graph_code)
        return original_run(self, definition, initial_context)

    monkeypatch.setattr(CalculationGraphRunner, "run", _recording_run)

    result = build_natal_result(_birth(), complete_reference(), ruleset_version="test")

    assert calls == [NATAL_GRAPH_CODE]
    assert result.chart_objects
    assert result.houses
    assert result.aspects


def test_natal_node_registry_resolves_every_graph_calculator() -> None:
    """Le registry explicite couvre tous les calculateurs declares par le graphe."""
    graph = build_natal_calculation_graph_definition()
    registry = build_natal_calculation_node_registry()

    assert graph.graph_code == NATAL_GRAPH_CODE
    for node in graph.nodes:
        assert registry.get(node.calculator) is not None, node.calculator


def test_node_failure_message_contains_node_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """Une erreur d'adapter remontee par la facade mentionne le code du node."""

    def _boom(julian_day: float, planet_codes: list[str], sign_codes: list[str]):
        del julian_day, planet_codes, sign_codes
        raise RuntimeError("forced planet failure")

    monkeypatch.setattr(natal_calculation, "calculate_planet_positions", _boom)

    with pytest.raises(NatalCalculationError) as error_info:
        build_natal_result(_birth(), complete_reference(), ruleset_version="test")

    assert error_info.value.code == "natal_graph_node_failed"
    assert "planet_positions" in error_info.value.message
    assert error_info.value.details["node_code"] == "planet_positions"


def test_adapters_do_not_use_dynamic_resolution_or_legacy_projection_sources() -> None:
    """Les adapters restent explicites et ne consomment pas les projections legacy."""
    source = NATAL_NODES.read_text(encoding="utf-8")

    assert "importlib" not in source
    assert "eval(" not in source
    assert "globals(" not in source
    assert "planet_positions_projection" not in source
    assert "dignity_results_projection" not in source
    assert "advanced_conditions_projection" not in source


def test_build_natal_result_is_thin_graph_facade() -> None:
    """La facade ne contient plus la longue sequence procedurale du pipeline natal."""
    tree = ast.parse(NATAL_CALCULATION.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "build_natal_result"
    )
    called_names = {
        node.func.id
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "CalculationGraphRunner" in ast.unparse(function)
    assert "build_natal_calculation_graph_definition" in ast.unparse(function)
    assert "FixedStarConjunctionCalculator" not in ast.unparse(function)
    assert "PlanetDignityScoringService" not in ast.unparse(function)
    assert "PlanetDominanceEngine" not in ast.unparse(function)
    assert "calculate_major_aspects" not in called_names


def test_registry_does_not_use_magic_lookup() -> None:
    """La resolution des calculateurs reste une table explicite."""
    source = NATAL_REGISTRY.read_text(encoding="utf-8")

    assert "importlib" not in source
    assert "eval(" not in source
    assert "globals(" not in source


def _birth() -> BirthInput:
    """Construit une naissance stable pour les tests de runner natal."""
    return BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

# Garde d'architecture pour la selection temporelle unique CS-253.
"""Prouve qu'aucune deuxieme famille temporelle n'est ouverte."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.domain.astrology.runtime.astrology_graph_family_registry import (
    AstrologyGraphFamilyRegistryError,
    resolve_astrology_graph_definition,
)
from app.domain.astrology.runtime.temporal_technique_selection import (
    SELECTED_TEMPORAL_FAMILY_CODE,
    TemporalCandidateStatus,
    TemporalTechniqueSelectionStatus,
    build_first_temporal_technique_selection,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ASTROLOGY_RUNTIME = BACKEND_ROOT / "app/domain/astrology/runtime"
API_ROOT = BACKEND_ROOT / "app/api"
FORBIDDEN_PUBLIC_SURFACE_TERMS = (
    "temporal_technique_selection",
    "transit_chart_v1",
    "synastry_chart_v1",
    "solar_return_v1",
    "progressed_chart_v1",
)


def test_selection_has_one_open_temporal_family_and_closed_candidates() -> None:
    """Le contrat ouvre seulement transit_chart_v1 comme decision interne."""
    selection = build_first_temporal_technique_selection(cs250_status="ready-to-review")
    open_family_codes = [selection.selected_family_code]

    assert open_family_codes == [SELECTED_TEMPORAL_FAMILY_CODE]
    assert selection.selection_status is TemporalTechniqueSelectionStatus.SELECTED_BLOCKED_BY_CS250
    assert all(
        candidate.status is TemporalCandidateStatus.CLOSED
        for candidate in selection.rejected_candidates
    )


def test_selected_temporal_family_has_no_executable_graph_definition_yet() -> None:
    """Le choix ne cree pas de graphe executable avant les gates requis."""
    with pytest.raises(AstrologyGraphFamilyRegistryError, match="no executable graph definition"):
        resolve_astrology_graph_definition(SELECTED_TEMPORAL_FAMILY_CODE)


def test_temporal_selection_module_does_not_import_prediction_runtime() -> None:
    """AST guard: la selection temporelle reste dans astrology runtime."""
    module_path = ASTROLOGY_RUNTIME / "temporal_technique_selection.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert not any(module.startswith("app.domain.prediction") for module in imported_modules)
    assert not any(module.startswith("app.services.prediction") for module in imported_modules)


def test_public_api_does_not_reference_temporal_selection_or_candidate_families() -> None:
    """AST guard: aucune route API ne publie la selection temporelle."""
    offenders: list[str] = []
    for path in sorted(API_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                lowered = node.value.lower()
                if any(term in lowered for term in FORBIDDEN_PUBLIC_SURFACE_TERMS):
                    offenders.append(f"{path.relative_to(BACKEND_ROOT).as_posix()}:{node.lineno}")
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.endswith("temporal_technique_selection"):
                    offenders.append(f"{path.relative_to(BACKEND_ROOT).as_posix()}:{node.lineno}")

    assert offenders == []

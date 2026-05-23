"""Gardes d'architecture de l'input interpretatif chart-object."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_ROOT = REPO_ROOT / "app/domain/astrology/interpretation"
INPUT_MODULES = (
    INPUT_ROOT / "chart_interpretation_input_contracts.py",
    INPUT_ROOT / "chart_object_interpretation_selector.py",
    INPUT_ROOT / "chart_object_interpretation_projector.py",
    INPUT_ROOT / "chart_interpretation_input_builder.py",
)
FORBIDDEN_CALCULATORS = (
    "calculate_aspects",
    "calculate_dignity",
    "calculate_dominance",
    "HouseRulerResolver",
    "FixedStarConjunctionCalculator",
)
FORBIDDEN_TEXT_FIELDS = (
    "meaning",
    "narrative",
    "psychological",
    "prompt",
    "llm",
    "OpenAI",
    "AIEngineAdapter",
)


def test_selector_does_not_branch_on_object_type_or_code() -> None:
    """Le selector reste pilote par les capacites runtime."""
    selector_path = INPUT_ROOT / "chart_object_interpretation_selector.py"
    tree = ast.parse(selector_path.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and _uses_forbidden_eligibility_reference(node):
            offenders.append(f"{selector_path}:{node.lineno}")

    assert offenders == []


def test_input_modules_do_not_call_calculators_or_providers() -> None:
    """L'input interpretatif projette des faits sans recalcul ni provider."""
    offenders: list[str] = []
    for module_path in INPUT_MODULES:
        source = module_path.read_text(encoding="utf-8")
        for forbidden_name in FORBIDDEN_CALCULATORS:
            if forbidden_name in source:
                offenders.append(f"{module_path}:{forbidden_name}")
        for provider_name in ("OpenAI", "AIEngineAdapter"):
            if provider_name in source:
                offenders.append(f"{module_path}:{provider_name}")

    assert offenders == []


def test_input_contracts_do_not_define_editorial_text_fields() -> None:
    """Les contrats d'input restent des contrats factuels."""
    contracts = (INPUT_ROOT / "chart_interpretation_input_contracts.py").read_text(encoding="utf-8")

    assert not any(forbidden_name in contracts for forbidden_name in FORBIDDEN_TEXT_FIELDS)


def _uses_forbidden_eligibility_reference(node: ast.Compare) -> bool:
    """Detecte les comparaisons sur famille ou code nominal."""
    compared_nodes = (node.left, *node.comparators)
    return any(_is_forbidden_reference(item) for item in compared_nodes)


def _is_forbidden_reference(node: ast.AST) -> bool:
    """Reconnait les champs interdits pour l'eligibilite."""
    if isinstance(node, ast.Name):
        return node.id in {"object_type", "code"}
    if isinstance(node, ast.Attribute):
        return node.attr in {"object_type", "code"}
    return False

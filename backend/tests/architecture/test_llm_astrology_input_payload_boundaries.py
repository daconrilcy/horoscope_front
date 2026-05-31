# Garde d'architecture des frontieres prompt du payload LLM natal.
"""Verifie que le gateway ne redevient pas owner des carriers natals bruts."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.interpretation.llm_astrology_input_v1 import (
    LLM_ASTROLOGY_INPUT_DATA_ROLES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = REPO_ROOT / "app/domain/llm/runtime/gateway.py"
CONTRACT_PATH = REPO_ROOT / "app/domain/astrology/interpretation/llm_astrology_input_v1.py"
THEME_ASTRAL_PROVIDER_BUILDER_PATH = (
    REPO_ROOT / "app/domain/llm/runtime/theme_astral_provider_payload_builder.py"
)
PROMPT_VISIBLE_BLOCKS = set(LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"])
AUDIT_ONLY_PROMPT_SURFACES = {
    "evidence",
    "provenance",
    "projection_hash",
    "llm_input_hash",
    "llm_input_version",
    "grounding_status",
    "validation_owner",
    "evidence_refs",
    "provider_response",
    "persisted_answer",
}


def test_gateway_serializes_projected_llm_astrology_prompt_payload() -> None:
    """Le gateway doit projeter le contrat riche avant serialisation prompt."""
    source = GATEWAY_PATH.read_text(encoding="utf-8")

    assert "_prompt_visible_llm_astrology_input(llm_astrology_input)" in source
    assert "json.dumps(llm_astrology_input, ensure_ascii=False" not in source


def test_gateway_prompt_projection_reuses_canonical_prompt_visible_roles() -> None:
    """La projection prompt reutilise le contrat canonique au lieu d'une copie."""
    source = GATEWAY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    import_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "app.domain.astrology.interpretation.llm_astrology_input_v1"
        for alias in node.names
    }
    assigned_from_roles = any(
        isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS"
            for target in node.targets
        )
        and "LLM_ASTROLOGY_INPUT_DATA_ROLES" in ast.unparse(node.value)
        and "prompt_visible" in ast.unparse(node.value)
        for node in ast.walk(tree)
    )

    assert "LLM_ASTROLOGY_INPUT_DATA_ROLES" in import_names
    assert assigned_from_roles


def test_gateway_prompt_projection_has_no_audit_only_literal_blocks() -> None:
    """La projection prompt ne declare aucun champ audit-only comme bloc prompt."""
    tree = ast.parse(GATEWAY_PATH.read_text(encoding="utf-8"))
    assigned_blocks: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS"
            for target in node.targets
        ):
            continue
        assigned_blocks = _literal_string_values(node.value)

    assert AUDIT_ONLY_PROMPT_SURFACES.isdisjoint(assigned_blocks)
    assert {"chart_json", "natal_data"}.isdisjoint(assigned_blocks)


def test_gateway_prompt_projection_removes_nested_audit_and_validation_keys() -> None:
    """La projection retire aussi les champs audit-only imbriques."""
    source = GATEWAY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    constant_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    assert "LLM_ASTROLOGY_INPUT_V1_PROMPT_EXCLUDED_KEYS" in constant_names
    assert "_without_prompt_excluded_keys" in function_names
    literal_keys = _literal_string_values(tree)
    assert {"provenance", "evidence_refs", "llm_input_version"} <= literal_keys
    assert "LLM_ASTROLOGY_INPUT_DATA_ROLES" in source
    assert "validation_only" in source
    assert "audit_only" in source


def test_contract_keeps_raw_surfaces_as_declared_exclusions_not_prompt_blocks() -> None:
    """Les carriers bruts restent des exclusions documentees, pas des blocs prompt."""
    tree = ast.parse(CONTRACT_PATH.read_text(encoding="utf-8"))
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}

    assert {"ChartObjectRuntimeData", "CalculationGraph", "chart_json", "natal_data"}.issubset(
        constants
    )
    assert {"facts", "signals", "limits", "evidence", "shaping"}.issubset(constants)


def test_canonical_prompt_visible_roles_exclude_audit_only_surfaces() -> None:
    """Le contrat canonique garde les donnees audit-only hors roles prompt."""
    assert PROMPT_VISIBLE_BLOCKS == {"facts", "signals", "limits", "shaping"}
    assert AUDIT_ONLY_PROMPT_SURFACES.isdisjoint(PROMPT_VISIBLE_BLOCKS)


def test_basic_natal_provider_payload_uses_reading_plan_not_raw_runtime() -> None:
    """Le payload provider Basic depend du plan et non des carriers natals bruts."""
    tree = ast.parse(THEME_ASTRAL_PROVIDER_BUILDER_PATH.read_text(encoding="utf-8"))
    source = ast.unparse(tree)

    assert "BasicNatalReadingPlan" in source
    assert "_basic_natal_prompt_payload" in source
    assert "NatalResult" not in source
    assert "build_chart_json" not in source


def _literal_string_values(node: ast.AST) -> set[str]:
    """Collecte les chaines litterales rattachees a une expression AST."""
    return {
        nested.value
        for nested in ast.walk(node)
        if isinstance(nested, ast.Constant) and isinstance(nested.value, str)
    }

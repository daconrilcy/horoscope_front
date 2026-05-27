# Garde d'architecture des frontieres prompt du payload LLM natal.
"""Verifie que le gateway ne redevient pas owner des carriers natals bruts."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = REPO_ROOT / "app/domain/llm/runtime/gateway.py"
CONTRACT_PATH = REPO_ROOT / "app/domain/astrology/interpretation/llm_astrology_input_v1.py"
PROMPT_VISIBLE_BLOCKS = {
    "facts",
    "signals",
    "limits",
    "evidence",
    "shaping",
    "provenance",
}


def test_gateway_serializes_projected_llm_astrology_prompt_payload() -> None:
    """Le gateway doit projeter le contrat riche avant serialisation prompt."""
    source = GATEWAY_PATH.read_text(encoding="utf-8")

    assert "_prompt_visible_llm_astrology_input(llm_astrology_input)" in source
    assert "json.dumps(llm_astrology_input, ensure_ascii=False" not in source


def test_gateway_prompt_projection_declares_only_prompt_visible_blocks() -> None:
    """La projection prompt exclut les roles runtime-only et validation-only."""
    tree = ast.parse(GATEWAY_PATH.read_text(encoding="utf-8"))
    assigned_blocks: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS"
            for target in node.targets
        ):
            continue
        assigned_blocks = {
            element.value
            for element in node.value.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        }

    assert assigned_blocks == PROMPT_VISIBLE_BLOCKS
    assert {"chart_json", "natal_data", "provider_response"}.isdisjoint(assigned_blocks)


def test_contract_keeps_raw_surfaces_as_declared_exclusions_not_prompt_blocks() -> None:
    """Les carriers bruts restent des exclusions documentees, pas des blocs prompt."""
    tree = ast.parse(CONTRACT_PATH.read_text(encoding="utf-8"))
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}

    assert {"ChartObjectRuntimeData", "CalculationGraph", "chart_json", "natal_data"}.issubset(
        constants
    )
    assert {"facts", "signals", "limits", "evidence", "shaping"}.issubset(constants)

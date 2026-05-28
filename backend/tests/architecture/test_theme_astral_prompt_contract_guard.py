"""Verrouille l'unicite du contrat prompt provider theme_astral."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.llm.configuration.theme_astral_contracts import (
    THEME_ASTRAL_INPUT_CONTRACT_ID,
    THEME_ASTRAL_PROMPT_CONTRACT_ID,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = BACKEND_ROOT / "app"


def test_theme_astral_contract_ids_are_canonical() -> None:
    """Le contrat prompt actif porte le nom cible sans ancien alias."""
    assert THEME_ASTRAL_PROMPT_CONTRACT_ID == "theme_astral_prompt_v1"
    assert THEME_ASTRAL_INPUT_CONTRACT_ID == "theme_astral_llm_input_v1"


def test_theme_astral_gateway_rejects_missing_canonical_payload() -> None:
    """AST guard: le gateway refuse le flux theme_astral sans payload cible."""
    gateway_source = (APP_ROOT / "domain/llm/runtime/gateway.py").read_text(encoding="utf-8")
    tree = ast.parse(gateway_source)
    constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert "theme_astral requires theme_astral_llm_input_v1 provider payload" in constants
    assert "_is_theme_astral_use_case" in gateway_source
    assert "THEME_ASTRAL_PROVIDER_PAYLOAD_KEY" in gateway_source


def test_theme_astral_runtime_files_do_not_use_legacy_prompt_carriers() -> None:
    """Les owners theme_astral n'importent pas les anciens carriers provider."""
    scoped_files = [
        APP_ROOT / "domain/llm/runtime/theme_astral_provider_payload_builder.py",
        APP_ROOT / "domain/llm/configuration/theme_astral_contracts.py",
        APP_ROOT / "ops/llm/bootstrap/seed_theme_astral_prompt_contract.py",
    ]
    forbidden = (
        "chart_json",
        "natal_data",
        "llm_astrology_input_v1",
        "natal_interpretation_short",
        "NATAL_SHORT_PROMPT",
        "NATAL_COMPLETE_PROMPT",
        "theme_astral_prompt_contract_v1",
    )

    for path in scoped_files:
        source = path.read_text(encoding="utf-8")
        assert not any(token in source for token in forbidden), path
    assert "theme_astral_prompt_v1" in scoped_files[1].read_text(encoding="utf-8")

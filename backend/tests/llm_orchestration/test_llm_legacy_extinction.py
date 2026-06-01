# Commentaire global: garde anti-retour des anciens chemins generateurs natal publics.
"""Scanne les owners runtime pour interdire les use cases publics legacy."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_RUNTIME_SYMBOLS = {
    "natal_interpretation_short",
    "natal_long_free",
    "use_case_level",
    "forceRefresh",
    "PROMPT_FALLBACK_CONFIGS",
    "fallback_default",
    "EXIGENCE PREMIUM",
    "AstroResponse_v3",
}
RUNTIME_FILES = (
    ROOT / "app/services/llm_generation/natal/theme_natal_product_actions.py",
    ROOT / "app/services/llm_generation/natal/theme_natal_basic_full_runtime.py",
)


def test_public_theme_natal_runtime_does_not_call_legacy_generator_symbols() -> None:
    """Les owners publics ne referencent pas les anciens symboles generateurs."""
    hits: list[str] = []
    for path in RUNTIME_FILES:
        source = path.read_text(encoding="utf-8")
        for symbol in FORBIDDEN_RUNTIME_SYMBOLS:
            if symbol in source:
                hits.append(f"{path.relative_to(ROOT)}::{symbol}")

    assert hits == []


def test_product_action_runtime_imports_no_prompt_fallback_or_legacy_interpret_service() -> None:
    """L'AST confirme que la commande publique ne depend pas du service legacy generateur."""
    path = ROOT / "app/services/llm_generation/natal/theme_natal_product_actions.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    forbidden_imports = {
        "app.services.llm_generation.natal.interpretation_service",
        "app.domain.llm.prompting.catalog",
    }

    assert imported_modules.isdisjoint(forbidden_imports)

"""Gardes d'architecture du contrat IA et narration."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"
AI_INPUT_ROOT = APP_ROOT / "domain/astrology/interpretation"
AI_INPUT_MODULES = (
    AI_INPUT_ROOT / "ai_narrative_input_contracts.py",
    AI_INPUT_ROOT / "ai_narrative_input_builder.py",
)
CALCULATION_ROOTS = (
    APP_ROOT / "domain/astrology/runtime",
    APP_ROOT / "domain/astrology/calculators",
    APP_ROOT / "domain/astrology/dignities",
    APP_ROOT / "domain/astrology/dominance",
)
FORBIDDEN_SOURCE_FIELD_NAMES = {
    "prompt",
    "llm_output",
    "final_narrative",
    "rendered_text",
    "provider_response",
}
FORBIDDEN_PROVIDER_NAMES = {"OpenAI", "AIEngineAdapter", "LLMGateway"}


def test_ai_input_contracts_do_not_define_forbidden_source_fields() -> None:
    """Le contrat IA ne porte aucun champ redactionnel comme source."""
    offenders: list[str] = []
    for module_path in AI_INPUT_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in FORBIDDEN_SOURCE_FIELD_NAMES:
                    offenders.append(f"{module_path}:{node.lineno}:{node.target.id}")

    assert offenders == []


def test_ai_input_modules_do_not_import_provider_or_public_api_layers() -> None:
    """L'input IA reste un owner domaine interne sans gateway ni route publique."""
    forbidden_imports = ("app.api", "app.infra", "app." + "infrastructure", "app.services")
    offenders: list[str] = []
    for module_path in AI_INPUT_MODULES:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            imported_name = _imported_module_name(node)
            if imported_name and (
                imported_name.startswith(forbidden_imports)
                or imported_name in FORBIDDEN_PROVIDER_NAMES
            ):
                offenders.append(f"{module_path}:{node.lineno}:{imported_name}")

    assert offenders == []


def test_calculation_modules_do_not_import_ai_narrative_input_or_narration_layers() -> None:
    """Le calcul reste en amont du contrat IA et des couches de narration."""
    forbidden_import_fragments = (
        "ai_narrative_input",
        ".narrative",
        ".narration",
        ".llm",
    )
    offenders: list[str] = []
    for module_path in _python_files(CALCULATION_ROOTS):
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            imported_name = _imported_module_name(node)
            if imported_name and any(
                fragment in imported_name for fragment in forbidden_import_fragments
            ):
                offenders.append(f"{module_path}:{node.lineno}:{imported_name}")

    assert offenders == []


def _python_files(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Retourne les fichiers Python de racines applicatives ciblees."""
    return tuple(path for root in roots for path in root.rglob("*.py"))


def _imported_module_name(node: ast.AST) -> str | None:
    """Extrait le module importe par un noeud AST."""
    if isinstance(node, ast.ImportFrom):
        return node.module
    if isinstance(node, ast.Import):
        return node.names[0].name if node.names else None
    return None

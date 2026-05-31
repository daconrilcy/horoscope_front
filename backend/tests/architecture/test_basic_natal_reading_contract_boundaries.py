# Commentaire global: garde d'architecture des contrats Basic natal reading V2.
"""Verifie que les contrats Basic V2 restent purs et sans dependance runtime."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "app" / "domain" / "astrology" / "reading" / "basic_natal_contracts.py"
DOC_PATH = ROOT / "docs" / "basic-natal-reading-v2-contract.md"

FORBIDDEN_IMPORT_ROOTS = (
    "fastapi",
    "sqlalchemy",
    "app.api",
    "app.infra",
    "app.repositories",
    "app.services.llm_generation",
    "app.services.api_contracts",
)


def _imported_modules(tree: ast.AST) -> set[str]:
    """Retourne les modules importes par le contrat inspecte."""
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_basic_natal_contracts_do_not_import_runtime_layers() -> None:
    """Prouve par AST que le owner canonique reste un module de domaine pur."""
    tree = ast.parse(CONTRACT_PATH.read_text(encoding="utf-8"))

    imported_modules = _imported_modules(tree)

    assert not {
        module
        for module in imported_modules
        for forbidden in FORBIDDEN_IMPORT_ROOTS
        if module == forbidden or module.startswith(f"{forbidden}.")
    }


def test_basic_natal_contract_documentation_defines_llm_as_writer() -> None:
    """Verifie que la documentation borne le role du LLM."""
    content = DOC_PATH.read_text(encoding="utf-8")

    assert "redacteur controle" in content
    assert "source d'intelligence astrologique" in content

# Commentaire global: garde d'architecture du resolver produit theme natal.
"""Verifie que le domaine theme natal reste independant des couches externes."""

from __future__ import annotations

import ast
from pathlib import Path


def test_theme_natal_domain_has_no_framework_database_frontend_or_llm_imports() -> None:
    """Analyse les imports Python sans dependance au repertoire courant du test."""
    backend_root = Path(__file__).resolve().parents[4]
    domain_root = backend_root / "app" / "domain" / "theme_natal"
    forbidden_roots = ("fastapi", "sqlalchemy", "frontend", "app.api", "app.infra", "app.services")
    forbidden_fragments = (".llm_generation",)

    violations: list[str] = []
    for source_path in sorted(domain_root.glob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            for module_name in _imported_module_names(node):
                if module_name.startswith(forbidden_roots) or any(
                    fragment in module_name for fragment in forbidden_fragments
                ):
                    violations.append(f"{source_path.name}: {module_name}")

    assert violations == []


def _imported_module_names(node: ast.AST) -> tuple[str, ...]:
    """Retourne les modules importes pour les noeuds d'import pertinents."""
    if isinstance(node, ast.Import):
        return tuple(alias.name for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return (node.module,) if node.module is not None else ()
    return ()

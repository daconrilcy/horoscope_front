"""Garde d'architecture entre astrology et prediction.

Ce test verrouille le sens autorise prediction -> astrology et bloque l'inverse.
"""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_IMPORT_PREFIXES = ("app.domain.prediction", "app.services.prediction")
FORBIDDEN_PRODUCT_SYMBOLS = {
    "prediction_categories",
    "house_category_weights",
    "visibility_weight",
    "base_priority",
    "routing_role",
    "DomainRouter",
    "PublicAstroFoundationProjector",
}


def test_astrology_domain_does_not_import_prediction() -> None:
    """Bloque les imports directs de prediction depuis le domaine astrology."""
    violations: list[str] = []
    for path in _astrology_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if _is_forbidden_import(alias.name):
                        violations.append(f"{path}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if _is_forbidden_import(module):
                    violations.append(f"{path}:{node.lineno}: from {module} import ...")

    assert violations == []


def test_astrology_domain_does_not_carry_product_symbols() -> None:
    """Bloque les symboles produit dans les fichiers Python astrology."""
    violations: list[str] = []
    for path in _astrology_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_PRODUCT_SYMBOLS:
                violations.append(f"{path}:{node.lineno}: {node.id}")
            elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_PRODUCT_SYMBOLS:
                violations.append(f"{path}:{node.lineno}: {node.attr}")
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in FORBIDDEN_PRODUCT_SYMBOLS:
                    violations.append(f"{path}:{node.lineno}: {node.value}")
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in FORBIDDEN_PRODUCT_SYMBOLS:
                    violations.append(f"{path}:{node.lineno}: {node.name}")

    assert violations == []


def _astrology_python_files() -> tuple[Path, ...]:
    """Retourne les fichiers Python actifs du domaine astrology."""
    root = Path(__file__).resolve().parents[2] / "domain" / "astrology"
    return tuple(sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts))


def _is_forbidden_import(module: str) -> bool:
    """Verifie si un module appartient a une dependance prediction interdite."""
    return any(
        module == prefix or module.startswith(f"{prefix}.") for prefix in FORBIDDEN_IMPORT_PREFIXES
    )

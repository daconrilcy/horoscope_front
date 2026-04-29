# Garde d'architecture pour interdire les imports entre modules de tests executables.
"""Verifie que les helpers partages ne sont pas exposes par des fichiers test_*.py."""

from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
TEST_ROOTS = (BACKEND_ROOT / "app" / "tests", BACKEND_ROOT / "tests")

FORBIDDEN_PREFIXES = (
    "app.tests.integration.test_",
    "app.tests.unit.test_",
    "app.tests.regression.test_",
    "tests.integration.test_",
    "tests.unit.test_",
    "tests.regression.test_",
)


def _iter_test_files() -> list[Path]:
    """Retourne les tests backend collectables par les racines connues."""
    files: list[Path] = []
    for root in TEST_ROOTS:
        if not root.exists():
            continue
        files.extend(
            path
            for path in root.rglob("test_*.py")
            if not {".pytest_cache", ".ruff_cache", "__pycache__"} & set(path.parts)
        )
    return sorted(files)


def _imported_modules(tree: ast.AST) -> list[str]:
    """Extrait les modules importes sous forme absolue quand l'AST les expose."""
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
    return modules


def test_backend_tests_do_not_import_executable_test_modules() -> None:
    """Bloque tout nouveau helper partage depuis un module de test executable."""
    offenders: list[str] = []
    for path in _iter_test_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module in _imported_modules(tree):
            if module.startswith(FORBIDDEN_PREFIXES):
                offenders.append(f"{path.relative_to(BACKEND_ROOT)} importe {module}")

    assert offenders == []

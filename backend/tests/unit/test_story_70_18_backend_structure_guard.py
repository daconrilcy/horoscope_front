# Garde-fou Story 70-18 pour la structure fondationnelle backend.
"""Verifie que les namespaces backend restent alignes sur la gouvernance cible."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = BACKEND_ROOT / "app"

APPROVED_BACKEND_ROOT_DIRS = {
    "app",
    "artifacts",
    "docs",
    "logs",
    "migrations",
    "scripts",
    "tests",
    "tools",
}
IGNORED_BACKEND_ROOT_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".tmp-pytest",
}
APPROVED_APP_ROOT_DIRS = {
    "ai_engine",
    "api",
    "application",
    "core",
    "domain",
    "infra",
    "integrations",
    "jobs",
    "ops",
    "prediction",
    "resources",
    "schemas",
    "services",
    "startup",
    "templates",
    "tests",
}
IGNORED_APP_ROOT_DIRS = {"__pycache__"}
DEPRECATED_IMPORT_PATTERNS = ("app.infrastructure",)


def _directory_names(root: Path, ignored: set[str]) -> set[str]:
    """Retourne les dossiers directs utiles pour controler la taxonomie backend."""
    return {path.name for path in root.iterdir() if path.is_dir() and path.name not in ignored}


def _iter_python_files() -> list[Path]:
    """Retourne les fichiers Python suivis par le controle de namespace."""
    roots = (APP_ROOT, BACKEND_ROOT / "scripts", BACKEND_ROOT / "tests")
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if {"__pycache__", ".pytest_cache", ".ruff_cache", ".tmp-pytest"} & set(path.parts):
                continue
            files.append(path)
    return files


def test_backend_root_directories_are_explicitly_approved() -> None:
    """Detecte tout nouveau dossier racine backend non approuve explicitement."""
    actual_dirs = _directory_names(BACKEND_ROOT, IGNORED_BACKEND_ROOT_DIRS)
    assert sorted(actual_dirs - APPROVED_BACKEND_ROOT_DIRS) == []


def test_app_root_directories_are_explicitly_classified() -> None:
    """Detecte tout nouveau dossier `backend/app` non classe dans la gouvernance."""
    actual_dirs = _directory_names(APP_ROOT, IGNORED_APP_ROOT_DIRS)
    assert sorted(actual_dirs - APPROVED_APP_ROOT_DIRS) == []


def test_deprecated_infrastructure_namespace_is_not_reintroduced() -> None:
    """Interdit le retour du namespace concurrent `app.infrastructure`."""
    assert not (APP_ROOT / "infrastructure").exists()

    offenders: list[str] = []
    for path in _iter_python_files():
        if path == Path(__file__):
            continue
        content = path.read_text(encoding="utf-8")
        for pattern in DEPRECATED_IMPORT_PATTERNS:
            if pattern in content:
                offenders.append(f"{path.relative_to(BACKEND_ROOT)} contient {pattern!r}")

    assert offenders == []

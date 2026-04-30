"""Verifie que la topologie des tests backend reste documentee et collectable."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
PYPROJECT_PATH = BACKEND_ROOT / "pyproject.toml"
TOPOLOGY_DOC_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "guard-backend-pytest-test-roots"
    / ("backend-test-topology.md")
)
IGNORED_TEST_PARTS = {".tmp-pytest", ".pytest_cache", "__pycache__"}
APP_TESTS_ROOT = (BACKEND_ROOT / "app" / "tests").resolve()
EXPECTED_NON_TEST_PACKAGE_TEST_DIRS = {
    (BACKEND_ROOT / "app" / "domain" / "llm" / "prompting" / "tests").resolve()
}


def _configured_testpaths() -> set[str]:
    """Retourne les racines pytest configurees sous forme POSIX relative au backend."""
    config = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return set(config["tool"]["pytest"]["ini_options"]["testpaths"])


def _documented_standard_roots() -> set[str]:
    """Extrait les racines standard documentees dans le registre de topologie."""
    return _documented_paths_from_section("## Racines pytest standard")


def _documented_exception_dirs() -> set[Path]:
    """Extrait les exceptions exactes de dossiers `tests` non racines pytest."""
    return {
        (BACKEND_ROOT / path).resolve()
        for path in _documented_paths_from_section("## Exceptions exactes")
    }


def _documented_paths_from_section(section_title: str) -> set[str]:
    """Lit les chemins de la premiere colonne d'une table Markdown ciblee."""
    content = TOPOLOGY_DOC_PATH.read_text(encoding="utf-8")
    paths: set[str] = set()
    in_section = False
    for line in content.splitlines():
        if line.startswith("## "):
            in_section = line == section_title
            continue
        if not in_section:
            continue
        match = re.match(r"\| `([^`]+)` \|", line)
        if match:
            paths.add(match.group(1))
    return paths


def _backend_test_files() -> set[Path]:
    """Inventorie les fichiers de tests backend hors caches et bases temporaires."""
    files: set[Path] = set()
    for pattern in ("test_*.py", "*_test.py"):
        for path in BACKEND_ROOT.rglob(pattern):
            if any(part in IGNORED_TEST_PARTS for part in path.parts):
                continue
            files.add(path.resolve())
    return files


def _is_under_any_root(path: Path, roots: set[str]) -> bool:
    """Indique si un fichier appartient a une racine approuvee."""
    return any(path.is_relative_to((BACKEND_ROOT / root).resolve()) for root in roots)


def test_topology_document_matches_pytest_testpaths() -> None:
    """La documentation et `pyproject.toml` doivent lister les memes racines."""
    assert _documented_standard_roots() == _configured_testpaths()


def test_backend_test_files_are_under_documented_roots() -> None:
    """Aucun fichier de test backend ne doit vivre hors racine documentee."""
    roots = _documented_standard_roots()
    offenders = sorted(
        path.relative_to(BACKEND_ROOT).as_posix()
        for path in _backend_test_files()
        if not _is_under_any_root(path, roots)
    )

    assert offenders == []


def test_domain_packages_do_not_embed_test_files() -> None:
    """Les packages domaine ne doivent pas redevenir proprietaires de dossiers tests."""
    allowed_roots = {APP_TESTS_ROOT, *_documented_exception_dirs()}
    offenders = sorted(
        path.relative_to(BACKEND_ROOT).as_posix()
        for path in (BACKEND_ROOT / "app").rglob("tests")
        if path.is_dir() and path.resolve() not in allowed_roots
    )

    assert offenders == []


def test_non_standard_test_directories_are_exactly_documented() -> None:
    """Les exceptions de dossiers `tests` doivent rester explicites et exactes."""
    assert _documented_exception_dirs() == EXPECTED_NON_TEST_PACKAGE_TEST_DIRS


def test_documented_exceptions_do_not_contain_test_files() -> None:
    """Une exception de package ne doit pas redevenir une racine de tests active."""
    offenders = sorted(
        path.relative_to(BACKEND_ROOT).as_posix()
        for exception_dir in _documented_exception_dirs()
        for pattern in ("test_*.py", "*_test.py")
        for path in exception_dir.rglob(pattern)
    )

    assert offenders == []


def test_no_active_opt_in_suite_is_documented() -> None:
    """La story converge vers zero suite opt-in active."""
    content = TOPOLOGY_DOC_PATH.read_text(encoding="utf-8")
    assert "Aucune suite opt-in active." in content

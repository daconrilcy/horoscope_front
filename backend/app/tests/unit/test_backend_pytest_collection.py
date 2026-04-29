"""Garde la collecte pytest standard contre les tests backend invisibles."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
PYPROJECT_PATH = BACKEND_ROOT / "pyproject.toml"
IGNORED_TEST_PARTS = {
    ".tmp-pytest",
    ".pytest_cache",
    "__pycache__",
}
OPT_IN_TEST_FILES = {
    "app/domain/llm/prompting/tests/test_qualified_context.py": (
        "Suite embarquee hors topologie standard: son package `tests` charge un registre JSON "
        "absent de ce dossier pendant la collecte. Elle reste opt-in jusqu'a convergence de "
        "topologie dediee."
    )
}


def _configured_testpaths() -> list[Path]:
    """Retourne les racines pytest configurees dans le `pyproject.toml` backend."""
    config = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    values = config["tool"]["pytest"]["ini_options"]["testpaths"]
    return [BACKEND_ROOT / value for value in values]


def _backend_test_files() -> set[Path]:
    """Inventorie les fichiers de test backend retenus par convention de nommage."""
    patterns = ("test_*.py", "*_test.py")
    files: set[Path] = set()
    for pattern in patterns:
        for path in BACKEND_ROOT.rglob(pattern):
            if any(part in IGNORED_TEST_PARTS for part in path.parts):
                continue
            files.add(path.resolve())
    return files


def _collected_test_files() -> set[Path]:
    """Execute la collecte standard et extrait les fichiers qui portent des tests."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--ignore=.tmp-pytest"],
        cwd=BACKEND_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    files: set[Path] = set()
    for line in result.stdout.splitlines():
        node_id = line.strip()
        if not node_id or ".py" not in node_id:
            continue
        file_part = node_id.split("::", maxsplit=1)[0]
        if not file_part.endswith(".py"):
            continue
        files.add((BACKEND_ROOT / file_part).resolve())
    return files


def test_configured_pytest_testpaths_exist() -> None:
    """Les racines declarees dans pytest doivent exister reellement."""
    missing = [
        path.relative_to(BACKEND_ROOT).as_posix()
        for path in _configured_testpaths()
        if not path.exists()
    ]

    assert missing == []


def test_standard_pytest_collection_covers_retained_backend_tests() -> None:
    """Tout fichier de test backend conserve doit etre collecte par pytest standard."""
    opt_in_files = {(BACKEND_ROOT / relative_path).resolve() for relative_path in OPT_IN_TEST_FILES}
    static_files = _backend_test_files()
    collected_files = _collected_test_files()
    uncollected = sorted(
        path.relative_to(BACKEND_ROOT).as_posix()
        for path in static_files
        if path not in collected_files and path not in opt_in_files
    )

    assert uncollected == []


def test_opt_in_test_files_are_exact_existing_exceptions() -> None:
    """Les suites optionnelles doivent etre exactes, existantes et justifiees."""
    configured_roots = _configured_testpaths()
    offenders: list[str] = []
    for relative_path, reason in OPT_IN_TEST_FILES.items():
        path = (BACKEND_ROOT / relative_path).resolve()
        if not path.exists():
            offenders.append(f"{relative_path} is missing")
        if not reason:
            offenders.append(f"{relative_path} has no reason")
        if any(path.is_relative_to(root.resolve()) for root in configured_roots):
            offenders.append(f"{relative_path} is already under standard testpaths")

    assert offenders == []

# Garde d'ownership des tests backend qualite et operations.
"""Verifie que les tests backend qualite et operations ont un proprietaire explicite."""

from __future__ import annotations

import re
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
OWNERSHIP_REGISTRY_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "classify-backend-ops-quality-tests"
    / "ops-quality-test-ownership.md"
)
CONCERNED_PATTERN = re.compile(r"(docs|scripts?|ops|secret|security)")
ALLOWED_GROUPS = {"docs", "scripts", "secrets", "security", "ops"}
ALLOWED_OWNERS = {
    "Backend quality suite registry",
    "Security quality suite registry",
    "Backend integration suite",
}
ALLOWED_COLLECTION_DECISIONS = {"standard_backend_pytest"}
REQUIRED_ROW_FIELDS = (
    "file",
    "group",
    "owner",
    "canonical_command",
    "os_dependency",
    "subprocess_dependency",
    "collection_decision",
)


def _concerned_test_files() -> set[str]:
    """Inventorie les tests backend qui exigent une decision d'ownership."""
    return {
        path.relative_to(REPO_ROOT).as_posix()
        for path in BACKEND_ROOT.rglob("test_*.py")
        if not {".tmp-pytest", ".pytest_cache", "__pycache__"}.intersection(path.parts)
        and CONCERNED_PATTERN.search(path.name)
        and path.name != Path(__file__).name
    }


def _ownership_rows() -> dict[str, dict[str, str]]:
    """Parse le registre Markdown d'ownership qualite et operations."""
    rows: dict[str, dict[str, str]] = {}
    duplicate_files: list[str] = []
    for line in OWNERSHIP_REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `backend/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(REQUIRED_ROW_FIELDS):
            raise AssertionError(f"ligne d'ownership invalide: {line}")

        values = dict(zip(REQUIRED_ROW_FIELDS, cells, strict=True))
        file_path = values["file"].strip("`")
        values["file"] = file_path
        values["canonical_command"] = values["canonical_command"].strip("`")
        if file_path in rows:
            duplicate_files.append(file_path)
        rows[file_path] = values

    if duplicate_files:
        raise AssertionError(
            "lignes d'ownership dupliquees: " + ", ".join(sorted(set(duplicate_files)))
        )
    return rows


def test_quality_ops_ownership_registry_covers_current_inventory() -> None:
    """Chaque test docs/scripts/secrets/security/ops doit avoir une ligne unique."""
    registry_rows = _ownership_rows()
    current_files = _concerned_test_files()

    assert sorted(current_files - set(registry_rows)) == []
    assert sorted(set(registry_rows) - current_files) == []


def test_quality_ops_ownership_rows_are_actionable() -> None:
    """Les lignes d'ownership doivent porter owner, commande et dependances."""
    offenders: list[str] = []
    for file_path, row in _ownership_rows().items():
        real_path = REPO_ROOT / file_path
        if not real_path.exists():
            offenders.append(f"{file_path}: missing file")
        if row["group"] not in ALLOWED_GROUPS:
            offenders.append(f"{file_path}: unsupported group {row['group']}")
        if row["owner"] not in ALLOWED_OWNERS:
            offenders.append(f"{file_path}: unsupported owner {row['owner']}")
        if row["collection_decision"] not in ALLOWED_COLLECTION_DECISIONS:
            offenders.append(
                f"{file_path}: unsupported collection decision {row['collection_decision']}"
            )
        if not row["canonical_command"].startswith("pytest -q "):
            offenders.append(f"{file_path}: command must be a targeted pytest command")
        if file_path.removeprefix("backend/") not in row["canonical_command"]:
            offenders.append(f"{file_path}: command does not target the file")
        if not row["os_dependency"] or not row["subprocess_dependency"]:
            offenders.append(f"{file_path}: dependencies must be classified")

    assert offenders == []


def test_quality_ops_suite_decision_keeps_backend_scope_explicit() -> None:
    """Le registre doit documenter l'absence de changement de perimetre backend."""
    content = OWNERSHIP_REGISTRY_PATH.read_text(encoding="utf-8")

    assert "| Standard backend pytest scope changed | no |" in content
    assert "| User approval required | no |" in content
    assert "pytest -q app/tests/unit/test_backend_quality_test_ownership.py" in content

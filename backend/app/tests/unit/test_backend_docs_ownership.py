# Garde locale de classification des documents backend.
"""Verifie que chaque document backend est classe par owner et type d'artefact."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
DOCS_ROOT = BACKEND_ROOT / "docs"
OWNERSHIP_INDEX = DOCS_ROOT / "ownership-index.md"

ALLOWED_ARTIFACT_TYPES = {
    "generated-doc",
    "executable-registry",
    "canonical-spec",
    "human-runbook",
    "historical-note",
    "governance-doc",
    "generated-artifact",
}
ALLOWED_STATUSES = {
    "canonical-guarded",
    "historical-note",
    "non-canonical-human-note",
    "generated-artifact",
}
REQUIRED_FIELDS = ("file", "owner", "artifact_type", "canonical_status", "expected_guard")


def _docs_inventory() -> set[str]:
    """Retourne l'inventaire exact des fichiers suivis sous backend/docs."""
    return {
        path.relative_to(REPO_ROOT).as_posix() for path in DOCS_ROOT.rglob("*") if path.is_file()
    }


def _ownership_rows() -> dict[str, dict[str, str]]:
    """Parse l'index Markdown local sans accepter les lignes incompletes."""
    rows: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    for line in OWNERSHIP_INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `backend/docs/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(REQUIRED_FIELDS):
            raise AssertionError(f"ligne d'ownership invalide: {line}")
        values = dict(zip(REQUIRED_FIELDS, cells, strict=True))
        file_path = values["file"].strip("`")
        values["file"] = file_path
        values["expected_guard"] = values["expected_guard"].strip("`")
        if file_path in rows:
            duplicates.append(file_path)
        rows[file_path] = values

    if duplicates:
        raise AssertionError("lignes dupliquees: " + ", ".join(sorted(set(duplicates))))
    return rows


def test_backend_docs_ownership_index_covers_current_inventory() -> None:
    """Tout fichier backend/docs doit etre reference exactement une fois."""
    rows = _ownership_rows()
    inventory = _docs_inventory()

    assert sorted(inventory - set(rows)) == []
    assert sorted(set(rows) - inventory) == []


def test_backend_docs_ownership_rows_are_actionable() -> None:
    """Chaque ligne doit porter un owner, un type connu, un statut et une garde."""
    offenders: list[str] = []
    for file_path, row in _ownership_rows().items():
        if not (REPO_ROOT / file_path).exists():
            offenders.append(f"{file_path}: missing file")
        if not row["owner"]:
            offenders.append(f"{file_path}: missing owner")
        if row["artifact_type"] not in ALLOWED_ARTIFACT_TYPES:
            offenders.append(f"{file_path}: unsupported artifact type {row['artifact_type']}")
        if row["canonical_status"] not in ALLOWED_STATUSES:
            offenders.append(f"{file_path}: unsupported status {row['canonical_status']}")
        if not row["expected_guard"].startswith("pytest -q "):
            offenders.append(f"{file_path}: expected guard must be a targeted pytest command")

    assert offenders == []


def test_backend_docs_ownership_rejects_vague_classifications() -> None:
    """Les classifications vagues ne doivent pas devenir des types acceptes."""
    forbidden = {"misc", "todo", "unknown", "other"}
    used_types = {row["artifact_type"] for row in _ownership_rows().values()}

    assert used_types.isdisjoint(forbidden)

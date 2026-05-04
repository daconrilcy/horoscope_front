# Garde de gouvernance des documents LLM backend.
"""Verifie que les docs LLM normatives sont gardees ou declassifiees."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
DOCS_ROOT = BACKEND_ROOT / "docs"
ROOT_LLM_DOCS = REPO_ROOT / "docs" / "llm"
GOVERNANCE_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "CS-022-uniformiser-gouvernance-docs-llm-source-truth"
    / "llm-doc-governance.md"
)
NORMATIVE_TERMS = ("source-of-truth", "source de verite", "canonical", "canonique")
GUARDED_STATUSES = {"generated-guarded", "executable-registry"}
ALLOWED_STATUSES = GUARDED_STATUSES | {"non-canonical-human-note"}
MOVED_HUMAN_LLM_DOCS = {
    "docs/llm/llm-db-governance.md",
    "docs/llm/llm-runtime-source-of-truth.md",
    "docs/llm/llm-canonical-consumption-rebuild.md",
}
FORBIDDEN_BACKEND_LLM_NOTES = {
    "backend/docs/llm-db-governance.md",
    "backend/docs/llm-runtime-source-of-truth.md",
    "backend/docs/llm-canonical-consumption-rebuild.md",
}


def _llm_docs_inventory() -> set[str]:
    """Liste les documents LLM gardes par le registre de gouvernance."""
    return {
        path.relative_to(REPO_ROOT).as_posix() for path in DOCS_ROOT.glob("llm-*") if path.is_file()
    } | {
        path.relative_to(REPO_ROOT).as_posix()
        for path in ROOT_LLM_DOCS.glob("llm-*")
        if path.is_file()
    }


def _governance_rows() -> dict[str, dict[str, str]]:
    """Parse les lignes de gouvernance LLM en imposant les colonnes attendues."""
    rows: dict[str, dict[str, str]] = {}
    for line in GOVERNANCE_PATH.read_text(encoding="utf-8").splitlines():
        if not (line.startswith("| `backend/docs/llm-") or line.startswith("| `docs/llm/llm-")):
            continue
        file_path, status, runtime_source, guard = [
            cell.strip() for cell in line.strip("|").split("|")
        ]
        rows[file_path.strip("`")] = {
            "status": status,
            "runtime_source": runtime_source,
            "guard": guard.strip("`"),
        }
    return rows


def test_llm_docs_governance_covers_all_llm_docs() -> None:
    """Chaque fichier LLM doit avoir une classification persistante."""
    rows = _governance_rows()
    inventory = _llm_docs_inventory()

    assert sorted(inventory - set(rows)) == []
    assert sorted(set(rows) - inventory) == []


def test_non_canonical_llm_notes_are_outside_backend_docs() -> None:
    """Les notes LLM humaines deplacees doivent rester hors backend/docs."""
    rows = _governance_rows()

    assert MOVED_HUMAN_LLM_DOCS <= set(rows)
    assert FORBIDDEN_BACKEND_LLM_NOTES.isdisjoint(_llm_docs_inventory())
    for file_path in MOVED_HUMAN_LLM_DOCS:
        assert (REPO_ROOT / file_path).exists()


def test_llm_docs_governance_rows_are_guarded_or_non_canonical() -> None:
    """Aucune ligne LLM ne doit avoir un statut vague ou une garde absente."""
    offenders: list[str] = []
    for file_path, row in _governance_rows().items():
        if row["status"] not in ALLOWED_STATUSES:
            offenders.append(f"{file_path}: unsupported status {row['status']}")
        if not row["runtime_source"]:
            offenders.append(f"{file_path}: missing runtime source")
        if not row["guard"].startswith("pytest -q "):
            offenders.append(f"{file_path}: missing pytest guard")

    assert offenders == []


def test_llm_normative_terms_require_guard_or_non_canonical_status() -> None:
    """Tout terme source-of-truth doit etre classe comme garde ou note non canonique."""
    rows = _governance_rows()
    offenders: list[str] = []
    for file_path in _llm_docs_inventory():
        text = (REPO_ROOT / file_path).read_text(encoding="utf-8").lower()
        if any(term in text for term in NORMATIVE_TERMS):
            status = rows[file_path]["status"]
            if status not in ALLOWED_STATUSES:
                offenders.append(f"{file_path}: unclassified normative wording")
            if (
                status == "non-canonical-human-note"
                and "document status: non-canonical" not in text
            ):
                offenders.append(f"{file_path}: missing in-file non-canonical status")

    assert offenders == []


def test_existing_llm_executable_guards_remain_declared() -> None:
    """Les gardes existantes du rendu LLM et du registre cleanup doivent rester visibles."""
    rows = _governance_rows()

    assert rows["backend/docs/llm-model-structure.md"]["status"] == "generated-guarded"
    assert (
        rows["backend/docs/llm-model-structure.md"]["guard"]
        == "pytest -q tests/unit/test_llm_canonical_perimeter.py"
    )
    assert rows["backend/docs/llm-db-cleanup-registry.json"]["status"] == "executable-registry"
    assert (
        rows["backend/docs/llm-db-cleanup-registry.json"]["guard"]
        == "pytest -q tests/integration/test_llm_db_cleanup_registry.py"
    )

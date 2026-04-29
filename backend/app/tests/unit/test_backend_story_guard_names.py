"""Controle le catalogue durable des anciens tests nommes par story."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
MAPPING_PATH = (
    REPO_ROOT
    / "_condamad"
    / "stories"
    / "reclassify-story-regression-guards"
    / "story-guard-mapping.md"
)
ALLOWED_CLASSIFICATIONS = {"migrated"}


def _story_test_files() -> set[str]:
    """Retourne les fichiers story-numbered encore presents dans le backend."""
    return {
        path.relative_to(REPO_ROOT).as_posix()
        for path in BACKEND_ROOT.rglob("test_story_*.py")
        if "__pycache__" not in path.parts
    }


def _mapping_rows() -> dict[str, dict[str, str]]:
    """Lit le registre persistant des guards story-numbered."""
    rows: dict[str, dict[str, str]] = {}
    for line in MAPPING_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `backend/"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            raise AssertionError(f"ligne de mapping invalide: {line}")
        file_path, classification, invariant, target, decision = cells
        rows[file_path.strip("`")] = {
            "classification": classification,
            "invariant": invariant,
            "target": target,
            "decision": decision,
        }
    return rows


def test_numbered_guard_mapping_is_complete_and_classified() -> None:
    """Chaque ancien fichier story-numbered doit avoir une migration durable."""
    rows = _mapping_rows()
    current_files = _story_test_files()

    assert sorted(current_files - set(rows)) == []
    assert current_files == set()
    assert all(row["classification"] in ALLOWED_CLASSIFICATIONS for row in rows.values())
    assert all(row["invariant"] for row in rows.values())
    assert all(row["decision"] for row in rows.values())


def test_migrated_story_guard_files_are_absent_from_backend() -> None:
    """Les fichiers migres ne doivent pas redevenir des noms story-numbered actifs."""
    rows = _mapping_rows()
    current_files = _story_test_files()
    migrated_files = {
        file_path for file_path, row in rows.items() if row["classification"] == "migrated"
    }

    assert migrated_files.isdisjoint(current_files)


def test_guard_mapping_points_to_existing_canonical_targets() -> None:
    """Le lot migre doit pointer vers des fichiers canoniques reels."""
    rows = _mapping_rows()
    missing_targets: list[str] = []
    for file_path, row in rows.items():
        if row["classification"] != "migrated":
            continue
        target = row["target"].strip("`")
        if not target.startswith("backend/"):
            missing_targets.append(f"{file_path} target is not backend-relative")
            continue
        if not (REPO_ROOT / target).exists():
            missing_targets.append(target)

    assert missing_targets == []

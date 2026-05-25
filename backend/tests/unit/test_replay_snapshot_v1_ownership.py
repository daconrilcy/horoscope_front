# Commentaire global: ces tests verrouillent l'owner canonique du stockage replay_snapshot_v1.
"""Tests d'architecture pour l'owner unique des snapshots de rejeu."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_ROOT = REPO_ROOT / "backend" / "app" / "infra" / "db" / "models"


def _python_files(root: Path) -> list[Path]:
    """Liste les fichiers Python applicatifs hors caches."""
    return [
        path
        for path in root.rglob("*.py")
        if not any(part in {"__pycache__", ".pytest_cache", ".ruff_cache"} for part in path.parts)
    ]


def test_replay_snapshot_model_is_the_only_table_owner() -> None:
    """Prouve que `llm_replay_snapshots` reste l'unique table canonique."""
    owners: list[str] = []
    for path in _python_files(MODEL_ROOT):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == "__tablename__"
                        for target in statement.targets
                    )
                    and isinstance(statement.value, ast.Constant)
                    and statement.value.value == "llm_replay_snapshots"
                ):
                    owners.append(f"{path.relative_to(REPO_ROOT)}:{node.name}")

    assert owners == [
        "backend\\app\\infra\\db\\models\\llm\\llm_observability.py:LlmReplaySnapshotModel"
    ]


def test_replay_snapshot_creation_uses_canonical_owner_only() -> None:
    """Verifie que le service canonique instancie seulement le modele approuve."""
    service_path = REPO_ROOT / "backend" / "app" / "services" / "replay_snapshot_v1_service.py"
    tree = ast.parse(service_path.read_text(encoding="utf-8"))

    created_classes = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]

    assert created_classes.count("LlmReplaySnapshotModel") == 1
    assert "ReplaySnapshotModel" not in created_classes


def test_observability_delegates_replay_snapshot_creation() -> None:
    """Verifie que le runtime LLM ne conserve pas de second writer replay."""
    observability_path = (
        REPO_ROOT / "backend" / "app" / "domain" / "llm" / "runtime" / "observability_service.py"
    )
    source = observability_path.read_text(encoding="utf-8")

    assert "ReplaySnapshotV1Service.create_snapshot" in source
    assert "LlmReplaySnapshotModel(" not in source

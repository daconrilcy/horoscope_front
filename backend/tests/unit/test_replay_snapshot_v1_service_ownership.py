# Commentaire global: ces tests verrouillent l'owner applicatif canonique replay_snapshot_v1.
"""Gardes d'architecture pour le service replay_snapshot_v1."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"
SERVICE_PATH = APP_ROOT / "services" / "replay_snapshot_v1_service.py"
OBSERVABILITY_PATH = APP_ROOT / "domain" / "llm" / "runtime" / "observability_service.py"
REPLAY_PATH = APP_ROOT / "ops" / "llm" / "replay_service.py"
ADMIN_AUDIT_ROUTER_PATH = APP_ROOT / "api" / "v1" / "routers" / "admin" / "audit.py"


def _calls_in(path: Path, name: str) -> list[ast.Call]:
    """Retourne les appels directs a un symbole donne dans un fichier Python."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called = node.func
            if isinstance(called, ast.Name) and called.id == name:
                calls.append(node)
            if isinstance(called, ast.Attribute) and called.attr == name:
                calls.append(node)
    return calls


def test_replay_snapshot_v1_service_is_the_only_lifecycle_owner() -> None:
    """Prouve que les decisions create, metadata et purge vivent dans le service."""
    source = SERVICE_PATH.read_text(encoding="utf-8")

    assert "class ReplaySnapshotV1Service" in source
    for method_name in (
        "create_snapshot",
        "get_snapshot_metadata",
        "get_replay_payload_snapshot",
        "purge_expired",
        "purge_snapshot",
    ):
        assert f"def {method_name}" in source


def test_observability_and_replay_delegate_lifecycle_decisions() -> None:
    """Prouve que les anciens owners appellent le service au lieu de dupliquer la politique."""
    observability_source = OBSERVABILITY_PATH.read_text(encoding="utf-8")
    replay_source = REPLAY_PATH.read_text(encoding="utf-8")

    assert "ReplaySnapshotV1Service.create_snapshot" in observability_source
    assert "ReplaySnapshotV1Service.purge_expired" in observability_source
    assert "ReplaySnapshotV1Service.get_replay_payload_snapshot" in replay_source
    assert len(_calls_in(OBSERVABILITY_PATH, "LlmReplaySnapshotModel")) == 0


def test_no_public_api_or_duplicate_service_surface_is_added() -> None:
    """Prouve que seule l'API admin CS-297 expose replay_snapshot_v1."""
    service_files = [
        path
        for path in (APP_ROOT / "services").rglob("*.py")
        if "ReplaySnapshotV1Service" in path.read_text(encoding="utf-8")
    ]
    api_hits = [
        path
        for path in (APP_ROOT / "api").rglob("*.py")
        if "replay_snapshot_v1" in path.read_text(encoding="utf-8")
    ]

    assert service_files == [SERVICE_PATH]
    assert api_hits == [ADMIN_AUDIT_ROUTER_PATH]

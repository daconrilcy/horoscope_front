# Commentaire global: ces tests verrouillent l'exposition strictement admin du replay snapshot v1.
"""Gardes d'architecture pour l'API admin `replay_snapshot_v1`."""

from __future__ import annotations

from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_APP = REPO_ROOT / "backend" / "app"
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"
ADMIN_REPLAY_BASE_PATH = "/v1/admin/audit/replay_snapshot_v1/{snapshot_id}"
ADMIN_REPLAY_ATTEMPT_PATH = f"{ADMIN_REPLAY_BASE_PATH}/replay-attempt"
FORBIDDEN_REPLAY_PATHS = {
    "/v1/replay_snapshot_v1",
    "/v1/public/replay_snapshot_v1",
    "/v1/support/replay_snapshot_v1",
    "/api/replay_snapshot_v1",
    "/replay_snapshot_v1",
}
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".jsx", ".md", ".ts", ".tsx"}


def _runtime_methods_by_path() -> dict[str, set[str]]:
    """Retourne les methodes HTTP declarees par chemin runtime charge."""
    methods_by_path: dict[str, set[str]] = {}
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()
        methods_by_path.setdefault(path, set()).update(methods)
    return methods_by_path


def test_runtime_exposes_only_the_three_admin_replay_operations() -> None:
    """Controle les chemins et methodes runtime autorises pour CS-297."""
    methods_by_path = _runtime_methods_by_path()
    replay_paths = {path for path in methods_by_path if "replay_snapshot_v1" in path}

    assert replay_paths == {ADMIN_REPLAY_BASE_PATH, ADMIN_REPLAY_ATTEMPT_PATH}
    assert {"GET", "DELETE"} <= methods_by_path[ADMIN_REPLAY_BASE_PATH]
    assert {"POST"} <= methods_by_path[ADMIN_REPLAY_ATTEMPT_PATH]
    assert FORBIDDEN_REPLAY_PATHS.isdisjoint(methods_by_path)


def test_openapi_exposes_replay_snapshot_only_under_admin_audit() -> None:
    """Controle la publication OpenAPI interne sans chemin client ou support."""
    paths = app.openapi()["paths"]
    replay_paths = {path for path in paths if "replay_snapshot_v1" in path}

    assert replay_paths == {ADMIN_REPLAY_BASE_PATH, ADMIN_REPLAY_ATTEMPT_PATH}
    assert set(paths[ADMIN_REPLAY_BASE_PATH]) == {"get", "delete"}
    assert set(paths[ADMIN_REPLAY_ATTEMPT_PATH]) == {"post"}
    assert all(path.startswith("/v1/admin/audit") for path in replay_paths)
    assert FORBIDDEN_REPLAY_PATHS.isdisjoint(paths)


def test_replay_snapshot_has_no_frontend_or_public_router_exposure() -> None:
    """Verifie l'absence de consommation frontend et de route publique."""
    public_router_root = BACKEND_APP / "api" / "v1" / "routers" / "public"
    public_mentions = [
        path
        for path in public_router_root.rglob("*.py")
        if "replay_snapshot_v1" in path.read_text(encoding="utf-8")
    ]
    frontend_mentions = (
        [
            path
            for path in FRONTEND_SRC.rglob("*")
            if path.is_file()
            and path.suffix in TEXT_SUFFIXES
            and "replay_snapshot_v1" in path.read_text(encoding="utf-8")
        ]
        if FRONTEND_SRC.exists()
        else []
    )

    assert public_mentions == []
    assert frontend_mentions == []

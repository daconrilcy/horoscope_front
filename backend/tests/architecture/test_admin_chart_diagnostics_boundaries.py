# Commentaire global: ces tests protegent les frontieres runtime du diagnostic admin astrologique.
"""Gardes d'architecture pour `admin_chart_diagnostics_v1`."""

from __future__ import annotations

import ast
from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
SERVICE_PATH = REPO_ROOT / "backend" / "app" / "services" / "ops" / "admin_chart_diagnostics.py"
ROUTER_PATH = (
    REPO_ROOT / "backend" / "app" / "api" / "v1" / "routers" / "admin" / "chart_diagnostics.py"
)
PUBLIC_ROUTERS = REPO_ROOT / "backend" / "app" / "api" / "v1" / "routers" / "public"
FORBIDDEN_IMPORT_FRAGMENTS = {
    "answer_audit",
    "rejected_answer_review",
    "llm_" + "replay",
    "replay_snapshot",
    "narrative_answer_audit",
}
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".jsx", ".md", ".ts", ".tsx"}


def test_route_registered_once_under_admin_family() -> None:
    """Verifie l'unicite du chemin runtime et son absence des routes publiques."""
    paths = [route.path for route in app.routes if "admin_chart_diagnostics_v1" in route.path]

    assert paths == ["/v1/admin/audit/admin_chart_diagnostics_v1/{chart_reference}"]
    assert not any(path.startswith("/v1/public") for path in paths)


def test_openapi_exposes_projection_only_under_admin_path() -> None:
    """Controle l'exposition OpenAPI interne de la projection."""
    paths = app.openapi()["paths"]
    matching_paths = [path for path in paths if "admin_chart_diagnostics_v1" in path]

    assert matching_paths == ["/v1/admin/audit/admin_chart_diagnostics_v1/{chart_reference}"]


def test_diagnostic_service_keeps_replay_and_answer_audit_separate() -> None:
    """Bloque les imports vers le replay ou l'audit narratif."""
    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_modules.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )

    assert not any(
        fragment in module for module in imported_modules for fragment in FORBIDDEN_IMPORT_FRAGMENTS
    )


def test_public_routers_and_frontend_do_not_consume_projection() -> None:
    """Verifie que la projection ne fuit pas vers les surfaces client."""
    public_mentions = [
        path
        for path in PUBLIC_ROUTERS.rglob("*.py")
        if "admin_chart_diagnostics_v1" in path.read_text(encoding="utf-8")
    ]
    frontend_root = REPO_ROOT / "frontend" / "src"
    frontend_mentions = (
        [
            path
            for path in frontend_root.rglob("*")
            if path.is_file()
            and path.suffix in TEXT_SUFFIXES
            and "admin_chart_diagnostics_v1" in path.read_text(encoding="utf-8")
        ]
        if frontend_root.exists()
        else []
    )

    assert public_mentions == []
    assert frontend_mentions == []


def test_canonical_owners_are_unique() -> None:
    """Controle qu'il n'existe qu'un routeur et un service proprietaires."""
    assert ROUTER_PATH.exists()
    assert SERVICE_PATH.exists()
    owner_files = {
        path
        for path in (REPO_ROOT / "backend" / "app").rglob("*.py")
        if "admin_chart_diagnostics_v1" in path.read_text(encoding="utf-8")
    }

    assert ROUTER_PATH in owner_files
    assert SERVICE_PATH in owner_files
    assert len([path for path in owner_files if path.name == "chart_diagnostics.py"]) == 2
    assert len([path for path in owner_files if path.name == "admin_chart_diagnostics.py"]) == 1

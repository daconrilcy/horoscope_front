# Commentaire global: ces tests bloquent les doublons et fuites de l'audit narratif.
"""Gardes d'architecture pour la persistance `narrative_answer_audit_v1`."""

from __future__ import annotations

from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = REPO_ROOT / "backend" / "app"
FRONTEND_ROOT = REPO_ROOT / "frontend" / "src"
CANONICAL_MODEL = APP_ROOT / "infra" / "db" / "models" / "user_natal_interpretation.py"
CANONICAL_REPOSITORY = (
    APP_ROOT / "infra" / "db" / "repositories" / "llm" / "narrative_answer_audit_repository.py"
)
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".jsx", ".md", ".ts", ".tsx"}


def test_no_narrative_answer_audit_table_or_model_is_added() -> None:
    """Verifie que l'audit etend le stockage existant sans table parallele."""
    duplicate_model_paths = [
        path
        for path in (APP_ROOT / "infra" / "db" / "models").rglob("*.py")
        if path.name != CANONICAL_MODEL.name and "answer_id" in path.read_text(encoding="utf-8")
    ]

    assert CANONICAL_MODEL.exists()
    assert duplicate_model_paths == []


def test_audit_is_not_exposed_through_routes_openapi_or_frontend() -> None:
    """Controle l'absence d'exposition client ou API de la persistance d'audit."""
    assert "narrative_answer_audit_v1" not in str(app.openapi())
    assert all("narrative_answer_audit" not in getattr(route, "path", "") for route in app.routes)

    frontend_mentions = (
        [
            path
            for path in FRONTEND_ROOT.rglob("*")
            if path.is_file()
            and path.suffix in TEXT_SUFFIXES
            and "narrative_answer_audit" in path.read_text(encoding="utf-8")
        ]
        if FRONTEND_ROOT.exists()
        else []
    )
    assert frontend_mentions == []


def test_create_read_owner_is_single_repository() -> None:
    """Verifie qu'un seul repository porte les operations audit create/read."""
    repository_mentions = [
        path
        for path in (APP_ROOT / "infra" / "db" / "repositories").rglob("*.py")
        if "NarrativeAnswerAuditRepository" in path.read_text(encoding="utf-8")
    ]

    assert repository_mentions == [CANONICAL_REPOSITORY]

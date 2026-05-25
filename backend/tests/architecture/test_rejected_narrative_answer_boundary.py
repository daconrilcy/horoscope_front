# Commentaire global: ces gardes conservent un seul workflow CS-290 sans surface publique.
"""Gardes d'architecture du workflow de rejet narratif."""

from __future__ import annotations

import ast
from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = REPO_ROOT / "backend" / "app"
WORKFLOW = APP_ROOT / "services" / "llm_generation" / "natal" / "rejected_answer_workflow.py"
ALLOWED_RETRY_OWNER = "retry_policy"


def test_rejected_answer_workflow_has_single_owner() -> None:
    """Verifie que le workflow de rejet n'est pas duplique."""
    owners = [
        path
        for path in (APP_ROOT / "services").rglob("*.py")
        if _defines_function(path, "build_rejected_narrative_answer_outcome")
    ]

    assert owners == [WORKFLOW]


def test_rejected_answer_workflow_does_not_expose_public_runtime_surface() -> None:
    """Controle l'absence de route ou schema OpenAPI public dedie au rejet."""
    assert "rejected_narrative_answer" not in str(app.openapi())
    assert all("rejected-narrative" not in getattr(route, "path", "") for route in app.routes)


def test_rejected_answer_workflow_does_not_add_retry_queue() -> None:
    """Bloque l'ajout d'une file de retry dans le scope CS-290."""
    workflow_source = WORKFLOW.read_text(encoding="utf-8")
    forbidden = [
        token
        for token in ("retry_queue", "retry_worker", "manual_publish")
        if token in workflow_source
    ]

    assert forbidden == []
    assert ALLOWED_RETRY_OWNER in workflow_source


def _defines_function(path: Path, function_name: str) -> bool:
    """Detecte une definition de fonction sans dependre d'un grep fragile."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.FunctionDef) and node.name == function_name for node in tree.body
    )

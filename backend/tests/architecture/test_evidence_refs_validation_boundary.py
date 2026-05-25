# Commentaire global: ces gardes bloquent les validateurs paralleles de preuves narratives.
"""Gardes d'architecture pour la validation canonique des `evidence_refs`."""

from __future__ import annotations

import ast
from pathlib import Path

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = REPO_ROOT / "backend" / "app"
FRONTEND_ROOT = REPO_ROOT / "frontend" / "src"
CANONICAL_VALIDATOR = (
    APP_ROOT / "domain" / "astrology" / "interpretation" / "evidence_refs_validation.py"
)
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".jsx", ".md", ".ts", ".tsx"}


def test_single_canonical_evidence_refs_validator() -> None:
    """Verifie qu'un seul module applicatif porte le validateur de preuves."""
    validator_definitions = [
        path for path in APP_ROOT.rglob("*.py") if _defines_validate_evidence_refs_by_section(path)
    ]

    assert validator_definitions == [CANONICAL_VALIDATOR]


def test_evidence_refs_proof_internals_are_not_exposed_to_api_or_frontend() -> None:
    """Controle l'absence de route ou schema client pour les preuves techniques."""
    openapi_payload = str(app.openapi())
    assert "evidence_refs_validation" not in openapi_payload
    assert all("evidence_refs" not in getattr(route, "path", "") for route in app.routes)

    frontend_mentions = (
        [
            path
            for path in FRONTEND_ROOT.rglob("*")
            if path.is_file()
            and path.suffix in TEXT_SUFFIXES
            and "source_hash" in path.read_text(encoding="utf-8")
        ]
        if FRONTEND_ROOT.exists()
        else []
    )
    assert frontend_mentions == []


def _defines_validate_evidence_refs_by_section(path: Path) -> bool:
    """Detecte la definition du validateur sans bloquer ses imports canoniques."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return any(
        isinstance(node, ast.FunctionDef) and node.name == "validate_evidence_refs_by_section"
        for node in ast.walk(tree)
    )

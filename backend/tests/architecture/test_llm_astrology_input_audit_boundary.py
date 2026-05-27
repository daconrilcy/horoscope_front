# Commentaire global: ces gardes empechent un owner parallele du hash LLM astrologique.
"""Verifie la frontiere publique et les owners de hash CS-333."""

from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"
LLM_INPUT_OWNER = APP_ROOT / "domain/astrology/interpretation/llm_astrology_input_v1.py"
NATAL_AUDIT_OWNER = APP_ROOT / "services/llm_generation/natal/interpretation_service.py"


def test_llm_input_hash_material_has_single_owner() -> None:
    """Le materiau canonique de `llm_input_hash` reste dans le domaine interpretation."""
    owner_files = [
        path
        for path in APP_ROOT.rglob("*.py")
        if "build_llm_input_hash_material" in path.read_text(encoding="utf-8")
    ]

    assert owner_files == [LLM_INPUT_OWNER]


def test_natal_audit_imports_llm_input_contract_version() -> None:
    """L'audit natal reference le contrat LLM au lieu d'une identite request-only."""
    tree = ast.parse(NATAL_AUDIT_OWNER.read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    source = NATAL_AUDIT_OWNER.read_text(encoding="utf-8")

    assert "LLM_ASTROLOGY_INPUT_V1_CONTRACT_VERSION" in imported_names
    assert "llm_input_identity" not in source


def test_llm_input_audit_alignment_stays_out_of_public_api() -> None:
    """Aucune route ni schema OpenAPI ne publie l'alignement d'audit interne."""
    client = TestClient(app)
    serialized_openapi = str(app.openapi())

    assert "llm_input_hash" not in serialized_openapi
    assert all("llm-input" not in getattr(route, "path", "") for route in app.routes)
    assert client.get("/health").status_code == 200

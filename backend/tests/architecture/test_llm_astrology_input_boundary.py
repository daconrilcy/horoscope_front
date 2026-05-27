# Garde d'architecture du mapper interne llm_astrology_input_v1.
"""Verifie que le mapper LLM reste interne au domaine interpretation."""

from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"
INTERPRETATION_DIR = APP_ROOT / "domain/astrology/interpretation"
MAPPER_PATH = INTERPRETATION_DIR / "llm_astrology_input_v1.py"


def test_llm_astrology_input_mapper_has_single_domain_owner() -> None:
    """Le builder canonique ne doit pas etre duplique hors interpretation."""
    owner_files = [
        path
        for path in INTERPRETATION_DIR.glob("*.py")
        if "LLMAstrologyInputV1Builder" in path.read_text(encoding="utf-8")
    ]

    assert owner_files == [MAPPER_PATH]


def test_llm_astrology_input_mapper_reuses_canonical_sources() -> None:
    """Les facts et signaux passent par les owners imposes par l'architecture."""
    tree = ast.parse(MAPPER_PATH.read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "AINarrativeInputContract" in imported_names
    assert "STRUCTURED_FACTS_V1_PROJECTION_ID" in imported_names
    assert "validate_evidence_refs_by_section" in imported_names


def test_llm_astrology_input_mapper_stays_out_of_public_api() -> None:
    """Le mapper ne cree aucun chemin HTTP ni schema OpenAPI public."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    schemas = app.openapi().get("components", {}).get("schemas", {})
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert all("llm_astrology" not in path for path in route_paths)
    assert "LLMAstrologyInputV1Builder" not in schemas
    assert "llm_astrology_input_v1" not in serialized_openapi
    assert client.get("/openapi.json").status_code == 200

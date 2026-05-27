# Garde runtime du transport llm_astrology_input_v1 natal.
"""Verifie que le contrat riche reste interne au runtime natal."""

from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.llm.runtime.contracts import ExecutionContext
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"
ADAPTER_PATH = APP_ROOT / "domain/llm/runtime/adapter.py"
CONTRACTS_PATH = APP_ROOT / "domain/llm/runtime/contracts.py"


def test_execution_context_does_not_own_llm_astrology_facts() -> None:
    """ExecutionContext ne porte pas de champ factuel dedie au contrat riche."""
    assert "llm_astrology_input_v1" not in ExecutionContext.model_fields


def test_adapter_propagates_llm_astrology_input_through_extra_context() -> None:
    """L'adaptateur transmet la cle riche sans creer de second owner runtime."""
    tree = ast.parse(ADAPTER_PATH.read_text(encoding="utf-8"))
    constants = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)}
    names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert "llm_astrology_input_v1" in constants
    assert "llm_astrology_input_v1" in names


def test_natal_execution_input_is_the_typed_transport_owner() -> None:
    """Le contrat type expose le champ riche uniquement sur NatalExecutionInput."""
    tree = ast.parse(CONTRACTS_PATH.read_text(encoding="utf-8"))
    class_fields: dict[str, set[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_fields[node.name] = {
                statement.target.id
                for statement in node.body
                if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
            }

    assert "llm_astrology_input_v1" in class_fields["NatalExecutionInput"]
    assert "llm_astrology_input_v1" not in class_fields["ExecutionContext"]


def test_llm_astrology_input_stays_out_of_public_openapi_surface() -> None:
    """Le wiring runtime ne cree aucune route ni schema public."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert all("llm_astrology" not in path for path in route_paths)
    assert "llm_astrology_input_v1" not in serialized_openapi
    assert client.get("/openapi.json").status_code == 200

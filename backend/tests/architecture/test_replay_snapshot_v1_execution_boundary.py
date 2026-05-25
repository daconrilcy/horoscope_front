# Commentaire global: ces gardes verrouillent la frontiere d'execution replay_snapshot_v1.
"""Gardes d'architecture CS-298 pour l'execution replay_snapshot_v1."""

from __future__ import annotations

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2] / "app"
ADMIN_AUDIT_ROUTER = APP_ROOT / "api" / "v1" / "routers" / "admin" / "audit.py"
REPLAY_SERVICE = APP_ROOT / "ops" / "llm" / "replay_service.py"


def _source(path: Path) -> str:
    """Charge une source applicative precise pour inspection AST."""
    return path.read_text(encoding="utf-8")


def test_admin_router_does_not_execute_provider_directly() -> None:
    """Prouve que le routeur admin ne possede pas de chemin provider direct."""
    source = _source(ADMIN_AUDIT_ROUTER)
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    assert "LLMGateway" not in names
    assert "gateway.execute(" not in source
    assert "execute_request(" not in source


def test_replay_service_validates_snapshot_before_gateway_execution() -> None:
    """Prouve que l'execution provider reste apres validation du snapshot v1."""
    source = _source(REPLAY_SERVICE)

    snapshot_check = source.index("ReplaySnapshotV1Service.get_replay_payload_snapshot")
    refusal_check = source.index('snapshot_result.status != "success"')
    gateway_execution = source.index("gateway.execute(")

    assert snapshot_check < refusal_check < gateway_execution


def test_replay_service_never_emits_raw_provider_output() -> None:
    """Prouve que le resultat de replay reste borne a une synthese sans payload brut."""
    source = _source(REPLAY_SERVICE)

    assert "raw_output=None" in source
    assert "structured_output=None" in source

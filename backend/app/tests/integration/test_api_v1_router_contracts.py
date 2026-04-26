"""Contrats OpenAPI minimaux pour les routeurs API v1 conserves."""

from __future__ import annotations

from app.main import app

EXPECTED_ROUTE_METHODS = {
    ("/v1/admin/llm/catalog", "get"),
    ("/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample", "post"),
    ("/v1/admin/llm/assembly/configs", "get"),
    ("/v1/admin/llm/consumption/canonical", "get"),
    ("/v1/admin/llm/releases/{snapshot_id}/activate", "post"),
    ("/v1/admin/content/texts", "get"),
    ("/v1/b2b/astrology/weekly-by-sign", "get"),
    ("/v1/ops/monitoring/conversation-kpis", "get"),
    ("/v1/predictions/daily", "get"),
    ("/v1/users/me/birth-data", "get"),
}


def test_conserved_v1_routes_remain_in_openapi() -> None:
    """Les chemins publics conserves restent montes apres le rangement Python."""
    schema = app.openapi()
    missing = [
        f"{method.upper()} {path}"
        for path, method in sorted(EXPECTED_ROUTE_METHODS)
        if method not in schema["paths"].get(path, {})
    ]

    assert missing == []

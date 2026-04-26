"""Contrats OpenAPI verifies contre les facades historiques supprimees."""

from __future__ import annotations

from app.main import app


def test_openapi_does_not_expose_public_ai_facade_paths() -> None:
    """L'OpenAPI FastAPI doit exposer uniquement les routes LLM canoniques."""
    paths = set(app.openapi()["paths"])

    removed_prefix = "/v1/" + "ai"
    assert f"{removed_prefix}/generate" not in paths
    assert f"{removed_prefix}/chat" not in paths
    assert not any(
        path == removed_prefix or path.startswith(f"{removed_prefix}/") for path in paths
    )
    assert "/v1/chat/messages" in paths
    assert "/v1/guidance" in paths

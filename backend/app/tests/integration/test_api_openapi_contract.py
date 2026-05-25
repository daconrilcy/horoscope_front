"""Contrats OpenAPI verifies contre les facades historiques supprimees."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

PROTECTED_ROUTE_FAMILY_PREFIXES = {
    "admin": "/v1/admin",
    "ops": "/v1/ops",
    "b2b": "/v1/b2b",
    "internal": "/v1/internal",
}
EXPECTED_PUBLIC_ROUTE_PREFIXES = {
    "/v1/chat",
    "/v1/guidance",
    "/v1/users",
}
PROTECTED_ROUTE_SAMPLES = (
    "/v1/admin/dashboard/kpis-flux",
    "/v1/ops/monitoring/operational-summary",
    "/v1/b2b/usage/summary",
    "/v1/b2b/credentials",
)


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


def test_app_routes_map_public_and_protected_route_families() -> None:
    """L'inventaire runtime separe les familles publiques et protegees."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    public_openapi_paths = set(app.openapi()["paths"])

    assert EXPECTED_PUBLIC_ROUTE_PREFIXES <= {
        prefix
        for prefix in EXPECTED_PUBLIC_ROUTE_PREFIXES
        if any(path.startswith(prefix) for path in public_openapi_paths)
    }
    assert all(
        any(path.startswith(prefix) for path in route_paths)
        for family, prefix in PROTECTED_ROUTE_FAMILY_PREFIXES.items()
        if family != "internal"
    )
    assert not any(
        path.startswith(PROTECTED_ROUTE_FAMILY_PREFIXES["internal"]) for path in route_paths
    )


def test_protected_route_families_reject_unauthenticated_access() -> None:
    """Les familles internes exposees refusent les acces sans identifiants."""
    client = TestClient(app)

    for path in PROTECTED_ROUTE_SAMPLES:
        response = client.get(path)

        assert response.status_code in {401, 403}
        assert "error" in response.json()

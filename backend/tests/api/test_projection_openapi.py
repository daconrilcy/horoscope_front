# Tests OpenAPI du endpoint public generique de projections.
"""Verifie l'exposition publique unique et l'absence de surfaces internes."""

from __future__ import annotations

import json

from app.main import app


def test_projection_endpoint_is_registered_in_runtime_and_openapi() -> None:
    """La route canonique est chargee par le registre API v1."""
    route_paths = {getattr(route, "path", "") for route in app.routes}

    assert "/v1/astrology/projections" in route_paths
    assert "/v1/astrology/projections" in app.openapi()["paths"]


def test_projection_openapi_hides_internal_projection_contracts() -> None:
    """L'OpenAPI publique ne publie pas les contrats expert, admin ou provider."""
    projection_operation = app.openapi()["paths"]["/v1/astrology/projections"]["post"]
    serialized_openapi = json.dumps(projection_operation, sort_keys=True)

    assert "expert_technical_projection_v1" not in serialized_openapi
    assert "astrology_full_data_v1" not in serialized_openapi
    assert "admin_chart_diagnostics_v1" not in serialized_openapi
    assert "provider_response" not in serialized_openapi

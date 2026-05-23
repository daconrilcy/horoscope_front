# Tests d'architecture prouvant la neutralite API des graphes de calcul.
"""Verifie que le graphe de calcul reste hors contrat HTTP public."""

from fastapi.testclient import TestClient

from app.main import app


def test_calculation_graph_contracts_are_not_public_openapi_schemas() -> None:
    """Les contrats CS-225 ne sont pas exposes dans OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}

    assert "CalculationGraphDefinition" not in schemas
    assert "CalculationNodeDefinition" not in schemas
    assert "CalculationInputDefinition" not in schemas
    assert not any("calculation-graph" in path for path in route_paths)


def test_app_routes_remain_available_for_openapi_smoke() -> None:
    """Les routes applicatives restent inspectables par TestClient."""
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "/openapi.json" in route_paths
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()

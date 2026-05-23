# Tests d'architecture prouvant la neutralite API des graphes de calcul.
"""Verifie que le graphe de calcul reste hors contrat HTTP public."""

from fastapi.testclient import TestClient

from app.domain.astrology.natal_calculation import AspectResult
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


def test_aspect_runtime_contracts_are_not_public_openapi_schemas() -> None:
    """Les contrats aspect CS-229 restent internes et neutres pour l'API."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "AspectStructuralRuntimeData" not in schemas
    assert "AspectInterpretiveHintsRuntimeData" not in schemas
    assert not any("aspect-runtime" in path for path in route_paths)
    assert client.get("/openapi.json").status_code == 200


def test_aspect_public_result_schema_does_not_expose_legacy_interpretive_fields() -> None:
    """Les aliases plats restent hors contrat public, le serializer garde la projection."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    aspect_result_schema = schemas.get("AspectResult", {})
    properties = aspect_result_schema.get("properties", {})

    assert not {
        "default_valence",
        "interpretive_valence",
        "energy_type",
    } & set(properties)


def test_aspect_public_result_dump_does_not_expose_legacy_interpretive_fields() -> None:
    """Les sorties `AspectResult.model_dump()` ignorent les aliases plats legacy."""
    aspect = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.0,
        orb=1.0,
        orb_used=1.0,
        orb_max=6.0,
        family="major",
        is_major=True,
        is_minor=False,
    )

    assert not {
        "default_valence",
        "interpretive_valence",
        "energy_type",
    } & set(aspect.model_dump())

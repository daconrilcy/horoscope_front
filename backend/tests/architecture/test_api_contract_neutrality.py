# Tests d'architecture prouvant la neutralite API des graphes de calcul.
"""Verifie que les contrats runtime restent hors contrat HTTP public."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.astrology.natal_calculation import AspectResult
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
PRODUCT_PRIMITIVES_DOC = (
    REPO_ROOT / "docs/architecture/official-product-primitives-public-projections.md"
)
PROJECTION_VERSIONING_POLICY_DOC = (
    REPO_ROOT / "docs/architecture/projection-versioning-incompatibility-policy.md"
)
PRODUCT_PRIMITIVES_SNAPSHOT = (
    REPO_ROOT
    / "_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap"
    / "evidence/product-primitives.json"
)
REQUIRED_PRIMITIVE_IDS = {
    "structured_facts",
    "beginner_summary",
    "expert_technical_projection",
    "fixed_star_contacts",
    "astrologer_debug_data",
    "llm_input",
}
REQUIRED_AUDIENCES = {
    "beginner",
    "expert",
    "astrologer",
    "debug",
    "AI",
    "PDF",
    "public-user",
}
REQUIRED_ROADMAP_COLUMNS = {"API contract", "frontend client", "UI component"}
FORBIDDEN_PUBLIC_TERMS = {
    "chart_objects",
    "ChartObjectRuntimeData",
    "interpretation_input",
    "raw calculation graph payloads",
}
FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS = {
    "ChartObjectRuntimeData",
    "chart_objects",
    "CalculationGraph",
    "execution_trace",
    "replay_snapshot",
    "llm_input",
    "expert_technical_projection",
    "astrology_full_data",
    "admin_chart_diagnostics",
}
CANONICAL_TRANSIT_PROJECTION_ROUTE = "/v1/transit/projection"
FORBIDDEN_TRANSIT_PUBLIC_ROUTE_FRAGMENTS = {
    "/transit" + "/raw",
    "/transits" + "/raw",
    "/transit" + "_chart_v1",
    "/transit" + "-debug",
    "/fixed-stars" + "/transits",
}
PUBLIC_INTERNAL_OPENAPI_BOUNDARY_DOC = (
    REPO_ROOT / "backend/docs/openapi-public-internal-boundary.md"
)
REQUIRED_PROJECTION_VERSIONING_TERMS = {
    "projection_version",
    "mandatory",
    "required",
    "breaking",
    "v1",
    "v2",
    "silent",
    "unknown",
    "deprecated",
    "dépréciée",
    "blocking",
    "admin_log",
    "admin log",
    "source_versions",
    "incompatible",
    "recalculation",
    "recalcul",
    "authorized",
    "strong backward compatibility",
    "stable public API",
    "B2B",
}


def test_official_product_primitives_document_covers_required_projection_contract() -> None:
    """La roadmap officielle nomme les primitives, audiences et couches futures."""
    document = PRODUCT_PRIMITIVES_DOC.read_text(encoding="utf-8")

    assert REQUIRED_PRIMITIVE_IDS <= set(_mentions_in(document, REQUIRED_PRIMITIVE_IDS))
    assert REQUIRED_AUDIENCES <= set(_mentions_in(document, REQUIRED_AUDIENCES))
    assert REQUIRED_ROADMAP_COLUMNS <= set(_mentions_in(document, REQUIRED_ROADMAP_COLUMNS))
    assert "needs-user-decision" in document
    assert FORBIDDEN_PUBLIC_TERMS <= set(_mentions_in(document, FORBIDDEN_PUBLIC_TERMS))


def test_product_primitives_snapshot_has_one_canonical_entry_per_primitive() -> None:
    """Le snapshot machine-readable garde une seule entree canonique par primitive."""
    payload = json.loads(PRODUCT_PRIMITIVES_SNAPSHOT.read_text(encoding="utf-8"))
    primitives = payload["primitives"]

    primitive_ids = [primitive["primitive_id"] for primitive in primitives]
    assert set(primitive_ids) == REQUIRED_PRIMITIVE_IDS
    assert len(primitive_ids) == len(set(primitive_ids))
    assert payload["fixed_star_policy"] == "needs-user-decision"
    assert all(
        {"api_contract_story", "frontend_client_story", "ui_component_story"} <= primitive.keys()
        for primitive in primitives
    )


def test_projection_versioning_policy_covers_blocking_incompatibility_rules() -> None:
    """La politique CS-265 fixe les versions, incompatibilites et blocages."""
    document = PROJECTION_VERSIONING_POLICY_DOC.read_text(encoding="utf-8")

    assert REQUIRED_PROJECTION_VERSIONING_TERMS <= set(
        _mentions_in(document, REQUIRED_PROJECTION_VERSIONING_TERMS)
    )
    assert "fallback" in document
    assert "alias silencieux" in document


def test_projection_versioning_policy_does_not_create_runtime_projection_route() -> None:
    """La politique CS-265 ne cree aucun schema ni chemin versioning public."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    serialized_openapi = str(app.openapi())

    assert "/v1/astrology/projections/versioning" not in app.openapi().get("paths", {})
    assert "ProjectionVersioningPolicy" not in schemas
    assert "projection-versioning-incompatibility-policy" not in serialized_openapi


def test_calculation_graph_contracts_are_not_public_openapi_schemas() -> None:
    """Les contrats CS-225 ne sont pas exposes dans OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}

    assert "CalculationGraphDefinition" not in schemas
    assert "CalculationNodeDefinition" not in schemas
    assert "CalculationInputDefinition" not in schemas
    assert not any("calculation-graph" in path for path in route_paths)


def test_astrology_graph_family_registry_is_not_public_api_contract() -> None:
    """Le registre CS-246 reste interne au domaine runtime."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "AstrologyGraphFamilyMetadata" not in schemas
    assert "AstrologyGraphFamilyStatus" not in schemas
    assert not any("graph-family" in path or "graph_family" in path for path in route_paths)
    assert client.get("/openapi.json").status_code == 200


def test_calculation_graph_manifest_is_not_public_api_contract() -> None:
    """Le manifeste CS-247 reste interne au domaine runtime."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "CalculationGraphManifest" not in schemas
    assert "NodeIOSchema" not in schemas
    assert "GraphTypeDescriptor" not in schemas
    assert not any("graph-manifest" in path or "node-io-schema" in path for path in route_paths)
    assert client.get("/openapi.json").status_code == 200


def test_calculation_graph_execution_trace_is_not_public_api_contract() -> None:
    """La trace CS-248 reste interne au domaine runtime."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "CalculationGraphExecutionTrace" not in schemas
    assert "CalculationGraphNodeTrace" not in schemas
    assert not any("execution-trace" in path or "execution_trace" in path for path in route_paths)
    assert client.get("/openapi.json").status_code == 200


def test_chart_object_capability_taxonomy_is_not_public_api_contract() -> None:
    """La matrice CS-249 reste interne au domaine runtime."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "ChartObjectCapabilityTaxonomyEntry" not in schemas
    assert "ChartObjectDecisionStatus" not in schemas
    assert not any(
        "capability-taxonomy" in path or "capability_taxonomy" in path for path in route_paths
    )
    assert client.get("/openapi.json").status_code == 200


def test_astrology_doctrine_governance_is_not_public_api_contract() -> None:
    """Le modele CS-252 reste interne au domaine runtime."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "AstrologyDoctrineGovernanceEntry" not in schemas
    assert "RuleSourceOwnerStatus" not in schemas
    assert "DoctrineDecisionStatus" not in schemas
    assert not any(
        "doctrine-governance" in path or "doctrine_governance" in path for path in route_paths
    )
    assert client.get("/openapi.json").status_code == 200


def test_temporal_technique_selection_is_not_public_api_contract() -> None:
    """La selection CS-253 reste interne et hors contrat OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert "FirstTemporalTechniqueSelection" not in schemas
    assert "TemporalTechniqueSelectionStatus" not in schemas
    assert "temporal_technique_selection" not in serialized_openapi
    assert "transit_chart_v1" not in serialized_openapi
    assert not any("temporal" in path for path in route_paths)
    assert CANONICAL_TRANSIT_PROJECTION_ROUTE in route_paths
    assert not any(
        fragment in path
        for fragment in FORBIDDEN_TRANSIT_PUBLIC_ROUTE_FRAGMENTS
        for path in route_paths
    )
    assert client.get("/openapi.json").status_code == 200


def test_transit_chart_manifest_is_not_public_api_contract() -> None:
    """Le manifest CS-279 reste interne et hors contrat OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert "TransitChartManifest" not in schemas
    assert "TransitManifestClassification" not in schemas
    assert "transit_chart_manifest" not in serialized_openapi
    assert "transit_chart_v1" not in serialized_openapi
    assert not any("temporal" in path for path in route_paths)
    assert CANONICAL_TRANSIT_PROJECTION_ROUTE in route_paths
    assert not any(
        fragment in path
        for fragment in FORBIDDEN_TRANSIT_PUBLIC_ROUTE_FRAGMENTS
        for path in route_paths
    )
    assert client.get("/openapi.json").status_code == 200


def test_transit_chart_runtime_is_not_public_api_contract() -> None:
    """Le runtime CS-280 reste interne et hors contrat OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert "TransitChartRuntimePayload" not in schemas
    assert "TransitToNatalRelationshipRuntimeData" not in schemas
    assert "transit_chart_runtime" not in serialized_openapi
    assert "transit_chart_v1" not in serialized_openapi
    assert not any("temporal" in path for path in route_paths)
    assert CANONICAL_TRANSIT_PROJECTION_ROUTE in route_paths
    assert not any(
        fragment in path
        for fragment in FORBIDDEN_TRANSIT_PUBLIC_ROUTE_FRAGMENTS
        for path in route_paths
    )
    assert client.get("/openapi.json").status_code == 200


def test_ai_narrative_input_contract_is_not_public_api_contract() -> None:
    """Le contrat CS-254 reste interne et hors schemas OpenAPI."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    serialized_openapi = str(app.openapi())
    client = TestClient(app)

    assert "AINarrativeInputContract" not in schemas
    assert "AINarrativeStructuralFacts" not in schemas
    assert "ai_narrative_input" not in serialized_openapi
    assert not any("ai-narrative" in path or "ai_narrative" in path for path in route_paths)
    assert client.get("/openapi.json").status_code == 200


def test_app_routes_remain_available_for_openapi_smoke() -> None:
    """Les routes applicatives restent inspectables par TestClient."""
    route_paths = {route.path for route in app.routes}
    client = TestClient(app)

    assert "/openapi.json" in route_paths
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()


def test_product_primitive_runtime_terms_are_not_public_routes_or_schemas() -> None:
    """Les primitives CS-251 ne rouvrent aucune surface runtime brute."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    route_paths = {route.path for route in app.routes}
    serialized_openapi = str(app.openapi())

    assert all(term not in schemas for term in FORBIDDEN_PUBLIC_TERMS)
    assert all(term not in serialized_openapi for term in FORBIDDEN_PUBLIC_TERMS)
    assert not any("chart-objects" in path or "chart_objects" in path for path in route_paths)
    assert not any("interpretation-input" in path for path in route_paths)


def test_internal_projection_tokens_are_not_public_openapi_contract() -> None:
    """Les tokens de projection interne restent absents de l'OpenAPI publique."""
    public_openapi_payload = {
        path: contract
        for path, contract in app.openapi()["paths"].items()
        if not path.startswith(("/v1/admin", "/v1/ops", "/v1/b2b", "/v1/internal"))
    }
    serialized_openapi = json.dumps(public_openapi_payload, sort_keys=True)
    route_paths = {route.path for route in app.routes}

    assert all(
        token not in serialized_openapi for token in FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS
    )
    assert all(
        token not in path
        for path in route_paths
        if not path.startswith(("/v1/admin", "/v1/ops", "/v1/b2b", "/v1/internal"))
        for token in FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS
    )


def test_public_internal_openapi_boundary_is_documented() -> None:
    """La documentation backend explicite la frontiere OpenAPI publique/interne."""
    document = PUBLIC_INTERNAL_OPENAPI_BOUNDARY_DOC.read_text(encoding="utf-8")

    assert "/openapi.json" in document
    assert "app.openapi()" in document
    assert "admin/ops/b2b/internal" in document
    assert FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS <= set(
        _mentions_in(document, FORBIDDEN_PUBLIC_OPENAPI_PROJECTION_TOKENS)
    )


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


def _mentions_in(document: str, expected_terms: set[str]) -> tuple[str, ...]:
    """Retourne les termes attendus presents dans un document."""
    return tuple(term for term in expected_terms if term in document)

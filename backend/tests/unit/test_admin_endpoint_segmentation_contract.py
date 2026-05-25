# Commentaire global: ces tests verrouillent le contrat documentaire de segmentation
# des endpoints admin sans modifier les routes runtime.
"""Tests de contrat pour la segmentation des endpoints admin."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.rbac import VALID_ROLES
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = REPO_ROOT / "docs" / "architecture" / "admin-endpoint-domain-segmentation.md"

DOMAIN_FAMILIES = {"business", "technical", "astrology"}
FUTURE_ROLES = {"MARKETER", "TECHNO", "ASTRO_EXPERT"}
REQUIRED_FIELDS = {
    "domain_family",
    "route_family",
    "target_roles",
    "current_access_state",
    "logging_rule",
    "openapi_visibility",
    "client_exclusion",
    "source_dependency",
}
REQUIRED_ADMIN_PREFIXES = {
    "/v1/admin/dashboard",
    "/v1/admin/users",
    "/v1/admin/entitlements",
    "/v1/admin/exports",
    "/v1/admin/support",
    "/v1/admin/ai",
    "/v1/admin/logs",
    "/v1/admin/llm",
    "/v1/admin/content",
    "/v1/admin/pdf-templates",
    "/v1/admin/answer-audits",
    "/v1/admin/audit",
}
FORBIDDEN_PUBLIC_OPENAPI_TOKENS = {
    "ChartObjectRuntimeData",
    "CalculationGraph",
    "execution_trace",
    "replay_snapshot",
    "llm_input",
    "expert_technical_projection",
    "astrology_full_data",
}
CLIENT_EXCLUSION_TERMS = {"debug", "replay", "trace", "prompt", "full astrology runtime"}


def _document() -> str:
    """Charge le document canonique de segmentation des endpoints admin."""
    return DOC_PATH.read_text(encoding="utf-8")


def _admin_route_paths() -> set[str]:
    """Retourne les chemins admin declares par l'application FastAPI chargee."""
    return {route.path for route in app.routes if route.path.startswith("/v1/admin")}


def test_segmentation_document_exists_and_defines_required_fields() -> None:
    """Valide l'existence du document et la forme du contrat."""
    document = _document()

    assert document.startswith("<!-- Commentaire global:")
    for required_field in REQUIRED_FIELDS:
        assert required_field in document


def test_admin_domains_are_separated_and_mapped_to_cs271_roles() -> None:
    """Controle les familles business, technical, astrology et leurs roles cibles."""
    document = _document()
    normalized_runtime_roles = {role.lower() for role in VALID_ROLES}

    for family in DOMAIN_FAMILIES:
        assert f"`{family}`" in document

    for role in FUTURE_ROLES:
        assert role in document
        assert "non actif" in document or "non actifs" in document
        assert role.lower() not in normalized_runtime_roles

    assert "CS-271" in document


def test_sensitive_logging_and_client_exclusions_are_documented() -> None:
    """Verifie les champs de log sensibles et les exclusions client."""
    document = _document()

    for logging_field in ("actor", "route_family", "action", "correlation_id"):
        assert logging_field in document

    for exclusion_term in CLIENT_EXCLUSION_TERMS:
        assert exclusion_term in document

    assert "Aucun endpoint client" in document


def test_runtime_admin_routes_are_inventoried_without_route_surface_change() -> None:
    """Prouve l'inventaire runtime admin depuis app.routes et TestClient."""
    document = _document()
    route_paths = _admin_route_paths()
    client = TestClient(app)

    missing_prefixes = {
        prefix
        for prefix in REQUIRED_ADMIN_PREFIXES
        if not any(path.startswith(prefix) for path in route_paths)
    }
    assert not missing_prefixes
    for prefix in REQUIRED_ADMIN_PREFIXES:
        assert prefix in document
    assert client.get("/openapi.json").status_code == 200


def test_internal_openapi_rules_do_not_publish_internal_projection_tokens() -> None:
    """Controle la separation OpenAPI interne et client depuis app.openapi()."""
    document = _document()
    openapi = app.openapi()
    openapi_payload = str(openapi)

    assert "OpenAPI interne" in document
    assert "app.openapi()" in document
    assert "CS-266" in document
    for forbidden_token in FORBIDDEN_PUBLIC_OPENAPI_TOKENS:
        assert forbidden_token not in openapi_payload
    assert "/v1/admin/audit/admin_chart_diagnostics_v1" in openapi_payload
    public_paths = {
        path: schema for path, schema in openapi["paths"].items() if path.startswith("/v1/public")
    }
    assert "admin_chart_diagnostics_v1" not in str(public_paths)

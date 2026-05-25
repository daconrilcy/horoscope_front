# Commentaire global: ces tests verrouillent le contrat documentaire replay_snapshot_v1
# sans creer de surface runtime.
"""Tests de contrat du modele de stockage et de securite replay_snapshot_v1."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.sensitive_data import FIELD_CLASSIFICATION, DataCategory
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = REPO_ROOT / "docs" / "architecture" / "replay-snapshot-v1-storage-security-model.md"

REQUIRED_FIELDS = {
    "model_id",
    "snapshot_type",
    "classification",
    "minimal_stored_content",
    "forbidden_data",
    "masking_policy",
    "authorized_roles",
    "denied_roles",
    "retention_policy",
    "purge_policy",
    "diagnostics_link",
    "ai_audit_link",
    "approval_state",
}

MINIMAL_CONTENT_TERMS = {
    "calculation identity",
    "input reconstruction reference",
    "version identity",
    "provenance",
    "diagnostics link",
    "AI audit link",
}

FORBIDDEN_DATA_TERMS = {
    "raw birth data",
    "exact coordinates",
    "direct identifiers",
    "raw prompts",
    "raw model payloads",
    "secrets",
}

AUTHORIZED_ROLE_TERMS = {"ADMIN", "TECHNO", "ASTRO_EXPERT"}
DENIED_ROLE_TERMS = {"client B2C", "public", "MARKETER", "enterprise_admin", "support", "ops"}


def _document() -> str:
    """Charge le contrat canonique replay_snapshot_v1."""
    return DOC_PATH.read_text(encoding="utf-8")


def test_contract_document_exists_and_has_required_shape() -> None:
    """Valide l'existence du document et ses champs obligatoires."""
    document = _document()

    assert document.startswith("<!-- Commentaire global:")
    assert "replay_snapshot_v1_storage_security_model" in document
    assert "replay_snapshot_v1" in document
    assert "Protected internal replay support and debug data" in document
    assert "production replay execution est approuvee uniquement" in document

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in document)
    assert missing_fields == []


def test_minimal_content_and_sensitive_data_rules_are_explicit() -> None:
    """Prouve le contenu minimal et les donnees interdites ou masquees."""
    document = _document()

    missing_content_terms = sorted(term for term in MINIMAL_CONTENT_TERMS if term not in document)
    missing_forbidden_terms = sorted(term for term in FORBIDDEN_DATA_TERMS if term not in document)

    assert missing_content_terms == []
    assert missing_forbidden_terms == []
    assert "mask, truncate or replace with `birth_data_ref_hash`" in document
    assert "deny raw storage" in document

    for field in ("birth_date", "birth_time", "birth_place"):
        assert FIELD_CLASSIFICATION[field] is DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA


def test_roles_retention_and_purge_are_restricted() -> None:
    """Controle les roles autorises, la retention bloquee et la purge separee."""
    document = _document()

    for role in AUTHORIZED_ROLE_TERMS:
        assert f"`{role}`" in document
    for denied in DENIED_ROLE_TERMS:
        assert denied in document

    assert "`MARKETER` is not an authorized role" in document
    assert "DPO-REPLAY-SNAPSHOT-V1-RETENTION-001" in document
    assert "Approved implementation surfaces" in document
    assert "public/client routes or OpenAPI exposure" in document
    assert "frontend/src/**" in document
    assert "without a separate DPO/security decision" in document

    assert "expiry purge" in document
    assert "manual deletion" in document
    assert "tombstone metadata" in document
    assert "must not delete unrelated diagnostics or AI audit records by cascade" in document


def test_diagnostics_and_ai_audit_links_remain_separate() -> None:
    """Verifie que diagnostics et audit IA restent des owners distincts."""
    document = _document()
    normalized_document = " ".join(document.split())

    assert "admin_chart_diagnostics_v1" in document
    assert "Diagnostics remain current redacted support facts, not replay snapshots" in document
    assert "narrative_answer_audit_v1" in document
    assert "rejected-answer audit records" in document
    assert "must not merge, copy or replace narrative answer audit records" in normalized_document


def test_runtime_routes_openapi_and_public_client_surfaces_do_not_expose_replay() -> None:
    """Prouve que le runtime replay reste absent des surfaces publiques ou client."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    openapi_payload = str(app.openapi())
    public_openapi_payload = str(
        {
            path: contract
            for path, contract in app.openapi()["paths"].items()
            if not path.startswith(("/v1/admin", "/v1/ops", "/v1/b2b", "/v1/internal"))
        }
    )
    client = TestClient(app)

    replay_route_paths = {
        route_path for route_path in route_paths if "replay_snapshot_v1" in route_path
    }
    assert replay_route_paths == {
        "/v1/admin/audit/replay_snapshot_v1/{snapshot_id}",
        "/v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt",
    }
    assert "/v1/admin/audit/replay_snapshot_v1" in openapi_payload
    assert "replay_snapshot_v1" not in public_openapi_payload
    assert client.get("/openapi.json").status_code == 200

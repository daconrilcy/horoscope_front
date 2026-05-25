# Test de contrat pour la politique admin_chart_diagnostics_v1 sans surface runtime.
"""Verifie la politique documentaire des diagnostics admin sans exposition API."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.sensitive_data import FIELD_CLASSIFICATION, DataCategory
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = REPO_ROOT / "docs/architecture/admin-chart-diagnostics-v1-policy.md"


def _policy_text() -> str:
    """Charge la politique canonique pour des assertions de contrat."""
    return POLICY_PATH.read_text(encoding="utf-8")


def test_admin_chart_diagnostics_policy_exists_with_required_contract_fields() -> None:
    """Prouve l'identite et les categories obligatoires de la politique."""
    document = _policy_text()

    assert document.startswith("<!-- Politique canonique")
    required_terms = {
        "admin_chart_diagnostics_v1_policy",
        "admin_chart_diagnostics_v1",
        "retained_diagnostic_data",
        "calculation facts",
        "graph node status",
        "source versions",
        "proof references",
        "diagnostic timings",
        "retention_policy",
        "DPO-open",
        "blocked implementation surfaces",
    }

    missing_terms = sorted(term for term in required_terms if term not in document)
    assert missing_terms == []


def test_birth_data_and_identifiers_are_sensitive_and_redacted() -> None:
    """Verifie la reutilisation des categories sensibles existantes."""
    document = _policy_text()

    for field in ("birth_date", "birth_time", "birth_place"):
        assert FIELD_CLASSIFICATION[field] is DataCategory.DERIVED_SENSITIVE_DOMAIN_DATA

    required_sensitive_terms = {
        "birth date",
        "birth time",
        "birth place",
        "coordinates",
        "user id",
        "chart id",
        "mask",
        "truncate",
        "hash",
        "Raw birth data",
        "precise coordinates",
    }

    missing_terms = sorted(term for term in required_sensitive_terms if term not in document)
    assert missing_terms == []


def test_replay_boundary_prerequisites_and_audit_fields_are_explicit() -> None:
    """Controle la separation diagnostics, replay et audit de consultation."""
    document = _policy_text()

    required_terms = {
        "Current diagnostics are not replay snapshots",
        "separate from calculation replay",
        "separate from narrative answer audit",
        "storage owner",
        "input reconstruction",
        "version identity",
        "retention approval",
        "purge rules",
        "actor",
        "role",
        "action",
        "decision",
        "timestamp",
        "subject reference",
        "correlation id",
    }

    missing_terms = sorted(term for term in required_terms if term not in document)
    assert missing_terms == []


def test_client_public_openapi_and_runtime_surfaces_are_denied() -> None:
    """Prouve que la story ne cree aucune surface client ou OpenAPI publique."""
    document = _policy_text()
    public_openapi_payload = str(
        {
            path: contract
            for path, contract in app.openapi()["paths"].items()
            if not path.startswith(("/v1/admin", "/v1/ops", "/v1/b2b", "/v1/internal"))
        }
    )
    route_paths = {getattr(route, "path", "") for route in app.routes}
    client = TestClient(app)

    assert "clients, public OpenAPI, frontend files" in document
    assert "generated clients" in document
    assert "admin_chart_diagnostics" not in public_openapi_payload
    assert all(
        "admin_chart_diagnostics" not in route_path
        for route_path in route_paths
        if not route_path.startswith(("/v1/admin", "/v1/ops", "/v1/b2b", "/v1/internal"))
    )
    assert client.get("/openapi.json").status_code == 200

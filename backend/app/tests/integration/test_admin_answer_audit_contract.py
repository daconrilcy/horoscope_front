"""Tests du contrat documentaire admin_answer_audit_v1 et de sa non-exposition runtime."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = REPO_ROOT / "docs" / "architecture" / "admin-answer-audit-api.md"
ANSWER_AUDIT_LIST_PATH = "/v1/admin/answer-audits"
ANSWER_AUDIT_DETAIL_PATH = "/v1/admin/answer-audits/{answer_id}"


def _contract_text() -> str:
    """Charge le contrat canonique pour verifier les invariants documentaires."""
    return CONTRACT_PATH.read_text(encoding="utf-8")


def test_admin_answer_audit_contract_documents_required_shape() -> None:
    """Verifie la forme contractuelle attendue pour la future API admin protegee."""
    contract = _contract_text()

    required_terms = (
        "admin_answer_audit_v1",
        ANSWER_AUDIT_LIST_PATH,
        ANSWER_AUDIT_DETAIL_PATH,
        "require_admin_user",
        "Consultation",
        "Diagnostic review",
        "reponses rejetées",
        "answer_id",
        "evidence_refs",
        "provider",
        "model",
        "prompt_version",
        "status",
        "plan",
        "date range",
        "created_from",
        "created_to",
        "rejection_reason",
        "401",
        "403",
        "404",
        "503",
        "admin_chart_diagnostics_v1",
    )

    for term in required_terms:
        assert term in contract


def test_admin_answer_audit_contract_masks_raw_birth_data_by_default() -> None:
    """Verifie que le contrat interdit les donnees de naissance brutes par defaut."""
    contract = _contract_text()

    assert "birth_data" in contract
    assert "masque" in contract
    for forbidden_raw_field in (
        "birth_date",
        "birth_time",
        "birth_place",
        "birth_coordinates",
        "birth_lat",
        "birth_lon",
        "birth_timezone",
    ):
        assert forbidden_raw_field in contract
    assert "ne doit jamais retourner" in contract


def test_admin_answer_audit_routes_are_not_exposed_in_runtime_app() -> None:
    """Prouve que cette story documentaire ne cree pas encore de route runtime."""
    runtime_paths = {getattr(route, "path", "") for route in app.routes}
    openapi_paths = set(app.openapi()["paths"])

    assert ANSWER_AUDIT_LIST_PATH not in runtime_paths
    assert ANSWER_AUDIT_DETAIL_PATH not in runtime_paths
    assert ANSWER_AUDIT_LIST_PATH not in openapi_paths
    assert ANSWER_AUDIT_DETAIL_PATH not in openapi_paths


def test_admin_answer_audit_route_family_has_no_client_or_public_variant() -> None:
    """Bloque une exposition prematuree hors namespace admin."""
    forbidden_prefixes = (
        "/v1/answer-audits",
        "/v1/client/answer-audits",
        "/v1/public/answer-audits",
        "/v1/users/me/answer-audits",
        "/v1/admin/chart-diagnostics/answer-audits",
        "/v1/admin/answer-audit-replay",
    )
    runtime_paths = {getattr(route, "path", "") for route in app.routes}
    openapi_paths = set(app.openapi()["paths"])

    for prefix in forbidden_prefixes:
        assert not any(path.startswith(prefix) for path in runtime_paths)
        assert not any(path.startswith(prefix) for path in openapi_paths)


def test_unimplemented_admin_answer_audit_path_returns_not_found() -> None:
    """Confirme qu'aucun fallback silencieux ne repond sur le chemin contractuel."""
    client = TestClient(app)

    response = client.get(ANSWER_AUDIT_LIST_PATH)

    assert response.status_code == 404

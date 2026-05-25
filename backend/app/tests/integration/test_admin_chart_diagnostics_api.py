# Commentaire global: ces tests prouvent la route admin de diagnostic
# astrologique sans surface client.
"""Tests d'integration de `admin_chart_diagnostics_v1`."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.tests.helpers.db_session import (
    open_app_test_db_session,
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(tmp_path: Path) -> None:
    """Isole les lignes de theme et d'audit pour chaque test."""
    database_url = f"sqlite:///{(tmp_path / 'test-admin-chart-diagnostics.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    use_app_test_db_session_factory(test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        reset_app_test_db_session_factory()
        test_engine.dispose()


def _login(email: str, password: str) -> str:
    """Retourne un token d'acces applicatif pour les tests HTTP."""
    response = client.post("/v1/auth/login", json={"email": email, "password": password})
    return response.json()["data"]["tokens"]["access_token"]


def _create_user(email: str, role: str) -> str:
    """Cree un utilisateur de test et renvoie son token."""
    with open_app_test_db_session() as db:
        db.add(
            UserModel(
                email=email,
                password_hash=hash_password("admin123"),
                role=role,
                astrologer_profile="standard",
            )
        )
        db.commit()
    return _login(email, "admin123")


def _create_chart_result(chart_id: str = "chart-diag-1") -> str:
    """Insere une source de diagnostic minimale deja persistee."""
    with open_app_test_db_session() as db:
        db.add(
            ChartResultModel(
                chart_id=chart_id,
                reference_version="ref-v1",
                ruleset_version="rules-v1",
                input_hash="a" * 64,
                result_payload={"status": "persisted"},
            )
        )
        db.commit()
    return chart_id


def _auth_header(token: str, request_id: str = "rid-admin-chart-diag") -> dict[str, str]:
    """Construit les headers d'authentification et correlation."""
    return {"Authorization": f"Bearer {token}", "X-Request-Id": request_id}


def test_admin_chart_diagnostics_route_openapi_and_success_payload() -> None:
    """Verifie l'acces admin, le contrat JSON et l'exposition OpenAPI interne."""
    chart_id = _create_chart_result()
    admin_token = _create_user("admin-chart-diag@example.com", "admin")

    response = client.get(
        f"/v1/admin/audit/admin_chart_diagnostics_v1/{chart_id}",
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["projection_id"] == "admin_chart_diagnostics_v1"
    assert payload["chart_reference"] != chart_id
    assert payload["diagnostic_summary"]["status"] == "available"
    assert payload["diagnostic_summary"]["node_count"] > 0
    assert payload["calculation_graph"]["graph_family"] == "natal_chart_v1"
    assert payload["redaction"]["policy_id"] == "admin_chart_diagnostics_v1_policy"
    assert payload["limits"]["replay_included"] is False
    assert payload["limits"]["narrative_answer_audit_included"] is False
    assert payload["correlation_id"] == "rid-admin-chart-diag"
    assert "admin_chart_diagnostics_v1" in str(app.openapi())


def test_admin_chart_diagnostics_rejects_non_admin_user() -> None:
    """Controle que le role utilisateur est refuse et journalise."""
    chart_id = _create_chart_result("chart-diag-denied")
    user_token = _create_user("user-chart-diag@example.com", "user")

    response = client.get(
        f"/v1/admin/audit/admin_chart_diagnostics_v1/{chart_id}",
        headers=_auth_header(user_token),
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_chart_diagnostics_consulted",
                AuditEventModel.request_id == "rid-admin-chart-diag",
            )
        )
    assert event is not None
    assert event.status == "failed"
    assert event.target_type == "chart_diagnostics"
    assert event.target_id != chart_id
    assert event.details["decision"] == "denied"
    assert event.details["error_code"] == "insufficient_role"


def test_admin_chart_diagnostics_logs_consultation() -> None:
    """Prouve l'ecriture d'un journal d'audit sans payload diagnostic brut."""
    chart_id = _create_chart_result("chart-diag-audit")
    admin_token = _create_user("admin-chart-diag-audit@example.com", "admin")

    response = client.get(
        f"/v1/admin/audit/admin_chart_diagnostics_v1/{chart_id}",
        headers=_auth_header(admin_token, request_id="rid-admin-chart-audit"),
    )

    assert response.status_code == 200
    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_chart_diagnostics_consulted",
                AuditEventModel.request_id == "rid-admin-chart-audit",
            )
        )
    assert event is not None
    assert event.target_type == "chart_diagnostics"
    assert event.target_id != chart_id
    assert event.details["contract_id"] == "admin_chart_diagnostics_v1_policy"
    assert event.details["projection_id"] == "admin_chart_diagnostics_v1"
    assert event.details["route_family"] == "astrology"
    assert event.details["decision"] == "allowed"
    assert "result_payload" not in event.details


def test_admin_chart_diagnostics_missing_source_is_typed() -> None:
    """Retourne une erreur stable et journalisee sans reference brute."""
    admin_token = _create_user("admin-chart-diag-missing@example.com", "admin")

    response = client.get(
        "/v1/admin/audit/admin_chart_diagnostics_v1/missing-chart",
        headers=_auth_header(admin_token, request_id="rid-admin-chart-missing"),
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "admin_chart_diagnostics_source_missing"
    assert payload["error"]["details"]["chart_reference"] != "missing-chart"
    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_chart_diagnostics_consulted",
                AuditEventModel.request_id == "rid-admin-chart-missing",
            )
        )
    assert event is not None
    assert event.status == "failed"
    assert event.target_id != "missing-chart"
    assert event.details["decision"] == "failed"
    assert event.details["error_code"] == "source_missing"

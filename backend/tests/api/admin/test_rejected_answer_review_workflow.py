"""Tests API du workflow admin de revue des réponses narratives rejetées."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.main import app
from app.tests.helpers.db_session import (
    build_sqlite_test_engine,
    open_app_test_db_session,
    override_app_test_db_session,
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(tmp_path: Path) -> None:
    """Isole les tests de revue sur une base SQLite temporaire."""
    engine = build_sqlite_test_engine(f"sqlite:///{(tmp_path / 'review.db').as_posix()}")
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    use_app_test_db_session_factory(session_factory)
    app.dependency_overrides[get_db_session] = override_app_test_db_session
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        reset_app_test_db_session_factory()
        engine.dispose()


def _create_user(email: str, *, role: str) -> str:
    """Crée un utilisateur et retourne son token d'accès."""
    from app.core.security import hash_password

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

    response = client.post("/v1/auth/login", json={"email": email, "password": "admin123"})
    return str(response.json()["data"]["tokens"]["access_token"])


@pytest.fixture
def admin_token() -> str:
    """Retourne un token admin pour les endpoints protégés."""
    return _create_user("admin-review@example.com", role="admin")


@pytest.fixture
def user_token() -> str:
    """Retourne un token non admin pour vérifier le refus d'accès."""
    return _create_user("user-review@example.com", role="user")


def _seed_rejected_answer(
    answer_id: str = "answer-rejected-1",
    *,
    created_at: datetime | None = None,
) -> None:
    """Insère une réponse rejetée dans le store canonique `audit_events`."""
    with open_app_test_db_session() as db:
        db.add(
            AuditEventModel(
                request_id="req-rejected",
                actor_user_id=None,
                actor_role="system",
                action="narrative_answer_rejected",
                target_type="narrative_answer",
                target_id=answer_id,
                status="success",
                details={
                    "answer_id": answer_id,
                    "status": "rejected",
                    "rejection_reason": {"code": "evidence_hash_mismatch"},
                    "missing_evidence_refs": ["projection:moon", "structured_fact:sun"],
                    "prompt_version": "prompt-v7",
                    "projection_version": "client_interpretation_v1",
                    "provider": "openai",
                    "model": "gpt-5-mini",
                    "raw_rejected_answer": "internal diagnostic only",
                },
                created_at=created_at or datetime(2026, 5, 24, 9, 30, tzinfo=UTC),
            )
        )
        db.commit()


def _auth_header(token: str) -> dict[str, str]:
    """Construit l'en-tête bearer des tests d'intégration."""
    return {"Authorization": f"Bearer {token}", "X-Request-Id": "req-review-test"}


def test_admin_can_list_rejected_answers(admin_token: str) -> None:
    """Vérifie la liste admin protégée, son audit et les champs de contrat."""
    _seed_rejected_answer()

    response = client.get(
        "/v1/admin/answer-audits/rejected",
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    payload = response.json()
    item = payload["data"][0]
    assert payload["total"] == 1
    assert item["contract_id"] == "admin_answer_audit_v1"
    assert item["answer_id"] == "answer-rejected-1"
    assert item["status"] == "rejected"
    assert item["review_status"] == "pending_review"
    assert item["rejection_reason"] == {"code": "evidence_hash_mismatch"}
    assert item["missing_evidence_refs"] == ["projection:moon", "structured_fact:sun"]
    assert item["prompt_version"] == "prompt-v7"
    assert item["projection_version"] == "client_interpretation_v1"
    assert item["provider"] == "openai"
    assert item["model"] == "gpt-5-mini"

    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_rejected_answer_review_accessed",
                AuditEventModel.target_id.is_(None),
            )
        )
        assert event is not None
        assert event.details["consultation"] == "list"
        assert event.details["contract_id"] == "admin_answer_audit_v1"
        assert event.details["record_count"] == 1


def test_admin_detail_logs_consultation_and_shows_limits(admin_token: str) -> None:
    """Vérifie le détail, les limites manuelles et l'audit de consultation."""
    _seed_rejected_answer()

    response = client.get(
        "/v1/admin/answer-audits/rejected/answer-rejected-1",
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rejection_reason"]["code"] == "evidence_hash_mismatch"
    assert "diagnostic_only_no_client_delivery" in payload["manual_correction_limits"]
    assert payload["audit_event"]["action"] == "admin_rejected_answer_review_accessed"

    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_rejected_answer_review_accessed"
            )
        )
        assert event is not None
        assert event.target_type == "rejected_answer_review"
        assert event.target_id == "answer-rejected-1"
        assert event.details["contract_id"] == "admin_answer_audit_v1"
        assert "raw_rejected_answer" not in event.details


def test_admin_review_status_change_is_internal_and_logged(admin_token: str) -> None:
    """Vérifie le changement de statut interne et sa persistance audit."""
    _seed_rejected_answer()

    response = client.patch(
        "/v1/admin/answer-audits/rejected/answer-rejected-1/review",
        json={
            "review_status": "resolved_validation_followup",
            "review_note": "Evidence hash validator must be checked.",
        },
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 204

    detail = client.get(
        "/v1/admin/answer-audits/rejected/answer-rejected-1",
        headers=_auth_header(admin_token),
    )
    assert detail.json()["review_status"] == "resolved_validation_followup"
    assert detail.json()["reviewed_by"] is not None

    with open_app_test_db_session() as db:
        event = db.scalar(
            select(AuditEventModel).where(
                AuditEventModel.action == "admin_rejected_answer_reviewed"
            )
        )
        assert event is not None
        assert event.details["review_status"] == "resolved_validation_followup"


def test_review_status_filter_applies_before_pagination(admin_token: str) -> None:
    """Vérifie que le filtre de statut couvre toute la file avant pagination."""
    _seed_rejected_answer(
        "answer-pending-newer",
        created_at=datetime(2026, 5, 24, 11, 30, tzinfo=UTC),
    )
    _seed_rejected_answer(
        "answer-validation-older",
        created_at=datetime(2026, 5, 24, 10, 30, tzinfo=UTC),
    )
    client.patch(
        "/v1/admin/answer-audits/rejected/answer-validation-older/review",
        json={"review_status": "resolved_validation_followup"},
        headers=_auth_header(admin_token),
    )

    response = client.get(
        "/v1/admin/answer-audits/rejected",
        params={"review_status": "resolved_validation_followup", "per_page": 1},
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [item["answer_id"] for item in payload["data"]] == ["answer-validation-older"]


def test_invalid_review_status_returns_business_400(admin_token: str) -> None:
    """Vérifie l'erreur métier attendue pour un statut de revue inconnu."""
    _seed_rejected_answer()

    response = client.patch(
        "/v1/admin/answer-audits/rejected/answer-rejected-1/review",
        json={"review_status": "invalid_status"},
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 400


def test_workflow_is_admin_protected(admin_token: str, user_token: str) -> None:
    """Prouve que la surface reste protégée par authentification admin."""
    _seed_rejected_answer()

    missing_auth = client.get("/v1/admin/answer-audits/rejected")
    forbidden = client.get(
        "/v1/admin/answer-audits/rejected",
        headers=_auth_header(user_token),
    )
    allowed = client.get(
        "/v1/admin/answer-audits/rejected",
        headers=_auth_header(admin_token),
    )

    assert missing_auth.status_code == 401
    assert forbidden.status_code == 403
    assert allowed.status_code == 200


def test_runtime_routes_and_openapi_expose_only_admin_rejected_workflow() -> None:
    """Bloque les variantes publiques, support, replay ou client-facing."""
    runtime_paths = {getattr(route, "path", "") for route in app.routes}
    openapi_text = str(app.openapi())

    assert "/v1/admin/answer-audits/rejected" in runtime_paths
    assert "/v1/admin/answer-audits/rejected/{answer_id}" in runtime_paths
    assert "/v1/admin/answer-audits/rejected/{answer_id}/review" in runtime_paths

    forbidden_paths = (
        "/v1/answer-audits/rejected",
        "/v1/users/me/answer-audits/rejected",
        "/v1/admin/answer-audit-replay",
        "/v1/support/rejected-answers",
    )
    for path in forbidden_paths:
        assert path not in runtime_paths
        assert path not in openapi_text


def test_no_parallel_audit_store_or_public_symbol_is_present() -> None:
    """Garde locale contre les stores parallèles et symboles de livraison client."""
    openapi_text = str(app.openapi())

    assert "AnswerAuditAccessLogModel" not in openapi_text
    assert "admin_rejected_answer_public" not in openapi_text
    assert "RejectedAnswerReplay" not in openapi_text
    assert "auto_correct_rejected_prompt" not in openapi_text

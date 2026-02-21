from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
from app.infra.db.models.privacy import UserPrivacyRequestModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            UserPrivacyRequestModel,
            ChatMessageModel,
            ChatConversationModel,
            ChartResultModel,
            UserDailyQuotaUsageModel,
            PaymentAttemptModel,
            SubscriptionPlanChangeModel,
            UserSubscriptionModel,
            BillingPlanModel,
            UserBirthProfileModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _register_user(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_privacy_evidence_requires_support_or_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user("privacy-evidence-user-role@example.com", "user")
    response = client.get(
        "/v1/privacy/evidence/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_privacy_evidence_returns_export_delete_and_audit() -> None:
    _cleanup_tables()
    user_email = "privacy-evidence-user@example.com"
    user_token = _register_user(user_email, "user")
    support_token = _register_user("privacy-evidence-support@example.com", "support")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == user_email).limit(1))
        assert user is not None
        target_user_id = user.id

    export_response = client.post("/v1/privacy/export", headers=user_headers)
    assert export_response.status_code == 200

    delete_response = client.post(
        "/v1/privacy/delete",
        headers=user_headers,
        json={"confirmation": "DELETE"},
    )
    assert delete_response.status_code == 200

    evidence_response = client.get(
        f"/v1/privacy/evidence/{target_user_id}",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert evidence_response.status_code == 200
    data = evidence_response.json()["data"]
    assert data["schema_version"] == "1.0"
    assert data["user_id"] == target_user_id
    assert data["export_request"]["request_kind"] == "export"
    assert data["delete_request"]["request_kind"] == "delete"
    assert len(data["audit_events"]) >= 2
    actions = {item["action"] for item in data["audit_events"]}
    assert "privacy_export" in actions
    assert "privacy_delete" in actions


def test_privacy_evidence_is_reproducible_without_data_changes() -> None:
    _cleanup_tables()
    user_email = "privacy-evidence-repro-user@example.com"
    user_token = _register_user(user_email, "user")
    ops_token = _register_user("privacy-evidence-ops@example.com", "ops")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == user_email).limit(1))
        assert user is not None
        target_user_id = user.id

    assert client.post("/v1/privacy/export", headers=user_headers).status_code == 200
    assert (
        client.post("/v1/privacy/delete", headers=user_headers, json={"confirmation": "DELETE"})
    ).status_code == 200

    headers = {"Authorization": f"Bearer {ops_token}"}
    first = client.get(f"/v1/privacy/evidence/{target_user_id}", headers=headers)
    second = client.get(f"/v1/privacy/evidence/{target_user_id}", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"] == second.json()["data"]


def test_privacy_evidence_returns_422_when_artifacts_are_missing() -> None:
    _cleanup_tables()
    user_token = _register_user("privacy-evidence-missing-user@example.com", "user")
    support_token = _register_user("privacy-evidence-missing-support@example.com", "support")
    assert user_token

    with SessionLocal() as db:
        user = db.scalar(
            select(UserModel).where(UserModel.email == "privacy-evidence-missing-user@example.com")
        )
        assert user is not None
        target_user_id = user.id

    response = client.get(
        f"/v1/privacy/evidence/{target_user_id}",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "privacy_evidence_incomplete"
    missing = payload["details"]["missing_artifacts"]
    assert "export" in missing
    assert "delete" in missing
    assert "export_request_id" not in missing
    assert "delete_request_id" not in missing


def test_privacy_evidence_returns_422_when_latest_request_not_completed() -> None:
    _cleanup_tables()
    user_email = "privacy-evidence-not-completed-user@example.com"
    user_token = _register_user(user_email, "user")
    support_token = _register_user("privacy-evidence-not-completed-support@example.com", "support")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == user_email).limit(1))
        assert user is not None
        target_user_id = user.id

    assert client.post("/v1/privacy/export", headers=user_headers).status_code == 200
    assert (
        client.post("/v1/privacy/delete", headers=user_headers, json={"confirmation": "DELETE"})
    ).status_code == 200

    with SessionLocal() as db:
        latest_delete = db.scalar(
            select(UserPrivacyRequestModel)
            .where(
                UserPrivacyRequestModel.user_id == target_user_id,
                UserPrivacyRequestModel.request_kind == "delete",
            )
            .order_by(UserPrivacyRequestModel.id.desc())
            .limit(1)
        )
        assert latest_delete is not None
        latest_delete.status = "failed"
        db.commit()

    response = client.get(
        f"/v1/privacy/evidence/{target_user_id}",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "privacy_evidence_incomplete"
    assert "delete_completed" in payload["details"]["missing_artifacts"]


def test_privacy_evidence_returns_422_when_correlated_audit_missing() -> None:
    _cleanup_tables()
    user_email = "privacy-evidence-audit-missing-user@example.com"
    user_token = _register_user(user_email, "user")
    ops_token = _register_user("privacy-evidence-audit-missing-ops@example.com", "ops")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == user_email).limit(1))
        assert user is not None
        target_user_id = user.id

    assert client.post("/v1/privacy/export", headers=user_headers).status_code == 200
    assert (
        client.post("/v1/privacy/delete", headers=user_headers, json={"confirmation": "DELETE"})
    ).status_code == 200

    with SessionLocal() as db:
        db.execute(
            delete(AuditEventModel).where(
                AuditEventModel.target_type == "user",
                AuditEventModel.target_id == str(target_user_id),
                AuditEventModel.action == "privacy_delete",
            )
        )
        db.commit()

    response = client.get(
        f"/v1/privacy/evidence/{target_user_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "privacy_evidence_incomplete"
    assert "audit_delete" in payload["details"]["missing_artifacts"]

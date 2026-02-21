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
from app.services.audit_service import AuditEventCreatePayload, AuditService
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


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_audit_events_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/audit/events")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_audit_events_forbidden_for_user_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("audit-user@example.com", "user")
    response = client.get(
        "/v1/audit/events",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "audit_forbidden"


def test_audit_events_list_and_filter_for_support_role() -> None:
    _cleanup_tables()
    support_token = _register_user_with_role_and_token("audit-support@example.com", "support")
    target_token = _register_user_with_role_and_token("audit-target@example.com", "user")
    assert target_token

    with SessionLocal() as db:
        target_user = db.scalar(
            select(UserModel).where(UserModel.email == "audit-target@example.com").limit(1)
        )
        assert target_user is not None
        target_user_id = target_user.id
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-audit-1",
                actor_user_id=target_user_id,
                actor_role="user",
                action="privacy_export",
                target_type="user",
                target_id=str(target_user_id),
                status="success",
            ),
        )
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-audit-2",
                actor_user_id=target_user_id,
                actor_role="user",
                action="billing_plan_change",
                target_type="user",
                target_id=str(target_user_id),
                status="failed",
            ),
        )
        db.commit()

    response = client.get(
        "/v1/audit/events",
        headers={"Authorization": f"Bearer {support_token}"},
        params={
            "action": "privacy_export",
            "status": "success",
            "target_user_id": target_user_id,
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 1
    assert payload["events"][0]["action"] == "privacy_export"
    assert payload["events"][0]["status"] == "success"


def test_audit_events_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    support_token = _register_user_with_role_and_token("audit-support-429@example.com", "support")
    headers = {"Authorization": f"Bearer {support_token}", "X-Request-Id": "rid-audit-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "5"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.audit.check_rate_limit", _always_rate_limited)

    response = client.get("/v1/audit/events", headers=headers)
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-audit-429"

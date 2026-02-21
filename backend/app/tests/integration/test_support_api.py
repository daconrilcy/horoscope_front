from datetime import date

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
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.privacy_service import PrivacyService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            SupportIncidentModel,
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


def _register_user_with_role_and_token(email: str, role: str) -> tuple[int, str]:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.user.id, auth.tokens.access_token


def test_support_endpoints_require_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/support/incidents")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_support_endpoints_forbidden_for_user_role() -> None:
    _cleanup_tables()
    _, user_token = _register_user_with_role_and_token("support-role-user@example.com", "user")
    response = client.get(
        "/v1/support/incidents",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_support_context_includes_subscription_privacy_and_incidents() -> None:
    _cleanup_tables()
    customer_id, _ = _register_user_with_role_and_token("support-customer@example.com", "user")
    _, support_token = _register_user_with_role_and_token("support-agent@example.com", "support")

    with SessionLocal() as db:
        BillingService.ensure_default_plans(db)
        Basic = BillingService.get_subscription_status(db, user_id=customer_id)
        assert Basic.status == "inactive"
        db.add(
            UserBirthProfileModel(
                user_id=customer_id,
                birth_date=date(1990, 1, 1),
                birth_time="10:30:00",
                birth_place="Paris",
                birth_timezone="Europe/Paris",
            )
        )
        PrivacyService.request_export(db, user_id=customer_id, request_id="rid-support-context")
        db.commit()

    create_response = client.post(
        "/v1/support/incidents",
        headers={
            "Authorization": f"Bearer {support_token}",
            "X-Request-Id": "rid-support-context-1",
        },
        json={
            "user_id": customer_id,
            "category": "account",
            "title": "Ticket de test",
            "description": "Le client ne voit pas son historique.",
            "priority": "medium",
        },
    )
    assert create_response.status_code == 200

    context_response = client.get(
        f"/v1/support/users/{customer_id}/context",
        headers={
            "Authorization": f"Bearer {support_token}",
            "X-Request-Id": "rid-support-context-2",
        },
    )
    assert context_response.status_code == 200
    data = context_response.json()["data"]
    assert data["user"]["user_id"] == customer_id
    assert data["subscription"]["status"] in {"inactive", "active"}
    assert len(data["privacy_requests"]) >= 1
    assert data["privacy_requests"][0]["status"] == "completed"
    assert len(data["incidents"]) >= 1
    assert len(data["audit_events"]) >= 1
    assert context_response.json()["meta"]["request_id"] == "rid-support-context-2"


def test_support_incident_lifecycle_and_audit() -> None:
    _cleanup_tables()
    customer_id, _ = _register_user_with_role_and_token("support-customer-2@example.com", "user")
    support_id, support_token = _register_user_with_role_and_token(
        "support-agent-2@example.com",
        "support",
    )

    create_response = client.post(
        "/v1/support/incidents",
        headers={"Authorization": f"Bearer {support_token}", "X-Request-Id": "rid-support-inc-1"},
        json={
            "user_id": customer_id,
            "category": "content",
            "title": "Reponse incoherente",
            "description": "Le client signale une reponse incoherente.",
            "priority": "high",
            "assigned_to_user_id": support_id,
        },
    )
    assert create_response.status_code == 200
    incident_id = create_response.json()["data"]["incident_id"]

    update_response = client.patch(
        f"/v1/support/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {support_token}", "X-Request-Id": "rid-support-inc-2"},
        json={"status": "in_progress"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "in_progress"

    close_response = client.patch(
        f"/v1/support/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {support_token}", "X-Request-Id": "rid-support-inc-3"},
        json={"status": "closed"},
    )
    assert close_response.status_code == 200
    assert close_response.json()["data"]["status"] == "closed"

    list_response = client.get(
        "/v1/support/incidents",
        headers={"Authorization": f"Bearer {support_token}"},
        params={"user_id": customer_id},
    )
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 1

    detail_response = client.get(
        f"/v1/support/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["incident_id"] == incident_id

    with SessionLocal() as db:
        audit_events = db.scalars(
            select(AuditEventModel)
            .where(AuditEventModel.target_type == "incident")
            .order_by(AuditEventModel.id.asc())
        ).all()
        assert len(audit_events) >= 3
        assert audit_events[0].action == "support_incident_create"
        assert audit_events[-1].action in {"support_incident_update", "support_incident_close"}


def test_support_incident_rejects_invalid_transition() -> None:
    _cleanup_tables()
    customer_id, _ = _register_user_with_role_and_token("support-customer-3@example.com", "user")
    _, support_token = _register_user_with_role_and_token("support-agent-3@example.com", "support")

    create_response = client.post(
        "/v1/support/incidents",
        headers={"Authorization": f"Bearer {support_token}"},
        json={
            "user_id": customer_id,
            "category": "subscription",
            "title": "Question plan",
            "description": "Le client veut changer d abonnement.",
            "priority": "low",
        },
    )
    assert create_response.status_code == 200
    incident_id = create_response.json()["data"]["incident_id"]

    resolved_response = client.patch(
        f"/v1/support/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {support_token}"},
        json={"status": "resolved"},
    )
    assert resolved_response.status_code == 200

    invalid_response = client.patch(
        f"/v1/support/incidents/{incident_id}",
        headers={"Authorization": f"Bearer {support_token}"},
        json={"status": "in_progress"},
    )
    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "incident_invalid_transition"


def test_support_endpoints_return_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    customer_id, _ = _register_user_with_role_and_token("support-customer-429@example.com", "user")
    _, support_token = _register_user_with_role_and_token(
        "support-agent-429@example.com", "support"
    )

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.support.check_rate_limit", _always_rate_limited)

    response = client.get(
        f"/v1/support/users/{customer_id}/context",
        headers={"Authorization": f"Bearer {support_token}", "X-Request-Id": "rid-support-429"},
    )
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-support-429"

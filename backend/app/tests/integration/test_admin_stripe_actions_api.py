from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-stripe.db').as_posix()}"
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
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        test_engine.dispose()


@pytest.fixture
def admin_token():
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password

        admin = UserModel(
            email="admin-stripe@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/v1/auth/login", json={"email": "admin-stripe@example.com", "password": "admin123"}
    )
    return response.json()["data"]["tokens"]["access_token"]


def test_refresh_subscription_success(admin_token, monkeypatch):
    # Setup user with Stripe profile
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-refresh@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()
        profile = StripeBillingProfileModel(
            user_id=user.id,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            entitlement_plan="free",
            subscription_status="active",
        )
        db.add(profile)
        db.commit()
        user_id = user.id

    # Mock Stripe Client
    mock_stripe = MagicMock()
    mock_sub = MagicMock()

    # We need to simulate the structure that update_from_event_payload expects
    # It uses subscription.to_dict() and then looks into items.data[0].price.id
    mock_sub.to_dict.return_value = {
        "id": "sub_123",
        "status": "active",
        "customer": "cus_123",
        "items": {"data": [{"price": {"id": "price_premium_id"}}]},
        "object": "subscription",
    }
    mock_stripe.subscriptions.retrieve.return_value = mock_sub

    # Mock settings for price mapping
    monkeypatch.setattr(
        "app.services.billing.stripe_billing_profile_service.settings.stripe_price_premium",
        "price_premium_id",
    )
    # Rebuild map
    from app.services.billing import stripe_billing_profile_service

    monkeypatch.setattr(
        stripe_billing_profile_service,
        "STRIPE_PRICE_ENTITLEMENT_MAP",
        stripe_billing_profile_service._build_price_entitlement_map(),
    )

    # Critical: monkeypatch the router's imported name
    monkeypatch.setattr("app.api.v1.routers.admin.users.get_stripe_client", lambda: mock_stripe)

    response = client.post(
        f"/v1/admin/users/{user_id}/refresh-subscription",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    with db_session_module.SessionLocal() as db:
        profile = db.scalar(
            select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user_id)
        )
        assert profile.entitlement_plan == "premium"
        # Check audit
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "subscription_refresh_forced")
        )
        assert audit is not None


def test_assign_plan_success(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-assign@test.com", password_hash="x", role="user")
        db.add(user)
        db.commit()
        user_id = user.id

    response = client.post(
        f"/v1/admin/users/{user_id}/assign-plan",
        json={"plan_code": "premium", "reason": "Test manual assign"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    with db_session_module.SessionLocal() as db:
        profile = db.scalar(
            select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user_id)
        )
        assert profile.entitlement_plan == "premium"
        # Check audit
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "plan_manually_assigned")
        )
        assert audit.details["reason"] == "Test manual assign"


def test_assign_plan_rejects_short_reason(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-short-reason@test.com", password_hash="x", role="user")
        db.add(user)
        db.commit()
        user_id = user.id

    response = client.post(
        f"/v1/admin/users/{user_id}/assign-plan",
        json={"plan_code": "premium", "reason": "bad"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400
    assert "at least 5 characters" in response.json()["detail"]


def test_record_commercial_gesture_audits_before_after(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-gesture@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()
        plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2990,
            currency="EUR",
            daily_message_limit=10,
        )
        db.add(plan)
        db.flush()
        db.add(
            UserSubscriptionModel(
                user_id=user.id,
                plan_id=plan.id,
                status="active",
                failure_reason=None,
                started_at=datetime.now(UTC),
            )
        )
        db.commit()
        user_id = user.id

    response = client.post(
        f"/v1/admin/users/{user_id}/commercial-gesture",
        json={"gesture_type": "bonus_messages", "value": 25, "reason": "Support recovery"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    with db_session_module.SessionLocal() as db:
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "commercial_gesture_recorded")
        )
        assert audit is not None
        assert audit.details["gesture_type"] == "bonus_messages"
        assert audit.details["before"]["commercial_gestures_count"] == 0
        assert audit.details["after"]["commercial_gestures_count"] == 1

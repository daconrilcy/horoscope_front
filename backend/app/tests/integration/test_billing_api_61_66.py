import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal
from app.main import app
from app.tests.integration.test_billing_api import _cleanup_tables, _register_and_get_access_token
from app.services.quota_usage_service import QuotaUsageService
from app.services.entitlement_types import QuotaDefinition

client = TestClient(app)

def test_billing_subscription_current_quota() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        # Create a premium profile
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                subscription_status="active",
                entitlement_plan="premium",
            )
        )
        db.commit()
        
        # Simulate some usage
        # Premium astrologer_chat is 1000/month (messages)
        q_def = QuotaDefinition(
            quota_key="messages",
            quota_limit=1000,
            period_unit="month",
            period_value=1,
            reset_mode="calendar",
        )
        QuotaUsageService.consume(db, user_id=user.id, feature_code="astrologer_chat", quota=q_def, amount=42)
        db.commit()

    response = client.get("/v1/billing/subscription", headers=headers)
    assert response.status_code == 200
    payload = response.json()["data"]
    
    assert "current_quota" in payload
    quota = payload["current_quota"]
    assert quota is not None
    assert quota["feature_code"] == "astrologer_chat"
    assert quota["quota_limit"] == 1000
    assert quota["consumed"] == 42
    assert quota["remaining"] == 958
    assert quota["period_unit"] == "month"

def test_downgrade_non_regression_quota() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    future_date = datetime.now(timezone.utc) + timedelta(days=30)
    
    with SessionLocal() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        # Profile is premium BUT scheduled to downgrade to basic
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                subscription_status="active",
                entitlement_plan="premium",
                scheduled_plan_code="basic",
                scheduled_change_effective_at=future_date,
            )
        )
        db.commit()

    response = client.get("/v1/billing/subscription", headers=headers)
    assert response.status_code == 200
    payload = response.json()["data"]
    
    # Effective plan is still premium
    assert payload["plan"]["code"] == "premium"
    # Quota should still be premium (1000)
    assert payload["current_quota"]["quota_limit"] == 1000

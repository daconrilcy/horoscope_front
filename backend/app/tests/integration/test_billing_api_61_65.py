from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.tests.helpers.db_session import open_app_test_db_session
from app.tests.integration.billing_helpers import (
    cleanup_billing_tables,
    register_and_get_billing_access_token,
)

client = TestClient(app)


def test_billing_subscription_enriched_fields() -> None:
    cleanup_billing_tables()
    access_token = register_and_get_billing_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    future_date = datetime.now(timezone.utc) + timedelta(days=30)

    with open_app_test_db_session() as db:
        user = db.query(UserModel).filter_by(email="billing-api-user@example.com").one()
        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                subscription_status="active",
                entitlement_plan="premium",
                scheduled_plan_code="basic",
                scheduled_change_effective_at=future_date,
                cancel_at_period_end=True,
                current_period_end=future_date,
            )
        )
        db.commit()

    response = client.get("/v1/billing/subscription", headers=headers)
    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["status"] == "active"
    assert payload["plan"]["code"] == "premium"
    assert payload["scheduled_plan"]["code"] == "basic"
    # ISO string comparison
    assert payload["cancel_at_period_end"] is True
    assert "current_period_end" in payload
    assert "change_effective_at" in payload

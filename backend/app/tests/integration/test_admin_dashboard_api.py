from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.user import UserModel
from app.main import app
from app.tests.helpers.db_session import (
    open_app_test_db_session,
    reset_app_test_db_session_factory,
    use_app_test_db_session_factory,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-dashboard.db').as_posix()}"
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


@pytest.fixture
def admin_token():
    with open_app_test_db_session() as db:
        from app.core.security import hash_password

        admin = UserModel(
            email="admin-test@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/v1/auth/login", json={"email": "admin-test@example.com", "password": "admin123"}
    )
    return response.json()["data"]["tokens"]["access_token"]


def test_get_kpis_snapshot_success(admin_token):
    with open_app_test_db_session() as db:
        premium_plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=1999,
            daily_message_limit=100,
        )
        db.add(premium_plan)
        db.commit()

        user1 = UserModel(email="user1@test.com", password_hash="x", role="user")
        db.add(user1)
        db.commit()

        sub1 = UserSubscriptionModel(user_id=user1.id, plan_id=premium_plan.id, status="active")
        db.add(sub1)
        db.commit()

    response = client.get(
        "/v1/admin/dashboard/kpis-snapshot", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_users"] >= 2
    assert data["subscriptions_by_plan"]["premium"] >= 1


def test_get_kpis_flux_success(admin_token):
    with open_app_test_db_session() as db:
        # User from 60 days ago
        old_user = UserModel(
            email="old-user@test.com",
            password_hash="x",
            role="user",
            created_at=datetime.now(UTC) - timedelta(days=60),
        )
        db.add(old_user)
        db.commit()

    # Test 30d period
    response = client.get(
        "/v1/admin/dashboard/kpis-flux?period=30d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["period"] == "30d"
    # Only admin (created today) should be counted
    assert data["new_users"] == 1

    # Test 12m period
    response = client.get(
        "/v1/admin/dashboard/kpis-flux?period=12m",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # Admin + old_user
    assert data["new_users"] == 2
    assert len(data["trend_data"]) >= 1


def test_get_kpis_flux_free_plan_includes_users_without_stripe_profile(admin_token):
    with open_app_test_db_session() as db:
        free_user = UserModel(
            email="free-user@test.com",
            password_hash="x",
            role="user",
            created_at=datetime.now(UTC) - timedelta(days=2),
        )
        premium_user = UserModel(
            email="premium-user@test.com",
            password_hash="x",
            role="user",
            created_at=datetime.now(UTC) - timedelta(days=2),
        )
        premium_plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=1999,
            daily_message_limit=100,
        )
        db.add_all([free_user, premium_user, premium_plan])
        db.commit()

        from app.infra.db.models.stripe_billing import StripeBillingProfileModel

        db.add(
            StripeBillingProfileModel(
                user_id=premium_user.id,
                entitlement_plan="premium",
                subscription_status="active",
            )
        )
        db.commit()

    response = client.get(
        "/v1/admin/dashboard/kpis-flux?period=30d&plan=free",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["new_users"] >= 1
    assert any(point["new_users"] >= 1 for point in data["trend_data"])


def test_get_kpis_billing_success(admin_token):
    with open_app_test_db_session() as db:
        premium_plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=1999,
            daily_message_limit=100,
        )
        db.add(premium_plan)
        db.commit()

        user1 = UserModel(email="user-fail@test.com", password_hash="x", role="user")
        db.add(user1)
        db.commit()

        # Add a failure
        sub_fail = UserSubscriptionModel(
            user_id=user1.id,
            plan_id=premium_plan.id,
            status="past_due",
            failure_reason="card_declined",
            updated_at=datetime.now(UTC),
        )
        db.add(sub_fail)
        db.commit()

    response = client.get(
        "/v1/admin/dashboard/kpis-billing?period=30d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["payment_failures"] >= 1
    # revenue might be 0 if no 'active' stripe profiles are set up in this isolated DB
    assert "revenue_by_plan" in data


def test_search_users_payment_failure(admin_token):
    with open_app_test_db_session() as db:
        premium_plan = BillingPlanModel(
            code="premium",
            display_name="Premium",
            monthly_price_cents=1999,
            daily_message_limit=100,
        )
        db.add(premium_plan)
        db.commit()

        user_fail = UserModel(email="user-fail-search@test.com", password_hash="x", role="user")
        db.add(user_fail)
        db.commit()

        sub_fail = UserSubscriptionModel(
            user_id=user_fail.id,
            plan_id=premium_plan.id,
            status="past_due",
            failure_reason="card_declined",
            updated_at=datetime.now(UTC),
        )
        db.add(sub_fail)
        db.commit()

    response = client.get(
        "/v1/admin/users?q=payment_failure", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # Should find at least our user_fail
    emails = [u["email"] for u in data]
    assert "user-fail-search@test.com" in emails

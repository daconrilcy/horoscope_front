from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
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
    database_url = f"sqlite:///{(tmp_path / 'test-admin-logs.db').as_posix()}"
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
            email="admin-logs@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/v1/auth/login", json={"email": "admin-logs@example.com", "password": "admin123"}
    )
    return response.json()["data"]["tokens"]["access_token"]


def test_get_app_errors(admin_token):
    with open_app_test_db_session() as db:
        err = AuditEventModel(
            request_id="req_err",
            action="test_action",
            status="error",
            details={"msg": "something went wrong"},
            actor_role="user",
            target_type="system",
        )
        db.add(err)
        db.commit()

    response = client.get(
        "/v1/admin/logs/errors",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert response.json()["data"][0]["action"] == "test_action"


def test_get_stripe_events(admin_token):
    with open_app_test_db_session() as db:
        evt = StripeWebhookEventModel(
            stripe_event_id="evt_123", event_type="charge.succeeded", status="processed"
        )
        db.add(evt)
        db.commit()

    response = client.get(
        "/v1/admin/logs/stripe",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1


def test_get_quota_alerts(admin_token):
    with open_app_test_db_session() as db:
        user = UserModel(email="high-usage@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()

        plan = PlanCatalogModel(
            plan_code="premium",
            plan_name="Premium",
            audience=Audience.B2C,
        )
        feature = FeatureCatalogModel(
            feature_code="chat",
            feature_name="Chat astrologue",
            is_metered=True,
        )
        db.add_all([plan, feature])
        db.flush()

        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                entitlement_plan="premium",
                subscription_status="active",
            )
        )
        binding = PlanFeatureBindingModel(
            plan_id=plan.id,
            feature_id=feature.id,
            is_enabled=True,
            access_mode=AccessMode.QUOTA,
        )
        db.add(binding)
        db.flush()
        db.add(
            PlanFeatureQuotaModel(
                plan_feature_binding_id=binding.id,
                quota_key="daily",
                quota_limit=10,
                period_unit=PeriodUnit.DAY,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
            )
        )

        now = datetime.now(UTC)
        counter = FeatureUsageCounterModel(
            user_id=user.id,
            feature_code="chat",
            quota_key="daily",
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
            window_start=now,
            window_end=now + timedelta(days=1),
            used_count=10,
        )
        db.add(counter)
        db.commit()

    response = client.get(
        "/v1/admin/logs/quota-alerts",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    alert = response.json()["data"][0]
    assert alert["user_email_masked"].endswith("@test.com")
    assert alert["plan_code"] == "premium"
    assert alert["limit"] == 10


def test_get_audit_log_with_filters_and_masking(admin_token):
    with open_app_test_db_session() as db:
        admin = db.query(UserModel).filter(UserModel.email == "admin-logs@example.com").one()
        db.add_all(
            [
                AuditEventModel(
                    request_id="req_audit_1",
                    actor_user_id=admin.id,
                    actor_role="admin",
                    action="user_suspended",
                    target_type="user",
                    target_id="1234",
                    status="success",
                    details={"reason": "fraud"},
                ),
                AuditEventModel(
                    request_id="req_audit_2",
                    actor_user_id=admin.id,
                    actor_role="admin",
                    action="feature_flag_toggled",
                    target_type="system",
                    target_id="ff-paywall",
                    status="success",
                    details={"flag": "paywall_copy"},
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/audit?action=user_suspended&period=all",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert payload["data"][0]["action"] == "user_suspended"
    assert payload["data"][0]["actor_email_masked"] == "adm***@example.com"
    assert payload["data"][0]["target_id_masked"] == "***4"


def test_get_audit_log_rejects_invalid_period(admin_token):
    response = client.get(
        "/v1/admin/audit?period=xyz",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 422


def test_export_audit_log_generates_csv_and_audits_export(admin_token):
    with open_app_test_db_session() as db:
        admin = db.query(UserModel).filter(UserModel.email == "admin-logs@example.com").one()
        db.add(
            AuditEventModel(
                request_id="req_export_1",
                actor_user_id=admin.id,
                actor_role="admin",
                action="user_note_updated",
                target_type="user",
                target_id="56",
                status="success",
                details={"note": "VIP"},
            )
        )
        db.commit()

    response = client.post(
        "/v1/admin/audit/export",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "user_note_updated", "period": "all"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=audit_log_all_" in response.headers["content-disposition"]
    assert "user_note_updated" in response.text
    assert "**" in response.text

    with open_app_test_db_session() as db:
        export_event = (
            db.query(AuditEventModel)
            .filter(AuditEventModel.action == "audit_log_exported")
            .order_by(AuditEventModel.created_at.desc())
            .first()
        )

        assert export_event is not None
        assert export_event.details["filters"]["action"] == "user_note_updated"
        assert export_event.details["record_count"] == 1

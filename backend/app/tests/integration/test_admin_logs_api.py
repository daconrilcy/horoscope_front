from pathlib import Path
from datetime import UTC, datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel, PeriodUnit, ResetMode
from app.main import app

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
            email="admin-logs@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard"
        )
        db.add(admin)
        db.commit()
    
    response = client.post("/v1/auth/login", json={
        "email": "admin-logs@example.com",
        "password": "admin123"
    })
    return response.json()["data"]["tokens"]["access_token"]

def test_get_app_errors(admin_token):
    with db_session_module.SessionLocal() as db:
        err = AuditEventModel(
            request_id="req_err",
            action="test_action",
            status="error",
            details={"msg": "something went wrong"},
            actor_role="user",
            target_type="system"
        )
        db.add(err)
        db.commit()

    response = client.get("/v1/admin/logs/errors", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert response.json()["data"][0]["action"] == "test_action"

def test_get_stripe_events(admin_token):
    with db_session_module.SessionLocal() as db:
        evt = StripeWebhookEventModel(
            stripe_event_id="evt_123",
            event_type="charge.succeeded",
            status="processed"
        )
        db.add(evt)
        db.commit()

    response = client.get("/v1/admin/logs/stripe", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1

def test_get_quota_alerts(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="high-usage@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()
        
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
            used_count=10
        )
        db.add(counter)
        db.commit()

    response = client.get("/v1/admin/logs/quota-alerts", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert response.json()["data"][0]["user_email_masked"].endswith("@test.com")

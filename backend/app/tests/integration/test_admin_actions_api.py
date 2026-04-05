from pathlib import Path
from datetime import UTC, datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel, PeriodUnit, ResetMode
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-actions.db').as_posix()}"
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
            email="admin-actions@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard"
        )
        db.add(admin)
        db.commit()
    
    response = client.post("/v1/auth/login", json={
        "email": "admin-actions@example.com",
        "password": "admin123"
    })
    return response.json()["data"]["tokens"]["access_token"]

def test_suspend_unsuspend_user(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-to-suspend@test.com", password_hash="x", role="user")
        db.add(user)
        db.commit()
        user_id = user.id

    # Suspend
    response = client.post(f"/v1/admin/users/{user_id}/suspend", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    with db_session_module.SessionLocal() as db:
        user = db.get(UserModel, user_id)
        assert user.is_suspended is True
        # Check audit
        audit = db.scalar(select(AuditEventModel).where(AuditEventModel.action == "account_suspended"))
        assert audit is not None
        assert audit.target_id == str(user_id)

    # Unsuspend
    response = client.post(f"/v1/admin/users/{user_id}/unsuspend", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    with db_session_module.SessionLocal() as db:
        user = db.get(UserModel, user_id)
        assert user.is_suspended is False

def test_reset_quota(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-quota@test.com", password_hash="x", role="user")
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
        user_id = user.id

    response = client.post(
        f"/v1/admin/users/{user_id}/reset-quota", 
        json={"feature_code": "chat"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    with db_session_module.SessionLocal() as db:
        counter = db.scalar(select(FeatureUsageCounterModel).where(FeatureUsageCounterModel.user_id == user_id))
        assert counter.used_count == 0

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.main import app

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
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        test_engine.dispose()

@pytest.fixture
def admin_token():
    # Use register to ensure everything is set up correctly in the isolated DB
    # But wait, register doesn't support setting role="admin"
    # We need to create the user manually in the DB first
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password
        admin = UserModel(
            email="admin-test@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard"
        )
        db.add(admin)
        db.commit()
    
    # Login to get token
    response = client.post("/v1/auth/login", json={
        "email": "admin-test@example.com",
        "password": "admin123"
    })
    return response.json()["data"]["tokens"]["access_token"]

def test_get_kpis_snapshot_success(admin_token):
    with db_session_module.SessionLocal() as db:
        # Setup some data
        # Plans
        free_plan = BillingPlanModel(code="free", display_name="Free", monthly_price_cents=0, daily_message_limit=5)
        db.add(free_plan)
        
        premium_plan = BillingPlanModel(code="premium", display_name="Premium", monthly_price_cents=1999, daily_message_limit=100)
        db.add(premium_plan)
        db.commit()

        # Users
        user1 = UserModel(email="user1@test.com", password_hash="x", role="user")
        db.add(user1)
        db.commit()
        
        # Subscription
        sub1 = UserSubscriptionModel(user_id=user1.id, plan_id=premium_plan.id, status="active")
        db.add(sub1)
        db.commit()
        
        # Usage log
        usage1 = UserTokenUsageLogModel(
            user_id=user1.id,
            feature_code="chat",
            provider_model="gpt-4o",
            tokens_in=10,
            tokens_out=20,
            tokens_total=30,
            request_id="req1"
        )
        db.add(usage1)
        db.commit()

    response = client.get("/v1/admin/dashboard/kpis-snapshot", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_users"] >= 2 # admin + user1
    assert data["active_users_7j"] >= 1
    assert data["subscriptions_by_plan"]["premium"] >= 1
    assert data["mrr_cents"] >= 1999
    assert data["trials_count"] == 0

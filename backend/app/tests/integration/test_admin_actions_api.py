from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.chat_conversation import ChatConversationModel
from app.infra.db.models.chat_message import ChatMessageModel
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
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_natal_interpretation import (
    InterpretationLevel,
    UserNatalInterpretationModel,
)
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
    response = client.post(
        f"/v1/admin/users/{user_id}/suspend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    
    with db_session_module.SessionLocal() as db:
        user = db.get(UserModel, user_id)
        assert user.is_suspended is True
        # Check audit
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "account_suspended")
        )
        assert audit is not None
        assert audit.target_id == str(user_id)

    # Unsuspend
    response = client.post(
        f"/v1/admin/users/{user_id}/unsuspend",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
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
        counter = db.scalar(
            select(FeatureUsageCounterModel).where(FeatureUsageCounterModel.user_id == user_id)
        )
        assert counter.used_count == 0


def test_unlock_user(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(
            email="user-to-unlock@test.com",
            password_hash="x",
            role="user",
            is_locked=True,
        )
        db.add(user)
        db.commit()
        user_id = user.id

    response = client.post(
        f"/v1/admin/users/{user_id}/unlock",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    with db_session_module.SessionLocal() as db:
        user = db.get(UserModel, user_id)
        assert user.is_locked is False
        audit = db.scalar(
            select(AuditEventModel).where(AuditEventModel.action == "account_unlocked")
        )
        assert audit is not None
        assert audit.target_id == str(user_id)


def test_get_user_detail_includes_activity_summary(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-detail-metrics@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()

        conversation = ChatConversationModel(
            user_id=user.id,
            persona_id=UUID("00000000-0000-0000-0000-000000000001"),
        )
        db.add(conversation)
        db.flush()

        db.add_all(
            [
                ChatMessageModel(conversation_id=conversation.id, role="user", content="Bonjour"),
                ChatMessageModel(
                    conversation_id=conversation.id,
                    role="assistant",
                    content="Salut",
                ),
                UserTokenUsageLogModel(
                    user_id=user.id,
                    feature_code="chat",
                    provider_model="gpt-5-nano",
                    tokens_in=120,
                    tokens_out=80,
                    tokens_total=200,
                    request_id="req-1",
                ),
                UserTokenUsageLogModel(
                    user_id=user.id,
                    feature_code="natal_interpretation",
                    provider_model="gpt-5-nano",
                    tokens_in=300,
                    tokens_out=150,
                    tokens_total=450,
                    request_id="req-2",
                ),
                UserNatalInterpretationModel(
                    user_id=user.id,
                    chart_id="chart-short",
                    level=InterpretationLevel.SHORT,
                    use_case="natal_interpretation_short",
                    interpretation_payload={"sections": []},
                ),
                UserNatalInterpretationModel(
                    user_id=user.id,
                    chart_id="chart-complete",
                    level=InterpretationLevel.COMPLETE,
                    use_case="natal_interpretation",
                    interpretation_payload={"sections": []},
                ),
            ]
        )
        db.commit()
        user_id = user.id

    response = client.get(
        f"/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    activity_summary = response.json()["data"]["activity_summary"]
    assert activity_summary == {
        "total_tokens": 650,
        "tokens_in": 420,
        "tokens_out": 230,
        "messages_count": 2,
        "natal_charts_total": 2,
        "natal_charts_short": 1,
        "natal_charts_complete": 1,
    }


def test_get_user_detail_lists_daily_weekly_and_monthly_quotas(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-detail-quota@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()

        current_period_start = datetime.now(UTC) - timedelta(days=3)
        current_period_end = datetime.now(UTC) + timedelta(days=27)

        db.add(
            StripeBillingProfileModel(
                user_id=user.id,
                entitlement_plan="basic",
                subscription_status="active",
                current_period_start=current_period_start,
                current_period_end=current_period_end,
            )
        )

        plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
        feature = FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer Chat",
        )
        db.add_all([plan, feature])
        db.flush()

        binding = PlanFeatureBindingModel(
            plan_id=plan.id,
            feature_id=feature.id,
            access_mode=AccessMode.QUOTA,
            is_enabled=True,
        )
        db.add(binding)
        db.flush()

        db.add_all(
            [
                PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="daily_tokens",
                    quota_limit=150,
                    period_unit=PeriodUnit.DAY,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                ),
                PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="weekly_tokens",
                    quota_limit=700,
                    period_unit=PeriodUnit.WEEK,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                ),
                PlanFeatureQuotaModel(
                    plan_feature_binding_id=binding.id,
                    quota_key="tokens",
                    quota_limit=1_500,
                    period_unit=PeriodUnit.MONTH,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                ),
            ]
        )

        now = datetime.now(UTC)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        db.add_all(
            [
                FeatureUsageCounterModel(
                    user_id=user.id,
                    feature_code="astrologer_chat",
                    quota_key="daily_tokens",
                    period_unit=PeriodUnit.DAY,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                    window_start=day_start,
                    window_end=day_start + timedelta(days=1),
                    used_count=25,
                ),
                FeatureUsageCounterModel(
                    user_id=user.id,
                    feature_code="astrologer_chat",
                    quota_key="weekly_tokens",
                    period_unit=PeriodUnit.WEEK,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                    window_start=week_start,
                    window_end=week_start + timedelta(days=7),
                    used_count=210,
                ),
                FeatureUsageCounterModel(
                    user_id=user.id,
                    feature_code="astrologer_chat",
                    quota_key="tokens",
                    period_unit=PeriodUnit.MONTH,
                    period_value=1,
                    reset_mode=ResetMode.CALENDAR,
                    window_start=current_period_start,
                    window_end=current_period_end,
                    used_count=725,
                ),
            ]
        )
        db.commit()
        user_id = user.id

    response = client.get(
        f"/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    quotas = response.json()["data"]["quotas"]
    assert quotas == [
        {
            "feature_code": "astrologer_chat",
            "used": 25,
            "limit": 150,
            "period": "1 day",
        },
        {
            "feature_code": "astrologer_chat",
            "used": 210,
            "limit": 700,
            "period": "1 week",
        },
        {
            "feature_code": "astrologer_chat",
            "used": 725,
            "limit": 1500,
            "period": "1 month",
        },
    ]

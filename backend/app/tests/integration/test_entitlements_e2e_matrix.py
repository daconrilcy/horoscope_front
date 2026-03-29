from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    PeriodUnit,
    ResetMode,
    FeatureUsageCounterModel,
)
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.infra.db.session import get_db_session
from app.services.billing_service import BillingService, SubscriptionStatusData, BillingPlanData

client = TestClient(app)

def _override_auth(user_id=1, role="user"):
    def _override():
        return AuthenticatedUser(
            id=user_id,
            role=role,
            email=f"test_{user_id}@example.com",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    return _override

def _subscription(plan_code: str, status: str = "active") -> SubscriptionStatusData:
    plan = None
    if plan_code != "none":
        plan = BillingPlanData(
            code=plan_code,
            display_name=plan_code.title(),
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        )
    return SubscriptionStatusData(
        status=status,
        plan=plan,
        failure_reason=None,
        updated_at=datetime.now(timezone.utc),
    )

def _add_binding(
    db: Session,
    *,
    plan_id: int,
    feature_id: int,
    access_mode: AccessMode,
    is_enabled: bool = True,
    variant_code: str | None = None,
    quota_key: str | None = None,
    quota_limit: int | None = None,
    period_unit: PeriodUnit | None = None,
    period_value: int | None = None,
    reset_mode: ResetMode | None = None,
) -> None:
    binding = PlanFeatureBindingModel(
        plan_id=plan_id,
        feature_id=feature_id,
        access_mode=access_mode,
        is_enabled=is_enabled,
        variant_code=variant_code,
    )
    db.add(binding)
    db.flush()

    if access_mode != AccessMode.QUOTA or not is_enabled:
        return

    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key=quota_key,
            quota_limit=quota_limit,
            period_unit=period_unit,
            period_value=period_value,
            reset_mode=reset_mode,
        )
    )

def seed_canonical_matrix(db: Session) -> None:
    plans = {
        code: PlanCatalogModel(
            plan_code=code,
            plan_name=f"{code.title()} Plan",
            audience=Audience.B2C,
        )
        for code in ("free", "trial", "basic", "premium")
    }
    db.add_all(plans.values())
    db.flush()

    features = {
        "natal_chart_short": FeatureCatalogModel(
            feature_code="natal_chart_short",
            feature_name="Natal Chart Short",
            is_metered=False,
        ),
        "natal_chart_long": FeatureCatalogModel(
            feature_code="natal_chart_long",
            feature_name="Natal Chart Long",
            is_metered=True,
        ),
        "astrologer_chat": FeatureCatalogModel(
            feature_code="astrologer_chat",
            feature_name="Astrologer Chat",
            is_metered=True,
        ),
        "thematic_consultation": FeatureCatalogModel(
            feature_code="thematic_consultation",
            feature_name="Thematic Consultation",
            is_metered=True,
        ),
    }
    db.add_all(features.values())
    db.flush()

    # Plan: free
    f_id = plans["free"].id
    _add_binding(db, plan_id=f_id, feature_id=features["natal_chart_short"].id, access_mode=AccessMode.UNLIMITED)
    _add_binding(db, plan_id=f_id, feature_id=features["natal_chart_long"].id, access_mode=AccessMode.DISABLED, is_enabled=False)
    _add_binding(db, plan_id=f_id, feature_id=features["astrologer_chat"].id, access_mode=AccessMode.DISABLED, is_enabled=False)
    _add_binding(db, plan_id=f_id, feature_id=features["thematic_consultation"].id, access_mode=AccessMode.DISABLED, is_enabled=False)

    # Plan: trial
    t_id = plans["trial"].id
    _add_binding(db, plan_id=t_id, feature_id=features["natal_chart_short"].id, access_mode=AccessMode.UNLIMITED)
    _add_binding(db, plan_id=t_id, feature_id=features["natal_chart_long"].id, access_mode=AccessMode.QUOTA, 
                 variant_code="single_astrologer", quota_key="interpretations", quota_limit=1, 
                 period_unit=PeriodUnit.LIFETIME, period_value=1, reset_mode=ResetMode.LIFETIME)
    _add_binding(db, plan_id=t_id, feature_id=features["astrologer_chat"].id, access_mode=AccessMode.DISABLED, is_enabled=False)
    _add_binding(db, plan_id=t_id, feature_id=features["thematic_consultation"].id, access_mode=AccessMode.QUOTA, 
                 quota_key="consultations", quota_limit=1, period_unit=PeriodUnit.WEEK, period_value=1, reset_mode=ResetMode.CALENDAR)

    # Plan: basic
    b_id = plans["basic"].id
    _add_binding(db, plan_id=b_id, feature_id=features["natal_chart_short"].id, access_mode=AccessMode.UNLIMITED)
    _add_binding(db, plan_id=b_id, feature_id=features["natal_chart_long"].id, access_mode=AccessMode.QUOTA, 
                 variant_code="single_astrologer", quota_key="interpretations", quota_limit=1, 
                 period_unit=PeriodUnit.LIFETIME, period_value=1, reset_mode=ResetMode.LIFETIME)
    _add_binding(db, plan_id=b_id, feature_id=features["astrologer_chat"].id, access_mode=AccessMode.QUOTA, 
                 quota_key="messages", quota_limit=5, period_unit=PeriodUnit.DAY, period_value=1, reset_mode=ResetMode.CALENDAR)
    _add_binding(db, plan_id=b_id, feature_id=features["thematic_consultation"].id, access_mode=AccessMode.QUOTA, 
                 quota_key="consultations", quota_limit=1, period_unit=PeriodUnit.WEEK, period_value=1, reset_mode=ResetMode.CALENDAR)

    # Plan: premium
    p_id = plans["premium"].id
    _add_binding(db, plan_id=p_id, feature_id=features["natal_chart_short"].id, access_mode=AccessMode.UNLIMITED)
    _add_binding(db, plan_id=p_id, feature_id=features["natal_chart_long"].id, access_mode=AccessMode.QUOTA, 
                 variant_code="multi_astrologer", quota_key="interpretations", quota_limit=5, 
                 period_unit=PeriodUnit.LIFETIME, period_value=1, reset_mode=ResetMode.LIFETIME)
    _add_binding(db, plan_id=p_id, feature_id=features["astrologer_chat"].id, access_mode=AccessMode.QUOTA, 
                 quota_key="messages", quota_limit=2000, period_unit=PeriodUnit.MONTH, period_value=1, reset_mode=ResetMode.CALENDAR)
    _add_binding(db, plan_id=p_id, feature_id=features["thematic_consultation"].id, access_mode=AccessMode.QUOTA, 
                 quota_key="consultations", quota_limit=2, period_unit=PeriodUnit.DAY, period_value=1, reset_mode=ResetMode.CALENDAR)

    db.commit()

@pytest.fixture(scope="class")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    seed_canonical_matrix(db)
    yield db
    db.close()
    Base.metadata.drop_all(engine)

def _get_feature(response, feature_code: str) -> dict:
    data = response.json()["data"]
    return next(f for f in data["features"] if f["feature_code"] == feature_code)

def _client_get_entitlements(user_id: int, db: Session, plan_code: str, billing_status: str = "active"):
    app.dependency_overrides[require_authenticated_user] = _override_auth(user_id=user_id)
    app.dependency_overrides[get_db_session] = lambda: db
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(
            BillingService,
            "get_subscription_status_readonly",
            lambda *args, **kwargs: _subscription(plan_code, billing_status),
        )
        response = client.get("/v1/entitlements/me")
    app.dependency_overrides.clear()
    return response

class TestEntitlementsE2EMatrix:
    
    def _create_user(self, db: Session) -> UserModel:
        user = UserModel(email=f"user_{datetime.now().timestamp()}@example.com", password_hash="hash", role="user")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def test_no_subscription_scenario(self, db_session):
        """User sans subscription : plan_code='none', tous feature_not_in_plan."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "none", "none")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["plan_code"] == "none"
        for feature_code in ("natal_chart_short", "natal_chart_long", "astrologer_chat", "thematic_consultation"):
            f = _get_feature(response, feature_code)
            assert f["granted"] is False
            assert f["reason_code"] == "feature_not_in_plan"
            assert f["access_mode"] is None

    def test_free_plan_scenario(self, db_session):
        """User avec subscription au plan 'free'."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "free")
        
        # Short: Granted Unlimited
        f = _get_feature(response, "natal_chart_short")
        assert f["granted"] is True
        assert f["access_mode"] == "unlimited"
        
        # Others: Binding Disabled
        for fc in ("natal_chart_long", "astrologer_chat", "thematic_consultation"):
            f = _get_feature(response, fc)
            assert f["granted"] is False
            assert f["reason_code"] == "binding_disabled"

    def test_trial_plan_scenario(self, db_session):
        """User au plan 'trial' avec billing_status='trialing'."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "trial", "trialing")
        
        # Short: Unlimited
        f = _get_feature(response, "natal_chart_short")
        assert f["granted"] is True
        assert f["access_mode"] == "unlimited"
        
        # Long: Quota 1 Lifetime / single_astrologer
        f = _get_feature(response, "natal_chart_long")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["variant_code"] == "single_astrologer"
        assert f["usage_states"][0]["quota_limit"] == 1
        assert f["usage_states"][0]["reset_mode"] == "lifetime"
        
        # Chat: Disabled
        f = _get_feature(response, "astrologer_chat")
        assert f["granted"] is False
        assert f["reason_code"] == "binding_disabled"
        
        # Thematic: Quota 1/week
        f = _get_feature(response, "thematic_consultation")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["usage_states"][0]["quota_limit"] == 1
        assert f["usage_states"][0]["period_unit"] == "week"

    def test_basic_plan_scenario(self, db_session):
        """User au plan 'basic'."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "basic")
        
        # Chat: Quota 5/day
        f = _get_feature(response, "astrologer_chat")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["usage_states"][0]["quota_limit"] == 5
        assert f["usage_states"][0]["period_unit"] == "day"
        
        # Long: Quota 1 Lifetime / single_astrologer
        f = _get_feature(response, "natal_chart_long")
        assert f["granted"] is True
        assert f["usage_states"][0]["quota_limit"] == 1
        assert f["variant_code"] == "single_astrologer"

    def test_premium_plan_scenario(self, db_session):
        """User au plan 'premium'."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "premium")
        
        # Chat: Quota 2000/month
        f = _get_feature(response, "astrologer_chat")
        assert f["granted"] is True
        assert f["access_mode"] == "quota"
        assert f["usage_states"][0]["quota_limit"] == 2000
        assert f["usage_states"][0]["period_unit"] == "month"
        
        # Long: Quota 5 Lifetime / multi_astrologer
        f = _get_feature(response, "natal_chart_long")
        assert f["granted"] is True
        assert f["usage_states"][0]["quota_limit"] == 5
        assert f["variant_code"] == "multi_astrologer"
        
        # Thematic: Quota 2/day
        f = _get_feature(response, "thematic_consultation")
        assert f["granted"] is True
        assert f["usage_states"][0]["quota_limit"] == 2
        assert f["usage_states"][0]["period_unit"] == "day"

    def test_billing_inactive_scenario(self, db_session):
        """Si billing_status='past_due' et feature activée -> reason_code='billing_inactive'."""
        user = self._create_user(db_session)
        response = _client_get_entitlements(user.id, db_session, "premium", "past_due")
        
        # natal_chart_short est activée dans premium
        f = _get_feature(response, "natal_chart_short")
        assert f["granted"] is False
        assert f["reason_code"] == "billing_inactive"

    def test_frontend_invariants(self, db_session):
        """Vérifie les invariants d'AC3 pour tous les plans."""
        for plan in ("free", "trial", "basic", "premium"):
            user = self._create_user(db_session)
            response = _client_get_entitlements(user.id, db_session, plan)
            features = response.json()["data"]["features"]
            for f in features:
                if f["granted"] is False:
                    # AC3: granted == false -> reason_code présent et normalisé
                    assert f["reason_code"] in ("binding_disabled", "feature_not_in_plan", "billing_inactive", "quota_exhausted")
                else:
                    if f["access_mode"] == "quota":
                        # AC3: granted == true avec quota -> quota_remaining et quota_limit non-null
                        # Dans le payload API, c'est dans usage_states
                        for state in f["usage_states"]:
                            assert state["remaining"] is not None
                            assert state["quota_limit"] is not None
                    elif f["access_mode"] == "unlimited":
                        # AC3: granted == true unlimited -> pas de quota_limit dans usage_states
                        assert f["usage_states"] == []

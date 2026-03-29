import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.main import app
from app.infra.db.models.user import UserModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    Audience,
    PeriodUnit,
    ResetMode
)
from app.infra.db.models.billing import (
    BillingPlanModel,
    UserSubscriptionModel
)
from app.core.security import create_access_token
from app.services.billing_service import BillingService
from app.services.quota_window_resolver import QuotaWindowResolver


@pytest.fixture(autouse=True)
def clear_billing_cache():
    BillingService.reset_subscription_status_cache()
    yield
    BillingService.reset_subscription_status_cache()


def _auth_headers(user: UserModel) -> dict[str, str]:
    token = create_access_token(subject=str(user.id), role=user.role)
    return {"Authorization": f"Bearer {token}"}


def _create_user(db: Session, email: str = "test@example.com") -> UserModel:
    user = UserModel(email=email, role="user", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_or_create_feature(db: Session, feature_code: str) -> FeatureCatalogModel:
    feature = db.query(FeatureCatalogModel).filter(FeatureCatalogModel.feature_code == feature_code).first()
    if not feature:
        feature = FeatureCatalogModel(
            feature_code=feature_code,
            feature_name=f"Feature {feature_code}",
            is_active=True
        )
        db.add(feature)
        db.commit()
        db.refresh(feature)
    return feature


def _create_plan_and_catalog(db: Session, code: str) -> PlanCatalogModel:
    # 1. Billing Plan (legacy but required by BillingService)
    billing_plan = BillingPlanModel(
        code=code,
        display_name=f"Plan {code}",
        monthly_price_cents=1000,
        currency="EUR",
        daily_message_limit=10,
        is_active=True
    )
    db.add(billing_plan)
    
    # 2. Canonical Plan
    catalog_plan = PlanCatalogModel(
        plan_code=code,
        plan_name=f"Plan {code} Canonical",
        audience=Audience.B2C,
        is_active=True
    )
    db.add(catalog_plan)
    db.commit()
    db.refresh(catalog_plan)
    return catalog_plan


def _create_binding(
    db: Session, plan: PlanCatalogModel, feature_code: str, mode: AccessMode, quota_limit: int | None = None
) -> PlanFeatureBindingModel:
    feature = _get_or_create_feature(db, feature_code)
    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feature.id,
        access_mode=mode,
    )
    db.add(binding)
    db.commit()
    
    if mode == AccessMode.QUOTA and quota_limit is not None:
        from app.infra.db.models.product_entitlements import PlanFeatureQuotaModel
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key=f"quota:{feature_code}",
            quota_limit=quota_limit,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.CALENDAR
        )
        db.add(quota)
        db.commit()
        
    db.refresh(binding)
    return binding


def _create_usage(db: Session, user_id: int, feature_code: str, used: int) -> FeatureUsageCounterModel:
    # We need to match what QuotaUsageService expects
    window = QuotaWindowResolver.compute_window(
        PeriodUnit.DAY, 1, ResetMode.CALENDAR, datetime.now(timezone.utc)
    )
    counter = FeatureUsageCounterModel(
        user_id=user_id,
        feature_code=feature_code,
        quota_key=f"quota:{feature_code}",
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=used,
    )
    db.add(counter)
    db.commit()
    db.refresh(counter)
    return counter


def _create_subscription(db: Session, user_id: int, plan_code: str, status: str = "active"):
    billing_plan = db.query(BillingPlanModel).filter(BillingPlanModel.code == plan_code).first()
    sub = UserSubscriptionModel(
        user_id=user_id,
        plan_id=billing_plan.id,
        status=status,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@pytest.fixture
def client():
    return TestClient(app)


def test_entitlements_me_no_plan(client, db_session):
    """Cas sans plan actif : utilisateur sans abonnement."""
    from app.infra.db.session import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session
    
    # Ensure priority features exist
    for fc in ["astrologer_chat", "thematic_consultation", "natal_chart_long", "natal_chart_short"]:
        _get_or_create_feature(db_session, fc)

    user = _create_user(db_session)
    # Pas de subscription

    headers = _auth_headers(user)
    response = client.get("/v1/entitlements/me", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    # Should fail here if not implemented
    assert "plan_code" in data
    assert data["plan_code"] == "none"
    assert data["billing_status"] == "none"
    assert len(data["features"]) == 4

    for feature in data["features"]:
        assert "granted" in feature
        assert feature["granted"] is False
        assert feature["reason_code"] in ["feature_not_in_plan", "billing_inactive"]


def test_entitlements_me_quota_available(client, db_session):
    """Cas feature quota disponible : binding QUOTA + usage partiel."""
    from app.infra.db.session import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Ensure priority features exist
    for fc in ["astrologer_chat", "thematic_consultation", "natal_chart_long", "natal_chart_short"]:
        _get_or_create_feature(db_session, fc)

    user = _create_user(db_session, email="quota_avail@example.com")
    plan = _create_plan_and_catalog(db_session, code="basic_test")
    _create_binding(db_session, plan, "astrologer_chat", AccessMode.QUOTA, quota_limit=10)
    _create_usage(db_session, user.id, "astrologer_chat", used=2)
    _create_subscription(db_session, user.id, "basic_test")

    headers = _auth_headers(user)
    response = client.get("/v1/entitlements/me", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["plan_code"] == "basic_test"
    assert data["billing_status"] == "active"

    chat = next(f for f in data["features"] if f["feature_code"] == "astrologer_chat")
    assert chat["granted"] is True
    assert chat["reason_code"] == "granted"
    assert chat["quota_remaining"] == 8
    assert chat["quota_limit"] == 10
    assert chat["access_mode"] == "quota"


def test_entitlements_me_quota_exhausted(client, db_session):
    """Cas feature quota épuisé : usage = limite."""
    from app.infra.db.session import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Ensure priority features exist
    for fc in ["astrologer_chat", "thematic_consultation", "natal_chart_long", "natal_chart_short"]:
        _get_or_create_feature(db_session, fc)

    user = _create_user(db_session, email="quota_exhaust@example.com")
    plan = _create_plan_and_catalog(db_session, code="basic_test_2")
    _create_binding(db_session, plan, "astrologer_chat", AccessMode.QUOTA, quota_limit=10)
    _create_usage(db_session, user.id, "astrologer_chat", used=10)
    _create_subscription(db_session, user.id, "basic_test_2")

    headers = _auth_headers(user)
    response = client.get("/v1/entitlements/me", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    chat = next(f for f in data["features"] if f["feature_code"] == "astrologer_chat")
    assert chat["granted"] is False
    assert chat["reason_code"] == "quota_exhausted"
    assert chat["quota_remaining"] == 0


def test_entitlements_me_unlimited(client, db_session):
    """Cas feature unlimited : binding UNLIMITED."""
    from app.infra.db.session import get_db_session
    app.dependency_overrides[get_db_session] = lambda: db_session

    # Ensure priority features exist
    for fc in ["astrologer_chat", "thematic_consultation", "natal_chart_long", "natal_chart_short"]:
        _get_or_create_feature(db_session, fc)

    user = _create_user(db_session, email="unlimited@example.com")
    plan = _create_plan_and_catalog(db_session, code="premium_test")
    _create_binding(db_session, plan, "natal_chart_long", AccessMode.UNLIMITED)
    _create_subscription(db_session, user.id, "premium_test")

    headers = _auth_headers(user)
    response = client.get("/v1/entitlements/me", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    natal = next(f for f in data["features"] if f["feature_code"] == "natal_chart_long")
    assert natal["granted"] is True
    assert natal["reason_code"] == "granted"
    assert natal["quota_remaining"] is None
    assert natal["quota_limit"] is None
    assert natal["access_mode"] == "unlimited"

import pytest
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import engine
from app.services.billing.service import BillingService
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.horoscope_daily_entitlement_gate import HoroscopeDailyEntitlementGate


@pytest.fixture
def seeded_catalog(db_session: Session):
    # Clear DB to avoid pollution from seed() in other tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    BillingService.reset_subscription_status_cache()

    # 1. Feature
    feature = FeatureCatalogModel(
        feature_code="horoscope_daily",
        feature_name="Horoscope Quotidien",
        is_metered=False,
    )
    db_session.add(feature)

    # 2. Plans (Billing + Catalog)
    plans_data = [
        ("free", "Plan Gratuit", "summary_only"),
        ("basic", "Plan Basic", "full"),
        ("premium", "Plan Premium", "full"),
    ]

    for code, name, variant in plans_data:
        # Billing Plan (required for BillingService fallback in tests)
        bp = BillingPlanModel(
            code=code,
            display_name=name,
            monthly_price_cents=0 if code == "free" else 900,
            currency="EUR",
            daily_message_limit=10,
            is_active=True,
        )
        db_session.add(bp)
        db_session.flush()

        # Catalog Plan
        cp = PlanCatalogModel(
            plan_code=code,
            plan_name=name,
            audience=Audience.B2C,
            is_active=True,
        )
        db_session.add(cp)
        db_session.flush()

        # Binding
        binding = PlanFeatureBindingModel(
            plan_id=cp.id,
            feature_id=feature.id,
            is_enabled=True,
            access_mode=AccessMode.UNLIMITED,
            variant_code=variant,
        )
        db_session.add(binding)

    db_session.commit()
    return True


def test_resolve_horoscope_daily_variant_by_plan(db_session: Session, seeded_catalog):
    from app.services.entitlement.feature_scope_registry import FEATURE_SCOPE_REGISTRY

    print(f"DEBUG: FEATURE_SCOPE_REGISTRY = {list(FEATURE_SCOPE_REGISTRY.keys())}")

    # Users for each plan
    user_free = UserModel(email="free@example.com", password_hash="...", role="user")
    user_basic = UserModel(email="basic@example.com", password_hash="...", role="user")
    user_premium = UserModel(email="premium@example.com", password_hash="...", role="user")

    db_session.add_all([user_free, user_basic, user_premium])
    db_session.flush()

    # Subscriptions (Legacy fallback for tests)
    plans = {p.code: p.id for p in db_session.query(BillingPlanModel).all()}

    sub_free = UserSubscriptionModel(user_id=user_free.id, plan_id=plans["free"], status="active")
    sub_basic = UserSubscriptionModel(
        user_id=user_basic.id, plan_id=plans["basic"], status="active"
    )
    sub_premium = UserSubscriptionModel(
        user_id=user_premium.id, plan_id=plans["premium"], status="active"
    )

    db_session.add_all([sub_free, sub_basic, sub_premium])
    db_session.commit()

    # Resolve and Check

    # 1. Free -> summary_only
    snapshot_free = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
        db_session, app_user_id=user_free.id
    )
    assert "horoscope_daily" in snapshot_free.entitlements
    assert snapshot_free.entitlements["horoscope_daily"].granted is True
    assert snapshot_free.entitlements["horoscope_daily"].variant_code == "summary_only"

    gate_res_free = HoroscopeDailyEntitlementGate.check_and_get_variant(
        db_session, user_id=user_free.id
    )
    assert gate_res_free.variant_code == "summary_only"

    # 2. Basic -> full
    snapshot_basic = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
        db_session, app_user_id=user_basic.id
    )
    assert snapshot_basic.entitlements["horoscope_daily"].variant_code == "full"

    gate_res_basic = HoroscopeDailyEntitlementGate.check_and_get_variant(
        db_session, user_id=user_basic.id
    )
    assert gate_res_basic.variant_code == "full"

    # 3. Premium -> full
    snapshot_premium = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
        db_session, app_user_id=user_premium.id
    )
    assert snapshot_premium.entitlements["horoscope_daily"].variant_code == "full"

    gate_res_premium = HoroscopeDailyEntitlementGate.check_and_get_variant(
        db_session, user_id=user_premium.id
    )
    assert gate_res_premium.variant_code == "full"

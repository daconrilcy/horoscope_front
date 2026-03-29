from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import EnterpriseAccountBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.models.user import UserModel
from app.services.billing_service import BillingPlanData, SubscriptionStatusData
from app.services.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_resolve_b2c_user_snapshot_no_plan(db):
    # Setup: User exists but has no plan
    user = UserModel(id=1, email="test@example.com", password_hash="hash", role="user")
    db.add(user)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="none",
        plan=None,
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.effective_entitlement_resolver_service.BillingService.get_subscription_status_readonly",
        return_value=mock_sub,
    ):
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=1)

        assert snapshot.subject_type == "b2c_user"
        assert snapshot.subject_id == 1
        assert snapshot.plan_code == "none"
        assert snapshot.billing_status == "none"
        # Toutes les features B2C doivent être présentes avec reason_code="feature_not_in_plan"
        assert "astrologer_chat" in snapshot.entitlements
        assert (
            snapshot.entitlements["astrologer_chat"].reason_code
            == EffectiveEntitlementResolverService.REASON_FEATURE_NOT_IN_PLAN
        )


def test_resolve_b2c_user_snapshot_user_not_found(db):
    # No user added to db
    snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=999)

    assert snapshot.subject_type == "b2c_user"
    assert snapshot.subject_id == 999
    assert snapshot.plan_code == "none"
    assert snapshot.billing_status == "none"
    assert (
        snapshot.entitlements["astrologer_chat"].reason_code
        == EffectiveEntitlementResolverService.REASON_SUBJECT_NOT_ELIGIBLE
    )


def test_resolve_b2c_user_snapshot_granted_quota(db):
    # Setup data
    user = UserModel(id=1, email="test@example.com", password_hash="hash", role="user")
    db.add(user)
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        variant_code="gold",
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="chats",
        quota_limit=10,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db.add(quota)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2000,
            currency="EUR",
            daily_message_limit=1000,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.effective_entitlement_resolver_service.BillingService.get_subscription_status_readonly",
        return_value=mock_sub,
    ):
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=1)

        assert snapshot.plan_code == "premium"
        assert snapshot.billing_status == "active"
        access = snapshot.entitlements["astrologer_chat"]
        assert access.granted is True
        assert access.reason_code == EffectiveEntitlementResolverService.REASON_GRANTED
        assert access.access_mode == "quota"
        assert access.quota_limit == 10
        assert access.quota_used == 0
        assert access.quota_remaining == 10


def test_resolve_b2b_account_snapshot_active(db):
    # Setup B2B data
    account = EnterpriseAccountModel(id=10, company_name="ACME", status="active")
    db.add(account)
    db.commit()

    plan = PlanCatalogModel(
        plan_code="enterprise_gold",
        plan_name="Enterprise Gold",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=100,
    )
    db.add(plan)
    db.commit()

    mapping = EnterpriseAccountBillingPlanModel(enterprise_account_id=10, plan_id=100)
    db.add(mapping)
    db.commit()

    feat = FeatureCatalogModel(feature_code="b2b_api_access", feature_name="API Access")
    db.add(feat)
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.UNLIMITED,
        is_enabled=True,
    )
    db.add(binding)
    db.commit()

    snapshot = EffectiveEntitlementResolverService.resolve_b2b_account_snapshot(
        db, enterprise_account_id=10
    )

    assert snapshot.subject_type == "b2b_account"
    assert snapshot.subject_id == 10
    assert snapshot.plan_code == "enterprise_gold"
    assert snapshot.billing_status == "active"
    access = snapshot.entitlements["b2b_api_access"]
    assert access.granted is True
    assert access.reason_code == EffectiveEntitlementResolverService.REASON_GRANTED
    assert access.access_mode == "unlimited"


def test_resolve_b2c_user_snapshot_billing_inactive(db):
    user = UserModel(id=1, email="test@example.com", password_hash="hash", role="user")
    db.add(user)
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.UNLIMITED,
        is_enabled=True,
    )
    db.add(binding)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="past_due",
        plan=BillingPlanData(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2000,
            currency="EUR",
            daily_message_limit=1000,
            is_active=True,
        ),
        failure_reason="card_declined",
        updated_at=None,
    )

    with patch(
        "app.services.effective_entitlement_resolver_service.BillingService.get_subscription_status_readonly",
        return_value=mock_sub,
    ):
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=1)

        assert snapshot.billing_status == "past_due"
        access = snapshot.entitlements["astrologer_chat"]
        assert access.granted is False
        assert access.reason_code == EffectiveEntitlementResolverService.REASON_BILLING_INACTIVE


def test_resolve_b2c_user_snapshot_quota_exhausted(db):
    user = UserModel(id=1, email="test@example.com", password_hash="hash", role="user")
    db.add(user)
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="chats",
        quota_limit=5,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db.add(quota)
    db.commit()

    # Add usage to exhaust quota
    from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
    from app.services.quota_window_resolver import QuotaWindowResolver

    now = datetime.now(timezone.utc)
    window = QuotaWindowResolver.compute_window("day", 1, "calendar", now)

    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="astrologer_chat",
        quota_key="chats",
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=5,
    )
    db.add(counter)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2000,
            currency="EUR",
            daily_message_limit=1000,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.effective_entitlement_resolver_service.BillingService.get_subscription_status_readonly",
        return_value=mock_sub,
    ):
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=1)

        access = snapshot.entitlements["astrologer_chat"]
        assert access.granted is False
        assert access.reason_code == EffectiveEntitlementResolverService.REASON_QUOTA_EXHAUSTED
        assert access.quota_remaining == 0


def test_resolve_b2c_user_snapshot_disabled(db):
    user = UserModel(id=1, email="test@example.com", password_hash="hash", role="user")
    db.add(user)
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.DISABLED,
        is_enabled=True,
    )
    db.add(binding)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="premium",
            display_name="Premium",
            monthly_price_cents=2000,
            currency="EUR",
            daily_message_limit=1000,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.effective_entitlement_resolver_service.BillingService.get_subscription_status_readonly",
        return_value=mock_sub,
    ):
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=1)

        access = snapshot.entitlements["astrologer_chat"]
        assert access.granted is False
        assert access.reason_code == EffectiveEntitlementResolverService.REASON_BINDING_DISABLED


def test_resolve_b2b_account_snapshot_quota_available(db):
    # Setup B2B data
    account = EnterpriseAccountModel(id=20, company_name="ACME-B2B", status="active")
    db.add(account)
    db.commit()

    plan = PlanCatalogModel(
        plan_code="b2b_silver",
        plan_name="B2B Silver",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=200,
    )
    db.add(plan)
    db.commit()

    mapping = EnterpriseAccountBillingPlanModel(enterprise_account_id=20, plan_id=200)
    db.add(mapping)
    db.commit()

    feat = FeatureCatalogModel(feature_code="b2b_api_access", feature_name="API Access")
    db.add(feat)
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="api_calls",
        quota_limit=100,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db.add(quota)
    db.commit()

    # Mock B2B usage
    from app.infra.db.models.enterprise_feature_usage_counters import (
        EnterpriseFeatureUsageCounterModel,
    )
    from app.services.quota_window_resolver import QuotaWindowResolver

    now = datetime.now(timezone.utc)
    window = QuotaWindowResolver.compute_window("month", 1, "calendar", now)

    counter = EnterpriseFeatureUsageCounterModel(
        enterprise_account_id=20,
        feature_code="b2b_api_access",
        quota_key="api_calls",
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=45,
    )
    db.add(counter)
    db.commit()

    snapshot = EffectiveEntitlementResolverService.resolve_b2b_account_snapshot(
        db, enterprise_account_id=20
    )

    access = snapshot.entitlements["b2b_api_access"]
    assert access.granted is True
    assert access.reason_code == EffectiveEntitlementResolverService.REASON_GRANTED
    assert access.quota_limit == 100
    assert access.quota_used == 45
    assert access.quota_remaining == 55

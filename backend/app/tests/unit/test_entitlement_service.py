from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infra.db.base import Base
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
from app.services.billing_service import BillingPlanData, SubscriptionStatusData
from app.services.entitlement_service import EntitlementService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_get_user_canonical_plan_found(db):
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    db.add(plan)
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
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_user_canonical_plan(db, user_id=1)
        assert result is not None
        assert result.plan_code == "premium"


def test_get_user_canonical_plan_not_found(db):
    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="unknown",
            display_name="Unknown",
            monthly_price_cents=2000,
            currency="EUR",
            daily_message_limit=1000,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_user_canonical_plan(db, user_id=1)
        assert result is None


def test_get_feature_entitlement_canonical_quota(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id,
        feature_id=feat.id,
        access_mode=AccessMode.QUOTA,
        is_enabled=True,
        variant_code="standard",
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="messages",
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
            code="basic",
            display_name="Basic",
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=5,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.plan_code == "basic"
        assert result.final_access is True
        assert result.access_mode == "quota"
        assert len(result.quotas) == 1
        assert result.quotas[0].quota_limit == 10
        assert result.reason == "canonical_binding"
        assert result.variant_code == "standard"


def test_get_feature_entitlement_canonical_unlimited(db):
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.UNLIMITED, is_enabled=True
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
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.access_mode == "unlimited"
        assert result.final_access is True
        assert len(result.quotas) == 0


def test_get_feature_entitlement_canonical_disabled(db):
    plan = PlanCatalogModel(plan_code="free", plan_name="Free", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.DISABLED, is_enabled=True
    )
    db.add(binding)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="free",
            display_name="Free",
            monthly_price_cents=0,
            currency="EUR",
            daily_message_limit=0,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.access_mode == "disabled"
        assert result.is_enabled_by_plan is False
        assert result.final_access is False
        assert result.reason == "disabled_by_plan"


def test_get_feature_entitlement_unknown_feature(db):
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
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="unknown_feature"
        )
        assert result.reason == "feature_unknown"
        assert result.final_access is False


def test_get_feature_entitlement_billing_inactive(db):
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.UNLIMITED, is_enabled=True
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
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.billing_status == "past_due"
        assert result.final_access is False
        assert result.reason == "billing_inactive"
        assert result.is_enabled_by_plan is True


def test_get_feature_entitlement_no_plan(db):
    mock_sub = SubscriptionStatusData(
        status="none",
        plan=None,
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.reason == "no_plan"
        assert result.plan_code == "none"
        assert result.final_access is False


def test_get_feature_entitlement_quota_missing_definition(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()
    # NO QUOTA DEFINED

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="basic",
            display_name="Basic",
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=5,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.final_access is False
        assert result.is_enabled_by_plan is False
        assert len(result.quotas) == 0
        assert result.reason == "disabled_by_plan"


def test_no_binding_for_astrologer_chat_returns_canonical_no_binding(db):
    """AC: 10 - Plan et feature existent, pas de binding -> canonical_no_binding"""
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()
    # Aucun binding ajouté intentionnellement

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="basic",
            display_name="Basic",
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=5,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.reason == "canonical_no_binding"
        assert result.access_mode == "unknown"
        assert result.final_access is False
        assert result.is_enabled_by_plan is False


def test_missing_plan_catalog_returns_feature_unknown(db):
    """AC: 10 - Plan absent du catalog -> feature_unknown (comportement générique)"""
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add(feat)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="ghost_plan",
            display_name="Ghost",
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=10,
            is_active=True,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(
            db, user_id=1, feature_code="astrologer_chat"
        )
        assert result.reason == "feature_unknown"
        assert result.final_access is False


def test_basic_plan_astrologer_chat_quota_daily(db):
    """AC: 10 - plan basic, quota 5/day -> canonical_binding, window_end non null"""
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    db.add(PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="messages",
        quota_limit=5,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    ))
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(code="basic", display_name="B", is_active=True, monthly_price_cents=1, currency="EUR", daily_message_limit=0),
        failure_reason=None, updated_at=None,
    )

    with patch("app.services.entitlement_service.BillingService.get_subscription_status", return_value=mock_sub):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="astrologer_chat")
        assert result.reason == "canonical_binding"
        assert result.access_mode == "quota"
        assert len(result.usage_states) == 1
        assert result.usage_states[0].window_end is not None
        # Vérifier que window_end est dans le futur (fin de journée)
        assert result.usage_states[0].window_end > datetime.now(timezone.utc)


def test_premium_plan_astrologer_chat_quota_monthly(db):
    """AC: 10 - plan premium, quota 2000/month -> window_end = fin du mois UTC"""
    plan = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    db.add(PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="messages",
        quota_limit=2000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    ))
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(code="premium", display_name="P", is_active=True, monthly_price_cents=1, currency="EUR", daily_message_limit=0),
        failure_reason=None, updated_at=None,
    )

    with patch("app.services.entitlement_service.BillingService.get_subscription_status", return_value=mock_sub):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="astrologer_chat")
        assert result.reason == "canonical_binding"
        assert len(result.usage_states) == 1
        window_end = result.usage_states[0].window_end
        assert window_end is not None
        # Vérifier que c'est le 1er du mois suivant à 00:00:00 UTC
        now = datetime.now(timezone.utc)
        if now.month == 12:
            expected_year, expected_month = now.year + 1, 1
        else:
            expected_year, expected_month = now.year, now.month + 1
        assert window_end.year == expected_year
        assert window_end.month == expected_month
        assert window_end.day == 1
        assert window_end.hour == 0


def test_trial_plan_astrologer_chat_disabled(db):
    """AC: 10 - plan trial -> disabled_by_plan, final_access=False"""
    plan = PlanCatalogModel(plan_code="trial", plan_name="Trial", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="astrologer_chat", feature_name="Chat")
    db.add_all([plan, feat])
    db.commit()

    db.add(PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.DISABLED, is_enabled=True
    ))
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="trialing",
        plan=BillingPlanData(code="trial", display_name="T", is_active=True, monthly_price_cents=1, currency="EUR", daily_message_limit=0),
        failure_reason=None, updated_at=None,
    )

    with patch("app.services.entitlement_service.BillingService.get_subscription_status", return_value=mock_sub):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="astrologer_chat")
        assert result.reason == "disabled_by_plan"
        assert result.final_access is False
        assert result.usage_states == []

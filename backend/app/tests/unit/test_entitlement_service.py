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


def test_get_feature_entitlement_legacy_fallback_chat(db):
    # No plan or feature in catalog
    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="legacy",
            display_name="Legacy",
            monthly_price_cents=500,
            currency="EUR",
            daily_message_limit=7,
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
        assert result.reason == "legacy_fallback"
        assert result.access_mode == "quota"
        assert len(result.quotas) == 1
        assert result.quotas[0].quota_limit == 7
        assert result.final_access is True


def test_get_feature_entitlement_legacy_fallback_chat_disabled(db):
    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="legacy",
            display_name="Legacy",
            monthly_price_cents=500,
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
        assert result.reason == "legacy_fallback"
        assert result.access_mode == "disabled"
        assert result.final_access is False


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


def test_get_feature_entitlement_plan_not_in_catalog_fallback(db):
    # Plan in billing but not in plan_catalog -> fallback legacy
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
        assert result.reason == "legacy_fallback"
        assert result.quotas[0].quota_limit == 10


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


def test_get_feature_entitlement_canonical_no_binding(db):
    """Feature connue, plan connu, aucun binding, hors scope fallback legacy."""
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="natal_chart_long", feature_name="Natal Chart Long")
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
            db, user_id=1, feature_code="natal_chart_long"
        )
        assert result.reason == "canonical_no_binding"
        assert result.access_mode == "unknown"
        assert result.final_access is False
        assert result.is_enabled_by_plan is False
        assert result.plan_code == "basic"


def test_get_feature_entitlement_unknown_billing_status(db):
    mock_sub = SubscriptionStatusData(
        status="weird_status",
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
        assert result.final_access is False
        # Reason depends on if it found a binding or not
        # Since we didn't add a binding in this test, it will try fallback
        # If fallback is used, it will be billing_inactive because of the override
        assert result.reason == "billing_inactive"


def test_entitlement_quota_remaining_gt_0_final_access_true(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="feat1", feature_name="F1")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="daily",
        quota_limit=5,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db.add(quota)
    db.commit()

    UTC = timezone.utc
    window_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=1)

    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="feat1",
        quota_key="daily",
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window_start,
        window_end=window_end,
        used_count=2,
    )
    db.add(counter)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="basic",
            display_name="B",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=0,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="feat1")
        assert result.final_access is True
        assert result.quota_exhausted is False
        assert len(result.usage_states) == 1
        assert result.usage_states[0].used == 2
        assert result.usage_states[0].remaining == 3


def test_entitlement_quota_exhausted_final_access_false(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="feat1", feature_name="F1")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="daily",
        quota_limit=5,
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db.add(quota)
    db.commit()

    UTC = timezone.utc
    window_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=1)

    counter = FeatureUsageCounterModel(
        user_id=1,
        feature_code="feat1",
        quota_key="daily",
        period_unit=PeriodUnit.DAY,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window_start,
        window_end=window_end,
        used_count=5,
    )
    db.add(counter)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="basic",
            display_name="B",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=0,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="feat1")
        assert result.final_access is False
        assert result.quota_exhausted is True
        assert result.reason == "canonical_binding"


def test_entitlement_no_counter_final_access_true(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="feat1", feature_name="F1")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    quota = PlanFeatureQuotaModel(
        plan_feature_binding_id=binding.id,
        quota_key="daily",
        quota_limit=5,
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
            display_name="B",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=0,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="feat1")
        assert result.final_access is True
        assert result.quota_exhausted is False
        assert len(result.usage_states) == 1
        assert result.usage_states[0].used == 0


def test_entitlement_billing_inactive_skips_quota(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="feat1", feature_name="F1")
    db.add_all([plan, feat])
    db.commit()

    binding = PlanFeatureBindingModel(
        plan_id=plan.id, feature_id=feat.id, access_mode=AccessMode.QUOTA, is_enabled=True
    )
    db.add(binding)
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="past_due",
        plan=BillingPlanData(
            code="basic",
            display_name="B",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=0,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="feat1")
        assert result.final_access is False
        assert result.reason == "billing_inactive"
        assert result.usage_states == []


def test_legacy_fallback_usage_states_empty(db):
    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="legacy",
            display_name="L",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=10,
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
        assert result.reason == "legacy_fallback"
        assert result.final_access is True
        assert result.usage_states == []
        assert result.quota_exhausted is False


def test_entitlement_no_plan_skips_quota(db):
    # no_plan → final_access=False, reason="no_plan", usage_states=[]
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
        assert result.final_access is False
        assert result.reason == "no_plan"
        assert result.usage_states == []
        assert result.quota_exhausted is False


def test_entitlement_rolling_quota_disables_access_instead_of_crashing(db):
    plan = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    feat = FeatureCatalogModel(feature_code="feat1", feature_name="F1")
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

    db.add(
        PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="rolling-daily",
            quota_limit=5,
            period_unit=PeriodUnit.DAY,
            period_value=1,
            reset_mode=ResetMode.ROLLING,
        )
    )
    db.commit()

    mock_sub = SubscriptionStatusData(
        status="active",
        plan=BillingPlanData(
            code="basic",
            display_name="B",
            monthly_price_cents=1,
            currency="EUR",
            is_active=True,
            daily_message_limit=0,
        ),
        failure_reason=None,
        updated_at=None,
    )

    with patch(
        "app.services.entitlement_service.BillingService.get_subscription_status",
        return_value=mock_sub,
    ):
        result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="feat1")

    assert result.final_access is False
    assert result.is_enabled_by_plan is False
    assert result.reason == "disabled_by_plan"
    assert result.usage_states == []
    assert result.quota_exhausted is False

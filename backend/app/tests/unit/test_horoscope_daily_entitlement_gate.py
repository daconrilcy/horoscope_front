from unittest.mock import patch

import pytest

from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
)
from app.services.horoscope_daily_entitlement_gate import (
    HoroscopeDailyAccessDeniedError,
    HoroscopeDailyEntitlementGate,
)


def make_snapshot(**kwargs) -> EffectiveEntitlementsSnapshot:
    access_defaults = dict(
        granted=True,
        reason_code="granted",
        access_mode="unlimited",
        variant_code="full",
        quota_limit=0,
        quota_used=0,
        quota_remaining=0,
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
        usage_states=[],
    )
    access_data = {**access_defaults, **kwargs.pop("access", {})}
    access = EffectiveFeatureAccess(**access_data)

    defaults = dict(
        subject_type="b2c_user",
        subject_id=1,
        plan_code="premium",
        billing_status="active",
        entitlements={"horoscope_daily": access},
    )
    return EffectiveEntitlementsSnapshot(**{**defaults, **kwargs})


def test_check_and_get_variant_access_denied(db_session):
    snapshot = make_snapshot(
        access=dict(granted=False, reason_code="feature_not_in_plan"),
        plan_code="free",
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(HoroscopeDailyAccessDeniedError) as excinfo:
            HoroscopeDailyEntitlementGate.check_and_get_variant(db_session, user_id=1)

    assert excinfo.value.plan_code == "free"
    assert excinfo.value.reason_code == "feature_not_in_plan"


def test_check_and_get_variant_free(db_session):
    snapshot = make_snapshot(
        access=dict(granted=True, variant_code="summary_only"),
        plan_code="free",
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = HoroscopeDailyEntitlementGate.check_and_get_variant(db_session, user_id=1)

    assert result.variant_code == "summary_only"


def test_check_and_get_variant_basic(db_session):
    snapshot = make_snapshot(
        access=dict(granted=True, variant_code="full"),
        plan_code="basic",
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = HoroscopeDailyEntitlementGate.check_and_get_variant(db_session, user_id=1)

    assert result.variant_code == "full"


def test_check_and_get_variant_premium(db_session):
    snapshot = make_snapshot(
        access=dict(granted=True, variant_code="full"),
        plan_code="premium",
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = HoroscopeDailyEntitlementGate.check_and_get_variant(db_session, user_id=1)

    assert result.variant_code == "full"


def test_check_and_get_variant_default_full(db_session):
    # If variant_code is missing for some reason but granted=True
    snapshot = make_snapshot(
        access=dict(granted=True, variant_code=None),
        plan_code="premium",
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = HoroscopeDailyEntitlementGate.check_and_get_variant(db_session, user_id=1)

    assert result.variant_code == "full"

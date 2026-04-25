from unittest.mock import patch

import pytest

from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementGate,
    NatalChartLongQuotaExceededError,
)


def test_natal_gate_uses_resolver_success(db_session):
    # GIVEN
    user_id = 42
    access = EffectiveFeatureAccess(
        granted=True,
        reason_code="granted",
        access_mode="unlimited",
        variant_code="multi_astrologer",
        quota_limit=None,
        quota_used=None,
        quota_remaining=None,
        period_unit=None,
        period_value=None,
        reset_mode=None,
    )
    snapshot = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=user_id,
        plan_code="premium",
        billing_status="active",
        entitlements={"natal_chart_long": access},
    )

    with patch.object(
        EffectiveEntitlementResolverService, "resolve_b2c_user_snapshot", return_value=snapshot
    ) as mock_resolver:
        # WHEN
        result = NatalChartLongEntitlementGate.check_access(db_session, user_id=user_id)

    # THEN
    assert result.path == "canonical_unlimited"
    assert result.variant_code == "multi_astrologer"
    mock_resolver.assert_called_once_with(db_session, app_user_id=user_id)


def test_natal_gate_uses_resolver_quota_exceeded(db_session):
    # GIVEN
    user_id = 42
    access = EffectiveFeatureAccess(
        granted=False,
        reason_code="quota_exhausted",
        access_mode="quota",
        variant_code="single_astrologer",
        quota_limit=1,
        quota_used=1,
        quota_remaining=0,
        period_unit="lifetime",
        period_value=1,
        reset_mode="lifetime",
    )
    snapshot = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=user_id,
        plan_code="premium",
        billing_status="active",
        entitlements={"natal_chart_long": access},
    )

    with patch.object(
        EffectiveEntitlementResolverService, "resolve_b2c_user_snapshot", return_value=snapshot
    ):
        # WHEN / THEN
        with pytest.raises(NatalChartLongQuotaExceededError) as exc:
            NatalChartLongEntitlementGate.check_access(db_session, user_id=user_id)

        assert exc.value.quota_key == "natal_chart_long"
        assert exc.value.used == 1
        assert exc.value.limit == 1


def test_natal_gate_uses_resolver_access_denied(db_session):
    # GIVEN
    user_id = 42
    access = EffectiveFeatureAccess(
        granted=False,
        reason_code="billing_inactive",
        access_mode="unlimited",
        variant_code=None,
        quota_limit=None,
        quota_used=None,
        quota_remaining=None,
        period_unit=None,
        period_value=None,
        reset_mode=None,
    )
    snapshot = EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=user_id,
        plan_code="premium",
        billing_status="past_due",
        entitlements={"natal_chart_long": access},
    )

    with patch.object(
        EffectiveEntitlementResolverService, "resolve_b2c_user_snapshot", return_value=snapshot
    ):
        # WHEN / THEN
        with pytest.raises(NatalChartLongAccessDeniedError) as exc:
            NatalChartLongEntitlementGate.check_access(db_session, user_id=user_id)

        assert exc.value.reason == "billing_inactive"
        assert exc.value.billing_status == "past_due"
        assert exc.value.plan_code == "premium"

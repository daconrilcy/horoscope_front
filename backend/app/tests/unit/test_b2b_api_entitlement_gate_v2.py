from unittest.mock import patch

import pytest

from app.services.b2b_api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)


def test_b2b_gate_uses_resolver_success(db_session):
    # GIVEN
    account_id = 1
    access = EffectiveFeatureAccess(
        granted=True,
        reason_code="granted",
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
        subject_type="b2b_account",
        subject_id=account_id,
        plan_code="b2b-premium",
        billing_status="active",
        entitlements={"b2b_api_access": access},
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ) as mock_resolver:
        # WHEN
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=account_id)

    # THEN
    assert result.path == "canonical_unlimited"
    mock_resolver.assert_called_once_with(db_session, enterprise_account_id=account_id)


def test_b2b_gate_uses_resolver_quota_exceeded(db_session):
    # GIVEN
    account_id = 1
    access = EffectiveFeatureAccess(
        granted=False,
        reason_code="quota_exhausted",
        access_mode="quota",
        variant_code=None,
        quota_limit=1000,
        quota_used=1000,
        quota_remaining=0,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
    )
    usage_state = UsageState(
        feature_code="b2b_api_access",
        quota_key="calls",
        quota_limit=1000,
        used=1000,
        remaining=0,
        exhausted=True,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
        window_start=None,
        window_end=None,
    )
    snapshot = EffectiveEntitlementsSnapshot(
        subject_type="b2b_account",
        subject_id=account_id,
        plan_code="b2b-premium",
        billing_status="active",
        entitlements={
            "b2b_api_access": EffectiveFeatureAccess(
                **{**access.__dict__, "usage_states": [usage_state]}
            )
        },
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ):
        # WHEN / THEN
        with pytest.raises(B2BApiQuotaExceededError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=account_id)

        assert exc.value.code == "b2b_api_quota_exceeded"
        assert exc.value.details["quota_key"] == "calls"


def test_b2b_gate_uses_resolver_access_denied(db_session):
    # GIVEN
    account_id = 1
    access = EffectiveFeatureAccess(
        granted=False,
        reason_code="feature_not_in_plan",
        access_mode=None,
        variant_code=None,
        quota_limit=None,
        quota_used=None,
        quota_remaining=None,
        period_unit=None,
        period_value=None,
        reset_mode=None,
    )
    snapshot = EffectiveEntitlementsSnapshot(
        subject_type="b2b_account",
        subject_id=account_id,
        plan_code="none",
        billing_status="none",
        entitlements={"b2b_api_access": access},
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ):
        # WHEN / THEN
        with pytest.raises(B2BApiAccessDeniedError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=account_id)

        assert exc.value.code == "b2b_no_canonical_plan"
        assert exc.value.details["reason_code"] == "feature_not_in_plan"

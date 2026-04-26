from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services.b2b.api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)
from app.services.b2b.enterprise_quota_usage_service import EnterpriseQuotaUsageService
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)


def make_snapshot(**kwargs) -> EffectiveEntitlementsSnapshot:
    access_defaults = dict(
        granted=True,
        reason_code="granted",
        access_mode="quota",
        variant_code=None,
        quota_limit=1000,
        quota_used=0,
        quota_remaining=1000,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
        usage_states=[
            UsageState(
                feature_code="b2b_api_access",
                quota_key="calls",
                quota_limit=1000,
                used=0,
                remaining=1000,
                exhausted=False,
                period_unit="month",
                period_value=1,
                reset_mode="calendar",
                window_start=None,
                window_end=None,
            )
        ],
    )
    access_data = {**access_defaults, **kwargs.pop("access", {})}
    access = EffectiveFeatureAccess(**access_data)

    defaults = dict(
        subject_type="b2b_account",
        subject_id=1,
        plan_code="b2b-test",
        billing_status="active",
        entitlements={"b2b_api_access": access},
    )
    return EffectiveEntitlementsSnapshot(**{**defaults, **kwargs})


def test_check_and_consume_quota_success(db_session):
    snapshot = make_snapshot()
    mock_state = MagicMock(used=1, remaining=999, quota_limit=1000)

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2b_account_snapshot",
            return_value=snapshot,
        ),
        patch.object(EnterpriseQuotaUsageService, "consume", return_value=mock_state),
    ):
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    assert len(result.usage_states) == 1
    state = result.usage_states[0]
    assert state.used == 1
    assert state.remaining == 999
    assert state.quota_limit == 1000


def test_check_and_consume_unlimited(db_session):
    snapshot = make_snapshot(access=dict(access_mode="unlimited", usage_states=[]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2b_account_snapshot",
            return_value=snapshot,
        ),
        patch.object(EnterpriseQuotaUsageService, "consume"),
    ):
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_unlimited"
    assert len(result.usage_states) == 0


def test_check_and_consume_disabled(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="binding_disabled"))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(B2BApiAccessDeniedError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)
    assert exc.value.code == "b2b_api_access_denied"
    assert exc.value.details["reason"] == "disabled_by_plan"
    assert exc.value.details["reason_code"] == "binding_disabled"


def test_check_and_consume_quota_exhausted(db_session):
    from app.services.quota.usage_service import QuotaExhaustedError

    snapshot = make_snapshot()

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2b_account_snapshot",
            return_value=snapshot,
        ),
        patch.object(
            EnterpriseQuotaUsageService,
            "consume",
            side_effect=QuotaExhaustedError(
                quota_key="calls",
                used=1000,
                limit=1000,
                feature_code="b2b_api_access",
            ),
        ),
    ):
        with pytest.raises(B2BApiQuotaExceededError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)
    assert exc.value.code == "b2b_api_quota_exceeded"


def test_check_and_consume_fallback_no_canonical(db_session):
    # Resolver handles no plan by returning a snapshot with plan_code="none" and granted=False
    snapshot = make_snapshot(
        plan_code="none",
        billing_status="none",
        access=dict(granted=False, reason_code="feature_not_in_plan"),
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(B2BApiAccessDeniedError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_no_canonical_plan"


def test_check_and_consume_fallback_no_binding(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="feature_not_in_plan"))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2b_account_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(B2BApiAccessDeniedError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_no_binding"


def test_check_and_consume_admin_user_missing_no_longer_blocks_quota(db_session):
    # Regression: si le resolver accorde l'accès, l'absence d'admin lié ne doit plus bloquer.
    snapshot = make_snapshot()
    mock_state = MagicMock(used=1, remaining=999)

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2b_account_snapshot",
            return_value=snapshot,
        ),
        patch.object(EnterpriseQuotaUsageService, "consume", return_value=mock_state),
    ):
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states[0].used == 1

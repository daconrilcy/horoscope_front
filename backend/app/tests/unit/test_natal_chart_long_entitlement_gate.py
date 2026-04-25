from unittest.mock import MagicMock, patch

import pytest

from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementGate,
    NatalChartLongQuotaExceededError,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
)


def make_snapshot(**kwargs) -> EffectiveEntitlementsSnapshot:
    access_defaults = dict(
        granted=True,
        reason_code="granted",
        access_mode="quota",
        variant_code="single_astrologer",
        quota_limit=1,
        quota_used=0,
        quota_remaining=1,
        period_unit="lifetime",
        period_value=1,
        reset_mode="lifetime",
        usage_states=[],
    )
    access_data = {**access_defaults, **kwargs.pop("access", {})}
    access = EffectiveFeatureAccess(**access_data)

    defaults = dict(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="trial",
        billing_status="active",
        entitlements={"natal_chart_long": access},
    )
    return EffectiveEntitlementsSnapshot(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)
    mock_state.quota_key = "interpretations"
    mock_state.period_unit = "lifetime"
    mock_state.period_value = 1
    mock_state.reset_mode = "lifetime"

    snapshot = make_snapshot(access=dict(access_mode="quota", usage_states=[mock_state]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ) as mock_consume,
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_quota"
    assert result.variant_code == "single_astrologer"
    mock_consume.assert_called_once()


def test_canonical_unlimited_path_no_consume(db_session):
    snapshot = make_snapshot(access=dict(access_mode="unlimited"))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch("app.services.quota_usage_service.QuotaUsageService.consume") as mock_consume,
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_unlimited"
    assert result.variant_code == "single_astrologer"
    mock_consume.assert_not_called()


def test_variant_code_single_astrologer(db_session):
    snapshot = make_snapshot(access=dict(variant_code="single_astrologer"))
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)
    mock_state.quota_key = "interpretations"
    mock_state.period_unit = "lifetime"
    mock_state.period_value = 1
    mock_state.reset_mode = "lifetime"
    snapshot.entitlements["natal_chart_long"] = snapshot.entitlements["natal_chart_long"].__class__(
        **{**snapshot.entitlements["natal_chart_long"].__dict__, "usage_states": [mock_state]}
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ),
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.variant_code == "single_astrologer"


def test_variant_code_multi_astrologer(db_session):
    snapshot = make_snapshot(access=dict(variant_code="multi_astrologer"))
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)
    mock_state.quota_key = "interpretations"
    mock_state.period_unit = "lifetime"
    mock_state.period_value = 1
    mock_state.reset_mode = "lifetime"
    snapshot.entitlements["natal_chart_long"] = snapshot.entitlements["natal_chart_long"].__class__(
        **{**snapshot.entitlements["natal_chart_long"].__dict__, "usage_states": [mock_state]}
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ),
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.variant_code == "multi_astrologer"


def test_access_denied_no_plan(db_session):
    snapshot = make_snapshot(
        plan_code="none",
        access=dict(granted=False, reason_code="feature_not_in_plan"),
    )
    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(NatalChartLongAccessDeniedError) as exc_info:
            NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "no_plan"


def test_access_denied_disabled_by_plan(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="binding_disabled"))
    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(NatalChartLongAccessDeniedError) as exc_info:
            NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "disabled_by_plan"


def test_quota_exceeded_raises_natal_error(db_session):
    from app.services.quota_usage_service import QuotaExhaustedError

    mock_state = MagicMock(used=0, remaining=1, quota_limit=1, window_end=None)
    mock_state.quota_key = "interpretations"
    mock_state.period_unit = "lifetime"
    mock_state.period_value = 1
    mock_state.reset_mode = "lifetime"

    snapshot = make_snapshot(access=dict(usage_states=[mock_state]))
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume",
            side_effect=QuotaExhaustedError(
                quota_key="interpretations",
                used=1,
                limit=1,
                feature_code="natal_chart_long",
            ),
        ),
    ):
        with pytest.raises(NatalChartLongQuotaExceededError) as exc_info:
            NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert exc_info.value.quota_key == "interpretations"
    assert exc_info.value.window_end is None

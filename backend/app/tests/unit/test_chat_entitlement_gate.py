from unittest.mock import MagicMock, patch

import pytest

from app.services.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatQuotaExceededError,
)
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    QuotaDefinition,
    UsageState,
)
from app.services.quota_usage_service import QuotaUsageService


def make_snapshot(**kwargs) -> EffectiveEntitlementsSnapshot:
    access_defaults = dict(
        granted=True,
        reason_code="granted",
        access_mode="quota",
        variant_code=None,
        quota_limit=5,
        quota_used=0,
        quota_remaining=5,
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
        plan_code="essai",
        billing_status="active",
        entitlements={"astrologer_chat": access},
    )
    return EffectiveEntitlementsSnapshot(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    mock_state = MagicMock(spec=UsageState)
    mock_state.quota_key = "daily"
    mock_state.quota_limit = 5
    mock_state.period_unit = "day"
    mock_state.period_value = 1
    mock_state.reset_mode = "calendar"

    snapshot = make_snapshot(access=dict(access_mode="quota", usage_states=[mock_state]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch.object(QuotaUsageService, "consume", return_value=mock_state) as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states == [mock_state]
    mock_consume.assert_called_once()
    call_args = mock_consume.call_args[1]
    assert call_args["user_id"] == 1
    assert call_args["feature_code"] == "astrologer_chat"
    assert isinstance(call_args["quota"], QuotaDefinition)


def test_canonical_unlimited_path_no_consume(db_session):
    mock_state = MagicMock(spec=UsageState)
    snapshot = make_snapshot(access=dict(access_mode="unlimited", usage_states=[mock_state]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch.object(QuotaUsageService, "consume") as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_unlimited"
    assert result.usage_states == [mock_state]
    mock_consume.assert_not_called()


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
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "no_plan"


def test_canonical_no_binding_raises_access_denied(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="feature_not_in_plan"))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "canonical_no_binding"


def test_access_denied_billing_inactive(db_session):
    snapshot = make_snapshot(
        billing_status="past_due", access=dict(granted=False, reason_code="billing_inactive")
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "billing_inactive"


def test_canonical_disabled_binding_rejected_403(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="binding_disabled"))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "disabled_by_plan"


def test_quota_exceeded_raises_chat_error(db_session):
    exhausted_state = MagicMock(spec=UsageState)
    exhausted_state.quota_key = "daily"
    exhausted_state.quota_limit = 5
    exhausted_state.used = 5
    exhausted_state.remaining = 0
    exhausted_state.exhausted = True
    exhausted_state.period_unit = "day"
    exhausted_state.period_value = 1
    exhausted_state.window_end = None
    snapshot = make_snapshot(
        access=dict(
            granted=False,
            reason_code="quota_exhausted",
            quota_used=5,
            quota_limit=5,
            usage_states=[exhausted_state],
        )
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatQuotaExceededError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.quota_key == "daily"
    assert excinfo.value.used == 5
    assert excinfo.value.limit == 5


def test_consume_called_once_per_quota(db_session):
    mock_state1 = MagicMock(spec=UsageState)
    mock_state1.quota_key = "q1"
    mock_state1.quota_limit = 5
    mock_state1.period_unit = "day"
    mock_state1.period_value = 1
    mock_state1.reset_mode = "calendar"

    mock_state2 = MagicMock(spec=UsageState)
    mock_state2.quota_key = "q2"
    mock_state2.quota_limit = 10
    mock_state2.period_unit = "month"
    mock_state2.period_value = 1
    mock_state2.reset_mode = "calendar"

    snapshot = make_snapshot(
        access=dict(access_mode="quota", usage_states=[mock_state1, mock_state2])
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch.object(
            QuotaUsageService, "consume", side_effect=[mock_state1, mock_state2]
        ) as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert len(result.usage_states) == 2
    assert mock_consume.call_count == 2

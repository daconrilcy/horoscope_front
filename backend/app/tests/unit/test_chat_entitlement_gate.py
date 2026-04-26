from unittest.mock import MagicMock, patch

import pytest

from app.services.entitlement.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatQuotaExceededError,
)
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)
from app.services.quota.usage_service import QuotaUsageService


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


def test_check_access_nominal_quota(db_session):
    mock_state = MagicMock(spec=UsageState)
    mock_state.quota_key = "tokens"
    mock_state.quota_limit = 5000
    snapshot = make_snapshot(access=dict(access_mode="quota", usage_states=[mock_state]))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = ChatEntitlementGate.check_access(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states == [mock_state]


def test_check_access_unlimited(db_session):
    snapshot = make_snapshot(access=dict(access_mode="unlimited", usage_states=[]))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = ChatEntitlementGate.check_access(db_session, user_id=1)

    assert result.path == "canonical_unlimited"
    assert result.usage_states == []


def test_check_access_denied_quota_exhausted(db_session):
    exhausted_state = MagicMock(spec=UsageState)
    exhausted_state.quota_key = "tokens"
    exhausted_state.used = 5000
    exhausted_state.quota_limit = 5000
    exhausted_state.exhausted = True
    exhausted_state.period_unit = "month"
    exhausted_state.period_value = 1
    exhausted_state.window_end = None
    snapshot = make_snapshot(
        access=dict(
            granted=False,
            reason_code="quota_exhausted",
            usage_states=[exhausted_state],
        )
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatQuotaExceededError) as exc:
            ChatEntitlementGate.check_access(db_session, user_id=1)

    assert exc.value.quota_key == "tokens"


def test_check_and_consume_skips_tokens_quota(db_session):
    # Quota key is 'tokens' -> should be skipped by check_and_consume
    mock_state = MagicMock(spec=UsageState)
    mock_state.quota_key = "tokens"
    snapshot = make_snapshot(access=dict(access_mode="quota", usage_states=[mock_state]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch.object(QuotaUsageService, "consume") as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states == []  # Consumed states list is empty because skip
    mock_consume.assert_not_called()


def test_check_and_consume_processes_legacy_quota(db_session):
    # Quota key is NOT 'tokens' -> should be consumed
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


def test_check_and_consume_processes_messages_quota(db_session):
    # Quota key is 'messages' -> should be consumed immediately
    mock_state = MagicMock(spec=UsageState)
    mock_state.quota_key = "messages"
    mock_state.quota_limit = 1
    mock_state.period_unit = "week"
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
    # Verify consumption amount is 1
    mock_consume.assert_called_once()
    call_args = mock_consume.call_args[1]
    assert call_args["amount"] == 1
    assert call_args["feature_code"] == "astrologer_chat"
    assert call_args["quota"].quota_key == "messages"


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
            ChatEntitlementGate.check_access(db_session, user_id=1)

    assert excinfo.value.reason == "no_plan"


def test_canonical_no_binding_raises_access_denied(db_session):
    snapshot = make_snapshot(access=dict(granted=False, reason_code="feature_not_in_plan"))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_access(db_session, user_id=1)

    assert excinfo.value.reason == "canonical_no_binding"

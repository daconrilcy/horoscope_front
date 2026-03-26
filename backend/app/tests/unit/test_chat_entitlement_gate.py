from unittest.mock import MagicMock, patch

import pytest

from app.services.chat_entitlement_gate import (
    ChatAccessDeniedError,
    ChatEntitlementGate,
    ChatQuotaExceededError,
)
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaUsageService


def make_entitlement(**kwargs) -> FeatureEntitlement:
    defaults = dict(
        plan_code="essai",
        billing_status="active",
        is_enabled_by_plan=True,
        access_mode="quota",
        variant_code=None,
        quotas=[],
        final_access=True,
        reason="canonical_binding",
        usage_states=[],
        quota_exhausted=False,
    )
    return FeatureEntitlement(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    quota = QuotaDefinition(
        quota_key="daily", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    entitlement = make_entitlement(access_mode="quota", quotas=[quota])
    mock_state = MagicMock(spec=UsageState)
    mock_state.used = 3
    mock_state.remaining = 2
    mock_state.quota_limit = 5

    with (
        patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement),
        patch.object(QuotaUsageService, "consume", return_value=mock_state) as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states == [mock_state]
    mock_consume.assert_called_once_with(
        db_session, user_id=1, feature_code="astrologer_chat", quota=quota, amount=1
    )


def test_canonical_unlimited_path_no_consume(db_session):
    entitlement = make_entitlement(access_mode="unlimited")
    mock_state = MagicMock(spec=UsageState)
    entitlement.usage_states = [mock_state]

    with (
        patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement),
        patch.object(QuotaUsageService, "consume") as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_unlimited"
    assert result.usage_states == [mock_state]
    mock_consume.assert_not_called()


def test_legacy_fallback_returns_legacy_path(db_session):
    entitlement = make_entitlement(reason="legacy_fallback", final_access=False)

    with (
        patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement),
        patch.object(QuotaUsageService, "consume") as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "legacy"
    assert result.usage_states == []
    mock_consume.assert_not_called()


def test_access_denied_no_plan(db_session):
    entitlement = make_entitlement(final_access=False, reason="no_plan")

    with patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "no_plan"


def test_access_denied_billing_inactive(db_session):
    entitlement = make_entitlement(final_access=False, reason="billing_inactive")

    with patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "billing_inactive"


def test_canonical_disabled_binding_rejected_403(db_session):
    entitlement = make_entitlement(final_access=False, reason="disabled_by_plan")

    with patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement):
        with pytest.raises(ChatAccessDeniedError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.reason == "disabled_by_plan"


def test_quota_exceeded_raises_chat_error(db_session):
    mock_state = MagicMock(spec=UsageState)
    mock_state.exhausted = True
    mock_state.quota_key = "daily"
    mock_state.used = 5
    mock_state.quota_limit = 5
    mock_state.window_end = None

    entitlement = make_entitlement(
        final_access=False, quota_exhausted=True, usage_states=[mock_state]
    )

    with patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement):
        with pytest.raises(ChatQuotaExceededError) as excinfo:
            ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert excinfo.value.quota_key == "daily"
    assert excinfo.value.used == 5
    assert excinfo.value.limit == 5


def test_consume_called_once_per_quota(db_session):
    quota1 = QuotaDefinition(
        quota_key="q1", quota_limit=5, period_unit="day", period_value=1, reset_mode="calendar"
    )
    quota2 = QuotaDefinition(
        quota_key="q2", quota_limit=10, period_unit="month", period_value=1, reset_mode="calendar"
    )
    entitlement = make_entitlement(access_mode="quota", quotas=[quota1, quota2])

    mock_state1 = MagicMock(spec=UsageState)
    mock_state2 = MagicMock(spec=UsageState)

    with (
        patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement),
        patch.object(
            QuotaUsageService, "consume", side_effect=[mock_state1, mock_state2]
        ) as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "canonical_quota"
    assert len(result.usage_states) == 2
    assert mock_consume.call_count == 2


def test_legacy_fallback_final_access_false_still_delegates(db_session):
    # legacy_fallback is evaluated before final_access
    entitlement = make_entitlement(reason="legacy_fallback", final_access=False)

    with (
        patch.object(EntitlementService, "get_feature_entitlement", return_value=entitlement),
        patch.object(QuotaUsageService, "consume") as mock_consume,
    ):
        result = ChatEntitlementGate.check_and_consume(db_session, user_id=1)

    assert result.path == "legacy"
    mock_consume.assert_not_called()

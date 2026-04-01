from unittest.mock import MagicMock, patch

import pytest

from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)
from app.services.quota_usage_service import QuotaExhaustedError
from app.services.thematic_consultation_entitlement_gate import (
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
    ThematicConsultationEntitlementGate,
)


@pytest.fixture
def mock_user():
    return MagicMock(id=42, email="user@example.com")


def make_snapshot(**kwargs) -> EffectiveEntitlementsSnapshot:
    access_defaults = dict(
        granted=True,
        reason_code="granted",
        access_mode="quota",
        variant_code=None,
        quota_limit=20000,
        quota_used=0,
        quota_remaining=20000,
        period_unit="week",
        period_value=1,
        reset_mode="calendar",
        usage_states=[
            UsageState(
                feature_code="thematic_consultation",
                quota_key="tokens",
                quota_limit=20000,
                used=0,
                remaining=20000,
                exhausted=False,
                period_unit="week",
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
        subject_type="b2c_user",
        subject_id=42,
        plan_code="basic",
        billing_status="active",
        entitlements={"thematic_consultation": access},
    )
    return EffectiveEntitlementsSnapshot(**{**defaults, **kwargs})


def test_check_access_nominal_quota(db_session):
    snapshot = make_snapshot()
    mock_state = snapshot.entitlements["thematic_consultation"].usage_states[0]

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = ThematicConsultationEntitlementGate.check_access(db_session, user_id=42)

    assert result.path == "canonical_quota"
    assert result.usage_states == [mock_state]


def test_check_access_unlimited(db_session):
    snapshot = make_snapshot(access=dict(access_mode="unlimited", usage_states=[]))

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        result = ThematicConsultationEntitlementGate.check_access(db_session, user_id=42)

    assert result.path == "canonical_unlimited"
    assert result.usage_states == []


def test_check_and_consume_skips_tokens_quota(db_session):
    snapshot = make_snapshot()
    
    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume"
        ) as mock_consume,
    ):
        result = ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_quota"
    assert result.usage_states == [] # Skipped
    mock_consume.assert_not_called()


def test_check_and_consume_processes_legacy_quota(db_session):
    legacy_state = UsageState(
        feature_code="thematic_consultation",
        quota_key="consultations",
        quota_limit=1,
        used=0,
        remaining=1,
        exhausted=False,
        period_unit="week",
        period_value=1,
        reset_mode="calendar",
        window_start=None,
        window_end=None,
    )
    snapshot = make_snapshot(access=dict(usage_states=[legacy_state]))

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume",
            return_value=legacy_state,
        ) as mock_consume,
    ):
        result = ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_quota"
    assert result.usage_states == [legacy_state]
    mock_consume.assert_called_once()


def test_access_denied_no_plan(db_session):
    snapshot = make_snapshot(
        plan_code="none",
        billing_status="none",
        access=dict(granted=False, reason_code="feature_not_in_plan"),
    )

    with patch.object(
        EffectiveEntitlementResolverService,
        "resolve_b2c_user_snapshot",
        return_value=snapshot,
    ):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_access(db_session, user_id=42)
    assert exc_info.value.reason == "no_plan"


def test_quota_exceeded_raises_consultation_error(db_session):
    exhausted_state = UsageState(
        feature_code="thematic_consultation",
        quota_key="tokens",
        quota_limit=20000,
        used=20000,
        remaining=0,
        exhausted=True,
        period_unit="week",
        period_value=1,
        reset_mode="calendar",
        window_start=None,
        window_end=None,
    )
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
        with pytest.raises(ConsultationQuotaExceededError) as exc_info:
            ThematicConsultationEntitlementGate.check_access(db_session, user_id=42)
    
    assert exc_info.value.quota_key == "tokens"
    assert exc_info.value.used == 20000

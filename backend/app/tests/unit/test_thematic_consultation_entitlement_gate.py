from unittest.mock import MagicMock, patch

import pytest

from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaExhaustedError
from app.services.thematic_consultation_entitlement_gate import (
    ConsultationAccessDeniedError,
    ConsultationQuotaExceededError,
    ThematicConsultationEntitlementGate,
)


@pytest.fixture
def mock_user():
    return MagicMock(id=42, email="user@example.com")


def make_entitlement(**kwargs) -> FeatureEntitlement:
    defaults = dict(
        plan_code="basic",
        billing_status="active",
        is_enabled_by_plan=True,
        access_mode="quota",
        variant_code=None,
        quotas=[
            QuotaDefinition(
                quota_key="consultations",
                quota_limit=1,
                period_unit="week",
                period_value=1,
                reset_mode="calendar",
            )
        ],
        final_access=True,
        reason="canonical_binding",
        usage_states=[
            UsageState(
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
        ],
        quota_exhausted=False,
    )
    return FeatureEntitlement(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    entitlement = make_entitlement()
    mock_state = MagicMock(used=1, remaining=0)

    with (
        patch(
            "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume",
            return_value=mock_state,
        ) as mock_consume,
    ):
        result = ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_quota"
    assert result.usage_states == [mock_state]
    mock_consume.assert_called_once()


def test_canonical_unlimited_path_no_consume(db_session):
    entitlement = make_entitlement(access_mode="unlimited", quotas=[])

    with (
        patch(
            "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume"
        ) as mock_consume,
    ):
        result = ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_unlimited"
    mock_consume.assert_not_called()


def test_legacy_fallback_treated_as_no_binding(db_session):
    entitlement = make_entitlement(reason="legacy_fallback", final_access=False)
    with patch(
        "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "canonical_no_binding"


def test_access_denied_no_plan(db_session):
    entitlement = make_entitlement(
        final_access=False, reason="no_plan", plan_code="", billing_status="none"
    )
    with patch(
        "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "no_plan"


def test_access_denied_billing_inactive(db_session):
    entitlement = make_entitlement(
        final_access=False, reason="billing_inactive", billing_status="past_due"
    )
    with patch(
        "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "billing_inactive"


def test_canonical_disabled_binding_rejected_403(db_session):
    entitlement = make_entitlement(final_access=False, reason="disabled_by_plan")
    with patch(
        "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(ConsultationAccessDeniedError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "disabled_by_plan"


def test_quota_exceeded_raises_consultation_error(db_session):
    entitlement = make_entitlement()
    with (
        patch(
            "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume",
            side_effect=QuotaExhaustedError(
                quota_key="consultations", used=1, limit=1, feature_code="thematic_consultation"
            ),
        ),
    ):
        with pytest.raises(ConsultationQuotaExceededError) as exc_info:
            ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.quota_key == "consultations"
    assert exc_info.value.used == 1
    assert exc_info.value.limit == 1


def test_no_legacy_quota_service_called(db_session):
    entitlement = make_entitlement()
    with (
        patch(
            "app.services.thematic_consultation_entitlement_gate.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.thematic_consultation_entitlement_gate.QuotaUsageService.consume",
            return_value=MagicMock(),
        ),
        patch("app.services.quota_service.QuotaService.consume_quota_or_raise") as legacy_consume,
    ):
        ThematicConsultationEntitlementGate.check_and_consume(db_session, user_id=42)

    legacy_consume.assert_not_called()

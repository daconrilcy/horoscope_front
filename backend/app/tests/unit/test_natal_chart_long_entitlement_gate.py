from unittest.mock import MagicMock, patch

import pytest

from app.services.entitlement_types import FeatureEntitlement, QuotaDefinition
from app.services.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementGate,
    NatalChartLongQuotaExceededError,
)


def make_entitlement(**kwargs) -> FeatureEntitlement:
    defaults = dict(
        plan_code="trial",
        billing_status="active",
        is_enabled_by_plan=True,
        access_mode="quota",
        variant_code="single_astrologer",
        quotas=[
            QuotaDefinition(
                quota_key="interpretations",
                quota_limit=1,
                period_unit="lifetime",
                period_value=1,
                reset_mode="lifetime",
            )
        ],
        final_access=True,
        reason="canonical_binding",
        usage_states=[],
        quota_exhausted=False,
    )
    return FeatureEntitlement(**{**defaults, **kwargs})


def test_canonical_quota_path_consumes(db_session):
    entitlement = make_entitlement()
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)
    # Re-mocking as real object to avoid issues with dataclass/attribute access if needed
    mock_state.quota_key = "interpretations"

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
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
    entitlement = make_entitlement(access_mode="unlimited")

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch("app.services.quota_usage_service.QuotaUsageService.consume") as mock_consume,
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.path == "canonical_unlimited"
    assert result.variant_code == "single_astrologer"
    mock_consume.assert_not_called()


def test_variant_code_single_astrologer(db_session):
    entitlement = make_entitlement(variant_code="single_astrologer")
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ),
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.variant_code == "single_astrologer"


def test_variant_code_multi_astrologer(db_session):
    entitlement = make_entitlement(variant_code="multi_astrologer")
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ),
    ):
        result = NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    assert result.variant_code == "multi_astrologer"


def test_access_denied_no_plan(db_session):
    entitlement = make_entitlement(final_access=False, reason="no_plan")
    with patch(
        "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(NatalChartLongAccessDeniedError) as exc_info:
            NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "no_plan"


def test_access_denied_disabled_by_plan(db_session):
    entitlement = make_entitlement(final_access=False, reason="disabled_by_plan")
    with patch(
        "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
        return_value=entitlement,
    ):
        with pytest.raises(NatalChartLongAccessDeniedError) as exc_info:
            NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)
    assert exc_info.value.reason == "disabled_by_plan"


def test_quota_exceeded_raises_natal_error(db_session):
    from app.services.quota_usage_service import QuotaExhaustedError

    entitlement = make_entitlement()

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
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


def test_no_legacy_quota_service_called(db_session):
    # Vérifie indirectement que seul le chemin canonique est utilisé.
    entitlement = make_entitlement()
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)

    with (
        patch(
            "app.services.entitlement_service.EntitlementService.get_feature_entitlement",
            return_value=entitlement,
        ),
        patch(
            "app.services.quota_usage_service.QuotaUsageService.consume", return_value=mock_state
        ),
        patch("app.services.quota_service.QuotaService") as mock_legacy_quota,
    ):
        NatalChartLongEntitlementGate.check_and_consume(db_session, user_id=42)

    mock_legacy_quota.assert_not_called()

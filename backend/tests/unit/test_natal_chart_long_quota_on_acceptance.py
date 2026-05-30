# Commentaire global: tests du quota natal long apres acceptation et regeneration corrective.
"""Verifie que le quota natal long n'est pas debite avant une lecture complete valide."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementGate,
    NatalChartLongEntitlementResult,
    NatalChartLongQuotaExceededError,
)


def _snapshot(**access_kwargs: object) -> EffectiveEntitlementsSnapshot:
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
    access_data = {**access_defaults, **access_kwargs}
    access = EffectiveFeatureAccess(**access_data)
    return EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code="trial",
        billing_status="active",
        entitlements={"natal_chart_long": access},
    )


def test_consume_on_acceptance_defers_quota_until_success() -> None:
    mock_state = MagicMock(used=1, remaining=0, quota_limit=1, window_end=None)
    mock_state.quota_key = "interpretations"
    mock_state.period_unit = "lifetime"
    mock_state.period_value = 1
    mock_state.reset_mode = "lifetime"
    access_result = NatalChartLongEntitlementResult(
        path="canonical_quota",
        variant_code="single_astrologer",
        usage_states=[mock_state],
    )

    with patch(
        "app.services.quota.usage_service.QuotaUsageService.consume",
        return_value=mock_state,
    ) as mock_consume:
        result = NatalChartLongEntitlementGate.consume_on_acceptance(
            MagicMock(),
            user_id=42,
            access_result=access_result,
        )

    assert result.path == "canonical_quota"
    mock_consume.assert_called_once()


def test_consume_on_acceptance_skips_corrective_regeneration() -> None:
    access_result = NatalChartLongEntitlementResult(
        path="corrective_regeneration",
        variant_code="single_astrologer",
        corrective_regeneration=True,
    )

    with patch("app.services.quota.usage_service.QuotaUsageService.consume") as mock_consume:
        result = NatalChartLongEntitlementGate.consume_on_acceptance(
            MagicMock(),
            user_id=42,
            access_result=access_result,
        )

    assert result.corrective_regeneration is True
    mock_consume.assert_not_called()


def test_check_access_for_complete_generation_allows_corrective_regeneration() -> None:
    exhausted_access = EffectiveFeatureAccess(
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
        subject_id=42,
        plan_code="trial",
        billing_status="active",
        entitlements={"natal_chart_long": exhausted_access},
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.claim_corrective_regeneration_eligibility",
            return_value=(123, "natal_interpretation"),
        ),
    ):
        result = NatalChartLongEntitlementGate.check_access_for_complete_generation(
            MagicMock(),
            user_id=42,
        )

    assert result.path == "corrective_regeneration"
    assert result.corrective_regeneration is True
    assert result.corrective_interpretation_id == 123


def test_check_access_for_complete_generation_raises_when_not_corrective() -> None:
    exhausted_access = EffectiveFeatureAccess(
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
        subject_id=42,
        plan_code="trial",
        billing_status="active",
        entitlements={"natal_chart_long": exhausted_access},
    )

    with (
        patch.object(
            EffectiveEntitlementResolverService,
            "resolve_b2c_user_snapshot",
            return_value=snapshot,
        ),
        patch(
            "app.services.llm_generation.natal.interpretation_service.NatalInterpretationService.claim_corrective_regeneration_eligibility",
            return_value=None,
        ),
    ):
        with pytest.raises(NatalChartLongQuotaExceededError):
            NatalChartLongEntitlementGate.check_access_for_complete_generation(
                MagicMock(),
                user_id=42,
            )

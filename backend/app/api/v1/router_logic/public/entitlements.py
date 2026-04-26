"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.schemas.entitlements import (
    FeatureEntitlementResponse,
    UsageStateResponse,
)
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel,
)
from app.services.entitlement.entitlement_types import EffectiveFeatureAccess, UsageState

router = APIRouter(prefix="/v1/entitlements", tags=["entitlements"])
FEATURES_TO_QUERY: list[str] = [
    "astrologer_chat",
    "thematic_consultation",
    "natal_chart_long",
    "natal_chart_short",
    "horoscope_daily",
]
_PLAN_PRIORITY: dict[str, str] = {
    "free": "low",
    "basic": "medium",
    "premium": "high",
}


def _to_usage_state_response(state: UsageState) -> UsageStateResponse:
    return UsageStateResponse(
        quota_key=state.quota_key,
        quota_limit=state.quota_limit,
        used=state.used,
        remaining=state.remaining,
        exhausted=state.exhausted,
        period_unit=state.period_unit,
        period_value=state.period_value,
        reset_mode=state.reset_mode,
        window_start=state.window_start,
        window_end=state.window_end,
    )


def _to_feature_response(
    feature_code: str, access: EffectiveFeatureAccess
) -> FeatureEntitlementResponse:
    period_order = {"day": 0, "week": 1, "month": 2, "year": 3, "lifetime": 4}
    ordered_usage_states = sorted(
        access.usage_states,
        key=lambda state: (
            period_order.get(state.period_unit, 99),
            state.period_value,
            state.quota_key,
        ),
    )
    return FeatureEntitlementResponse(
        feature_code=feature_code,
        granted=access.granted,
        reason_code=access.reason_code,
        access_mode=access.access_mode,
        quota_remaining=access.quota_remaining,
        quota_limit=access.quota_limit,
        variant_code=access.variant_code,
        usage_states=[_to_usage_state_response(s) for s in ordered_usage_states],
    )


def _missing_feature_response(feature_code: str) -> FeatureEntitlementResponse:
    # Preserve the frontend contract even if a future resolver regression omits a priority feature.
    return FeatureEntitlementResponse(
        feature_code=feature_code,
        granted=False,
        reason_code="feature_not_in_plan",
        access_mode=None,
        quota_remaining=None,
        quota_limit=None,
        variant_code=None,
        usage_states=[],
    )


def _get_available_feature_codes(db: Session) -> list[str]:
    try:
        existing_codes = set(
            db.scalars(
                select(FeatureCatalogModel.feature_code).where(
                    FeatureCatalogModel.is_active,
                    FeatureCatalogModel.feature_code.in_(FEATURES_TO_QUERY),
                )
            ).all()
        )
    except SQLAlchemyError:
        return FEATURES_TO_QUERY

    if not existing_codes:
        return FEATURES_TO_QUERY
    return [feature_code for feature_code in FEATURES_TO_QUERY if feature_code in existing_codes]

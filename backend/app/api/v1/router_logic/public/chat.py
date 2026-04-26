"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.services.entitlement.chat_entitlement_gate import (
    ChatEntitlementGate,
    ChatEntitlementResult,
)
from app.services.entitlement.entitlement_types import QuotaDefinition
from app.services.quota.usage_service import QuotaUsageService

logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.public.chat import QuotaInfo


def _build_quota_info(result: ChatEntitlementResult) -> QuotaInfo:
    if result.path in ("canonical_quota", "canonical_unlimited") and result.usage_states:
        state = result.usage_states[0]
        return QuotaInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,
        )
    return QuotaInfo()


def _build_post_turn_quota_info(
    db: Session,
    *,
    user_id: int,
    result: ChatEntitlementResult,
) -> QuotaInfo:
    if result.path != "canonical_quota" or not result.usage_states:
        return QuotaInfo()

    state = result.usage_states[0]
    refreshed_state = QuotaUsageService.get_usage(
        db,
        user_id=user_id,
        feature_code=ChatEntitlementGate.FEATURE_CODE,
        quota=QuotaDefinition(
            quota_key=state.quota_key,
            quota_limit=state.quota_limit,
            period_unit=state.period_unit,
            period_value=state.period_value,
            reset_mode=state.reset_mode,
        ),
    )
    return QuotaInfo(
        remaining=refreshed_state.remaining,
        limit=refreshed_state.quota_limit,
        window_end=refreshed_state.window_end,
    )

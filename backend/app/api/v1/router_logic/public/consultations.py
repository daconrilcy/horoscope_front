"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.schemas.consultation import (
    ConsultationQuotaInfo,
)
from app.services.entitlement.thematic_consultation_entitlement_gate import (
    ConsultationEntitlementResult,
)

router = APIRouter()


def _build_consultation_quota_info(result: ConsultationEntitlementResult) -> ConsultationQuotaInfo:
    """
    Construit les informations de quota pour la réponse.
    thematic_consultation a un seul quota par plan (quota_key="consultations").
    """
    if result.path in ("canonical_quota", "canonical_unlimited") and result.usage_states:
        state = result.usage_states[0]
        return ConsultationQuotaInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,
        )
    return ConsultationQuotaInfo()

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.schemas.entitlements import (
    EntitlementsMeResponse,
    FeatureEntitlementResponse,
    UsageStateResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import FeatureEntitlement, UsageState

router = APIRouter(prefix="/v1/entitlements", tags=["entitlements"])

# Liste fixe des 4 features — toujours retournées, quel que soit l'état du binding
FEATURES_TO_QUERY: list[str] = [
    "astrologer_chat",
    "thematic_consultation",
    "natal_chart_long",
    "natal_chart_short",
]


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
    feature_code: str, entitlement: FeatureEntitlement
) -> FeatureEntitlementResponse:
    return FeatureEntitlementResponse(
        feature_code=feature_code,
        plan_code=entitlement.plan_code,
        billing_status=entitlement.billing_status,
        access_mode=entitlement.access_mode,
        final_access=entitlement.final_access,
        reason=entitlement.reason,
        variant_code=entitlement.variant_code,
        usage_states=[_to_usage_state_response(s) for s in entitlement.usage_states],
    )


@router.get(
    "/me",
    response_model=EntitlementsMeResponse,
    responses={401: {}, 403: {}},
)
def get_my_entitlements(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"user", "admin"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role not allowed for entitlements",
                    "details": {"role": current_user.role},
                    "request_id": request_id,
                }
            },
        )

    # Lecture pure — EntitlementService appelle QuotaUsageService.get_usage() (lecture)
    # mais JAMAIS QuotaUsageService.consume() — aucune écriture dans feature_usage_counters
    features: list[FeatureEntitlementResponse] = []
    for feature_code in FEATURES_TO_QUERY:
        entitlement = EntitlementService.get_feature_entitlement(
            db, user_id=current_user.id, feature_code=feature_code
        )
        features.append(_to_feature_response(feature_code, entitlement))

    return {
        "data": {"features": features},
        "meta": {"request_id": request_id},
    }

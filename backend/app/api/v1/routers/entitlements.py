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
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import EffectiveFeatureAccess, UsageState

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
    feature_code: str, access: EffectiveFeatureAccess
) -> FeatureEntitlementResponse:
    return FeatureEntitlementResponse(
        feature_code=feature_code,
        granted=access.granted,
        reason_code=access.reason_code,
        access_mode=access.access_mode,
        quota_remaining=access.quota_remaining,
        quota_limit=access.quota_limit,
        variant_code=access.variant_code,
        usage_states=[_to_usage_state_response(s) for s in access.usage_states],
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
    """
    Expose l'état d'accès complet pour l'utilisateur courant (B2C).

    AC4 - Mapping reason_code -> action UX recommandé :
    - granted (true)          -> CTA actif, afficher quota restant
    - feature_not_in_plan (false) -> Désactiver CTA, afficher badge "upgrade"
    - billing_inactive (false)    -> Désactiver CTA, afficher lien renouvellement
    - quota_exhausted (false)     -> Désactiver CTA, afficher quota 0 / limit
    - binding_disabled (false)    -> Désactiver CTA, pas d'upgrade possible
    - subject_not_eligible (false)-> Désactiver CTA, message générique
    """
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

    # AC5 - Appel unique au resolver effectif (livré en story 61.47)
    snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
        db, app_user_id=current_user.id
    )

    # AC2 - Toujours exposer les 4 features prioritaires dans l'ordre attendu par le frontend.
    features = [
        _to_feature_response(fc, snapshot.entitlements[fc])
        if fc in snapshot.entitlements
        else _missing_feature_response(fc)
        for fc in FEATURES_TO_QUERY
    ]

    # AC1 - plan_code et billing_status au top-level
    return {
        "data": {
            "plan_code": snapshot.plan_code,
            "billing_status": snapshot.billing_status,
            "features": features,
        },
        "meta": {"request_id": request_id},
    }

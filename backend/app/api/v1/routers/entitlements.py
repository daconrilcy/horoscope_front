from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.schemas.entitlements import (
    EntitlementsMeResponse,
    FeatureEntitlementResponse,
    PlanCatalogData,
    PlanFeatureData,
    PlanFeatureQuotaData,
    PlansCatalogResponse,
    UsageStateResponse,
)
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.product_entitlements import (
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
)
from app.infra.db.session import get_db_session
from app.services.billing_service import BillingService
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import EffectiveFeatureAccess, UsageState

router = APIRouter(prefix="/v1/entitlements", tags=["entitlements"])

# Liste fixe des features — toujours retournées, quel que soit l'état du binding
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
# fallback : "medium"


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

    # Story 64.4 - Calcul des hints d'upgrade
    hints = EffectiveEntitlementResolverService.compute_upgrade_hints(snapshot, db)

    # AC2 - Toujours exposer les features prioritaires dans l'ordre attendu par le frontend.
    available_feature_codes = _get_available_feature_codes(db)
    features = [
        _to_feature_response(feature_code, snapshot.entitlements[feature_code])
        if feature_code in snapshot.entitlements
        else _missing_feature_response(feature_code)
        for feature_code in available_feature_codes
    ]

    # AC1 - plan_code et billing_status au top-level
    return {
        "data": {
            "plan_code": snapshot.plan_code,
            "billing_status": snapshot.billing_status,
            "features": features,
            "upgrade_hints": hints,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/plans",
    response_model=PlansCatalogResponse,
    responses={401: {}, 403: {}},
)
def get_plans_catalog(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Expose le catalogue des plans B2C (AC1).
    Utilisé par la page /help/subscriptions.
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

    BillingService.ensure_default_plans(db)

    # 1. Charger les plans B2C actifs avec leurs bindings, features et quotas (anti N+1)
    stmt = (
        select(PlanCatalogModel)
        .where(
            PlanCatalogModel.audience == Audience.B2C,
            PlanCatalogModel.is_active,
        )
        .options(
            selectinload(PlanCatalogModel.bindings).selectinload(PlanFeatureBindingModel.feature),
            selectinload(PlanCatalogModel.bindings).selectinload(PlanFeatureBindingModel.quotas),
        )
    )
    plans = db.scalars(stmt).all()

    # 2. Charger les prix depuis billing_plans
    billing_plans = db.scalars(select(BillingPlanModel).where(BillingPlanModel.is_active)).all()
    price_map = {bp.code: bp for bp in billing_plans}

    # 3. Ordonner les plans : free, basic, premium
    plan_order = {"free": 0, "basic": 1, "premium": 2}
    sorted_plans = sorted(plans, key=lambda p: plan_order.get(p.plan_code, 99))

    # 4. Charger toutes les features du catalogue pour garantir l'exhaustivité (AC1)
    feature_order = {
        "natal_chart_short": 0,
        "natal_chart_long": 1,
        "astrologer_chat": 2,
        "thematic_consultation": 3,
        "horoscope_daily": 4,
    }
    all_features = db.scalars(
        select(FeatureCatalogModel).where(
            FeatureCatalogModel.feature_code.in_(feature_order.keys())
        )
    ).all()
    feature_map = {f.feature_code: f for f in all_features}

    data = []
    for plan in sorted_plans:
        bp = price_map.get(plan.plan_code)
        if plan.plan_code != "free":
            if bp is None or not bp.is_visible_to_users:
                continue
        monthly_price_cents = bp.monthly_price_cents if bp else 0
        currency = bp.currency if bp else "EUR"
        is_plan_active = bp.is_available_to_users if bp else plan.is_active

        # Map des bindings existants pour ce plan
        plan_bindings = {b.feature.feature_code: b for b in plan.bindings}

        features_data = []
        # On itère sur l'ordre imposé des features
        for f_code in sorted(feature_order.keys(), key=lambda k: feature_order[k]):
            b = plan_bindings.get(f_code)
            feature_ref = feature_map.get(f_code)

            if not feature_ref:
                # Si la feature n'existe pas en base, on skip (cas rare si seeds OK)
                continue

            if b:
                period_order = {"day": 0, "week": 1, "month": 2, "year": 3, "lifetime": 4}
                quotas_data = [
                    PlanFeatureQuotaData(
                        quota_key=q.quota_key,
                        quota_limit=q.quota_limit,
                        period_unit=q.period_unit.value,
                        period_value=q.period_value,
                        reset_mode=q.reset_mode.value,
                    )
                    for q in sorted(
                        b.quotas,
                        key=lambda quota: (
                            period_order.get(quota.period_unit.value, 99),
                            quota.period_value,
                            quota.quota_key,
                        ),
                    )
                ]
                features_data.append(
                    PlanFeatureData(
                        feature_code=b.feature.feature_code,
                        feature_name=b.feature.feature_name,
                        is_enabled=b.is_enabled,
                        access_mode=b.access_mode.value,
                        quotas=quotas_data,
                    )
                )
            else:
                # Pas de binding = feature non incluse / désactivée pour ce plan
                features_data.append(
                    PlanFeatureData(
                        feature_code=f_code,
                        feature_name=feature_ref.feature_name,
                        is_enabled=False,
                        access_mode="disabled",
                        quotas=[],
                    )
                )

        data.append(
            PlanCatalogData(
                plan_code=plan.plan_code,
                plan_name=plan.plan_name,
                monthly_price_cents=monthly_price_cents,
                currency=currency,
                is_active=is_plan_active,
                processing_priority=_PLAN_PRIORITY.get(plan.plan_code, "medium"),
                features=features_data,
            )
        )

    return {
        "data": data,
        "meta": {"request_id": request_id},
    }

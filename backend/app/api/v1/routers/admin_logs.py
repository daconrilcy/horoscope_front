from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.admin_logs import (
    AdminAppErrorsResponse,
    AdminQuotaAlertsResponse,
    AdminStripeEventsResponse,
)
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.stripe_webhook_event import StripeWebhookEventModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/logs", tags=["admin-logs"])


@router.get("/errors", response_model=AdminAppErrorsResponse)
def get_app_errors(
    request: Request,
    limit: int = Query(default=50, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get application errors from audit logs.
    """
    stmt = (
        select(AuditEventModel)
        .where(AuditEventModel.status == "error")
        .order_by(AuditEventModel.created_at.desc())
        .limit(limit)
    )
    results = db.scalars(stmt).all()

    data = [
        {
            "id": result.id,
            "timestamp": result.created_at,
            "request_id": result.request_id,
            "action": result.action,
            "status": result.status,
            "details": result.details,
        }
        for result in results
    ]

    return {"data": data, "total": len(data)}


@router.get("/stripe", response_model=AdminStripeEventsResponse)
def get_stripe_events(
    request: Request,
    status: str | None = Query(default=None),
    limit: int = Query(default=50, le=100),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get Stripe webhook events history.
    """
    stmt = select(StripeWebhookEventModel).order_by(StripeWebhookEventModel.received_at.desc())
    if status:
        stmt = stmt.where(StripeWebhookEventModel.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    results = db.scalars(stmt.limit(limit)).all()

    return {"data": results, "total": total or 0}


def _mask_email(email: str) -> str:
    local_part, separator, domain = email.partition("@")
    if not separator:
        return email

    visible_prefix = local_part[:3]
    return f"{visible_prefix}***@{domain}"


@router.get("/quota-alerts", response_model=AdminQuotaAlertsResponse)
def get_quota_alerts(
    request: Request,
    threshold: float = Query(default=0.9, ge=0, le=1),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Find users who consumed more than ``threshold`` of a configured quota.
    """
    quota_stmt = (
        select(
            UserModel.id.label("user_id"),
            UserModel.email,
            FeatureUsageCounterModel.feature_code,
            FeatureUsageCounterModel.used_count,
            PlanCatalogModel.plan_code,
            PlanFeatureQuotaModel.quota_limit,
        )
        .join(FeatureUsageCounterModel, FeatureUsageCounterModel.user_id == UserModel.id)
        .outerjoin(
            StripeBillingProfileModel,
            StripeBillingProfileModel.user_id == UserModel.id,
        )
        .outerjoin(
            PlanCatalogModel,
            PlanCatalogModel.plan_code
            == func.coalesce(StripeBillingProfileModel.entitlement_plan, "free"),
        )
        .outerjoin(
            FeatureCatalogModel,
            FeatureCatalogModel.feature_code == FeatureUsageCounterModel.feature_code,
        )
        .outerjoin(
            PlanFeatureBindingModel,
            (PlanFeatureBindingModel.plan_id == PlanCatalogModel.id)
            & (PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id),
        )
        .outerjoin(
            PlanFeatureQuotaModel,
            (PlanFeatureQuotaModel.plan_feature_binding_id == PlanFeatureBindingModel.id)
            & (PlanFeatureQuotaModel.quota_key == FeatureUsageCounterModel.quota_key)
            & (PlanFeatureQuotaModel.period_unit == FeatureUsageCounterModel.period_unit)
            & (PlanFeatureQuotaModel.period_value == FeatureUsageCounterModel.period_value)
            & (PlanFeatureQuotaModel.reset_mode == FeatureUsageCounterModel.reset_mode),
        )
        .where(FeatureUsageCounterModel.used_count > 0)
        .order_by(FeatureUsageCounterModel.used_count.desc(), UserModel.id.desc())
        .limit(100)
    )
    results = db.execute(quota_stmt).all()

    alerts: list[dict[str, Any]] = []
    for result in results:
        quota_limit = result.quota_limit
        if quota_limit is None or quota_limit <= 0:
            continue

        consumption_rate = float(result.used_count / quota_limit)
        if consumption_rate < threshold:
            continue

        alerts.append(
            {
                "user_id": result.user_id,
                "user_email_masked": _mask_email(result.email),
                "plan_code": result.plan_code or "free",
                "feature_code": result.feature_code,
                "used": result.used_count,
                "limit": quota_limit,
                "consumption_rate": consumption_rate,
            }
        )

    return {"data": alerts}

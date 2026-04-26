from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.ops.admin_dashboard import (
    _apply_user_plan_filter,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/admin/dashboard", tags=["admin-dashboard"])


@router.get("/kpis-snapshot")
def get_kpis_snapshot(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get instantaneous KPIs for the admin dashboard.
    Covers total users, active users (7d/30d), MRR, and trials.
    """
    request_id = resolve_request_id(request)
    now = datetime_provider.utcnow()

    try:
        # 1. Inscrits totaux
        total_users = db.scalar(select(func.count(UserModel.id)))

        # 2. Utilisateurs actifs (ayant eu une génération dans les 7j / 30j)
        active_7j = (
            db.scalar(
                select(func.count(func.distinct(UserTokenUsageLogModel.user_id))).where(
                    UserTokenUsageLogModel.created_at >= now - timedelta(days=7)
                )
            )
            or 0
        )

        active_30j = (
            db.scalar(
                select(func.count(func.distinct(UserTokenUsageLogModel.user_id))).where(
                    UserTokenUsageLogModel.created_at >= now - timedelta(days=30)
                )
            )
            or 0
        )

        # 3. Abonnements actifs par plan
        sub_stmt = (
            select(BillingPlanModel.code, func.count(UserSubscriptionModel.id))
            .join(UserSubscriptionModel, UserSubscriptionModel.plan_id == BillingPlanModel.id)
            .where(UserSubscriptionModel.status == "active")
            .group_by(BillingPlanModel.code)
        )
        subscriptions_by_plan_rows = db.execute(sub_stmt).all()
        subscriptions_by_plan = {code: count for code, count in subscriptions_by_plan_rows}

        # 4. MRR estimé (uniquement sur les abonnements 'active')
        mrr_stmt = (
            select(func.sum(BillingPlanModel.monthly_price_cents))
            .join(UserSubscriptionModel, UserSubscriptionModel.plan_id == BillingPlanModel.id)
            .where(UserSubscriptionModel.status == "active")
        )
        mrr_cents = db.scalar(mrr_stmt) or 0

        # 5. Essais en cours
        trials_count = (
            db.scalar(
                select(func.count(UserSubscriptionModel.id)).where(
                    UserSubscriptionModel.status == "trial"
                )
            )
            or 0
        )

        return {
            "data": {
                "total_users": total_users,
                "active_users_7j": active_7j,
                "active_users_30j": active_30j,
                "subscriptions_by_plan": subscriptions_by_plan,
                "mrr_cents": mrr_cents,
                "arr_cents": mrr_cents * 12,
                "trials_count": trials_count,
                "last_updated": now.isoformat(),
            },
            "meta": {"request_id": request_id},
        }

    except Exception as e:
        logger.error("admin_dashboard_kpis_snapshot_failed error=%s", e)
        raise


@router.get("/kpis-flux")
def get_kpis_flux(
    request: Request,
    period: str = Query(default="30d"),
    plan: str = Query(default="all"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get flow KPIs (new users, churn, revenue) for a given period and plan segment.
    """
    request_id = resolve_request_id(request)
    now = datetime_provider.utcnow()

    # 1. Period calculation
    if period == "7d":
        start_date = now - timedelta(days=7)
        granularity = "day"
    elif period == "30d":
        start_date = now - timedelta(days=30)
        granularity = "day"
    elif period == "12m":
        start_date = now - timedelta(days=365)
        granularity = "week"
    else:
        start_date = now - timedelta(days=30)
        granularity = "day"

    # 2. Plan filter
    plan_filter = None if plan == "all" else plan

    try:
        # 3. New registered users
        new_users_stmt = select(func.count(func.distinct(UserModel.id))).where(
            UserModel.created_at >= start_date
        )
        new_users_stmt = _apply_user_plan_filter(new_users_stmt, plan_filter)
        new_users_count = db.scalar(new_users_stmt) or 0

        # 4. Churn (canceled/unpaid profiles updated in the period)
        churn_stmt = select(func.count(StripeBillingProfileModel.id)).where(
            StripeBillingProfileModel.subscription_status.in_(["canceled", "unpaid"]),
            StripeBillingProfileModel.updated_at >= start_date,
        )
        if plan_filter:
            churn_stmt = churn_stmt.where(StripeBillingProfileModel.entitlement_plan == plan_filter)
        churn_count = db.scalar(churn_stmt) or 0

        # 5. Payment failures (via UserSubscription fallback table which records reason)
        payment_failures_stmt = select(func.count(UserSubscriptionModel.id)).where(
            UserSubscriptionModel.failure_reason.is_not(None),
            UserSubscriptionModel.updated_at >= start_date,
        )
        if plan_filter:
            payment_failures_stmt = payment_failures_stmt.join(
                BillingPlanModel, BillingPlanModel.id == UserSubscriptionModel.plan_id
            ).where(BillingPlanModel.code == plan_filter)
        payment_failures_count = db.scalar(payment_failures_stmt) or 0

        # 6. Estimated Revenue (sum of active plans)
        revenue_stmt = (
            select(func.sum(BillingPlanModel.monthly_price_cents))
            .join(
                StripeBillingProfileModel,
                StripeBillingProfileModel.entitlement_plan == BillingPlanModel.code,
            )
            .where(StripeBillingProfileModel.subscription_status == "active")
        )
        if plan_filter:
            revenue_stmt = revenue_stmt.where(BillingPlanModel.code == plan_filter)
        revenue_cents = db.scalar(revenue_stmt) or 0

        # 7. Trend Data
        if granularity == "day":
            date_func = func.date(UserModel.created_at)
        else:  # week
            date_func = func.strftime("%Y-W%W", UserModel.created_at)

        trend_stmt = (
            select(date_func, func.count(func.distinct(UserModel.id)))
            .where(UserModel.created_at >= start_date)
            .group_by(date_func)
            .order_by(date_func)
        )
        trend_stmt = _apply_user_plan_filter(trend_stmt, plan_filter)

        trend_rows = db.execute(trend_stmt).all()
        trend_data = [{"date": str(row[0]), "new_users": row[1]} for row in trend_rows]

        return {
            "data": {
                "period": period,
                "plan": plan,
                "new_users": new_users_count,
                "churn_count": churn_count,
                "upgrades_count": 0,
                "downgrades_count": 0,
                "payment_failures_count": payment_failures_count,
                "revenue_cents": revenue_cents,
                "trend_data": trend_data,
                "last_updated": now.isoformat(),
            },
            "meta": {"request_id": request_id},
        }

    except Exception as e:
        logger.error("admin_dashboard_kpis_flux_failed error=%s", e)
        raise


@router.get("/kpis-billing")
def get_kpis_billing(
    request: Request,
    period: str = Query(default="30d"),
    plan: str = Query(default="all"),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """
    Get billing health KPIs (payment failures, estimated revenue) for a given period and plan.
    """
    request_id = resolve_request_id(request)
    now = datetime_provider.utcnow()

    # 1. Period calculation
    if period == "7d":
        days = 7
    elif period == "12m":
        days = 365
    else:
        days = 30
    start_date = now - timedelta(days=days)

    plan_filter = None if plan == "all" else plan

    try:
        # 2. Payment failures
        failures_stmt = select(func.count(UserSubscriptionModel.id)).where(
            UserSubscriptionModel.failure_reason.is_not(None),
            UserSubscriptionModel.updated_at >= start_date,
        )
        if plan_filter:
            failures_stmt = failures_stmt.join(
                BillingPlanModel, BillingPlanModel.id == UserSubscriptionModel.plan_id
            ).where(BillingPlanModel.code == plan_filter)
        payment_failures = db.scalar(failures_stmt) or 0

        # 3. Revenue by plan (Current Active base applied to period)
        revenue_stmt = (
            select(
                BillingPlanModel.code,
                func.count(StripeBillingProfileModel.id),
                func.sum(BillingPlanModel.monthly_price_cents),
            )
            .join(
                StripeBillingProfileModel,
                StripeBillingProfileModel.entitlement_plan == BillingPlanModel.code,
            )
            .where(StripeBillingProfileModel.subscription_status == "active")
            .group_by(BillingPlanModel.code)
        )
        if plan_filter:
            revenue_stmt = revenue_stmt.where(BillingPlanModel.code == plan_filter)

        revenue_rows = db.execute(revenue_stmt).all()

        revenue_by_plan = []
        total_mrr_cents = 0
        for row in revenue_rows:
            p_code, count, mrr = row
            total_mrr_cents += mrr
            revenue_by_plan.append(
                {
                    "plan_code": p_code,
                    "count": count,
                    "mrr_cents": mrr,
                    "estimated_period_revenue_cents": int(mrr * (days / 30)),
                }
            )

        return {
            "data": {
                "period": period,
                "plan": plan,
                "payment_failures": payment_failures,
                "estimated_total_revenue_cents": int(total_mrr_cents * (days / 30)),
                "revenue_by_plan": revenue_by_plan,
                "last_updated": now.isoformat(),
            },
            "meta": {"request_id": request_id},
        }

    except Exception as e:
        logger.error("admin_dashboard_kpis_billing_failed error=%s", e)
        raise

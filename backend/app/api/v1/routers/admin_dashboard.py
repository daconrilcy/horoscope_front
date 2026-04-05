from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.request_id import resolve_request_id
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session

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
    now = datetime.now(UTC)

    try:
        # 1. Inscrits totaux
        total_users = db.scalar(select(func.count(UserModel.id)))

        # 2. Utilisateurs actifs (ayant eu une génération dans les 7j / 30j)
        active_7j = db.scalar(
            select(func.count(func.distinct(UserTokenUsageLogModel.user_id))).where(
                UserTokenUsageLogModel.created_at >= now - timedelta(days=7)
            )
        ) or 0
        
        active_30j = db.scalar(
            select(func.count(func.distinct(UserTokenUsageLogModel.user_id))).where(
                UserTokenUsageLogModel.created_at >= now - timedelta(days=30)
            )
        ) or 0

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
        trials_count = db.scalar(
            select(func.count(UserSubscriptionModel.id)).where(
                UserSubscriptionModel.status == "trial"
            )
        ) or 0

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
        # We don't want to break the whole dashboard if one KPI fails, 
        # but here it's a single endpoint.
        raise

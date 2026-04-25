"""Expose la facade canonique du domaine billing."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.token_usage_log import UserTokenUsageLogModel
from app.services.billing.models import (
    BASIC_PLAN_CODE,
    FREE_PLAN_CODE,
    PLAN_CODE_TO_STRIPE_ENTITLEMENT,
    PREMIUM_PLAN_CODE,
    STRIPE_ENTITLEMENT_TO_PLAN_CODE,
    BillingPlanData,
    BillingServiceError,
    SubscriptionStatusData,
    TokenUsageData,
    TokenUsageFeatureSummary,
    TokenUsagePeriod,
    TokenUsageSummary,
)
from app.services.billing.plan_catalog import ensure_default_plans
from app.services.billing.subscription_cache import (
    invalidate_cached_subscription_status,
    reset_subscription_status_cache,
)
from app.services.billing.subscription_status import (
    get_subscription_status,
    resolve_runtime_billing_status,
    resolve_runtime_plan_code,
)


class BillingService:
    """Facade fine d orchestration pour le domaine billing."""

    BILLING_QUOTA_FEATURE = "astrologer_chat"

    @staticmethod
    def get_token_usage(
        db: Session, *, user_id: int, period: str = "current_month"
    ) -> TokenUsageData:
        """Calcule l usage tokens agrege pour un utilisateur."""
        now = datetime_provider.utcnow()
        window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        window_end = window_start + timedelta(days=1)
        unit = "day"

        if period == "current_month":
            window_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            window_end = (
                now.replace(year=now.year + 1, month=1, day=1)
                if now.month == 12
                else now.replace(month=now.month + 1, day=1)
            )
            unit = "month"
        elif period == "current_week":
            window_start = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            window_end = window_start + timedelta(days=7)
            unit = "week"
        elif period == "all":
            first_log_dt = db.scalar(
                select(func.min(UserTokenUsageLogModel.created_at)).where(
                    UserTokenUsageLogModel.user_id == user_id
                )
            )
            window_start = first_log_dt or now
            window_end = now
            unit = "all"

        totals = db.execute(
            select(
                func.sum(UserTokenUsageLogModel.tokens_total).label("total_sum"),
                func.sum(UserTokenUsageLogModel.tokens_in).label("in_sum"),
                func.sum(UserTokenUsageLogModel.tokens_out).label("out_sum"),
            ).where(
                UserTokenUsageLogModel.user_id == user_id,
                UserTokenUsageLogModel.created_at >= window_start,
                UserTokenUsageLogModel.created_at < window_end,
            )
        ).first()
        feature_totals = db.execute(
            select(
                UserTokenUsageLogModel.feature_code,
                func.sum(UserTokenUsageLogModel.tokens_total).label("total_sum"),
                func.sum(UserTokenUsageLogModel.tokens_in).label("in_sum"),
                func.sum(UserTokenUsageLogModel.tokens_out).label("out_sum"),
            )
            .where(
                UserTokenUsageLogModel.user_id == user_id,
                UserTokenUsageLogModel.created_at >= window_start,
                UserTokenUsageLogModel.created_at < window_end,
            )
            .group_by(UserTokenUsageLogModel.feature_code)
        ).all()

        return TokenUsageData(
            period=TokenUsagePeriod(unit=unit, window_start=window_start, window_end=window_end),
            summary=TokenUsageSummary(
                tokens_total=int(totals.total_sum or 0),
                tokens_in=int(totals.in_sum or 0),
                tokens_out=int(totals.out_sum or 0),
            ),
            by_feature=[
                TokenUsageFeatureSummary(
                    feature_code=row.feature_code,
                    tokens_total=int(row.total_sum or 0),
                    tokens_in=int(row.in_sum or 0),
                    tokens_out=int(row.out_sum or 0),
                )
                for row in feature_totals
            ],
        )

    @staticmethod
    def ensure_default_plans(db: Session) -> dict[str, object]:
        """Garantit la presence des plans canonique en base."""
        return ensure_default_plans(db)

    @staticmethod
    def get_subscription_status(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """Retourne le statut d abonnement runtime d un utilisateur."""
        return get_subscription_status(
            db,
            user_id=user_id,
            feature_code=BillingService.BILLING_QUOTA_FEATURE,
        )

    @staticmethod
    def get_subscription_status_readonly(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """Equivalent lecture seule du statut d abonnement runtime."""
        return BillingService.get_subscription_status(db, user_id=user_id)

    @staticmethod
    def resolve_runtime_billing_status(subscription: SubscriptionStatusData) -> str:
        """Retourne le statut billing canonique expose au runtime."""
        return resolve_runtime_billing_status(subscription)

    @staticmethod
    def resolve_runtime_plan_code(subscription: SubscriptionStatusData) -> str:
        """Retourne le plan canonique expose au runtime."""
        return resolve_runtime_plan_code(subscription)

    @staticmethod
    def get_plan_lookup_codes(plan_code: str) -> tuple[str, ...]:
        """Retourne les codes de plan compatibles a essayer cote catalogue."""
        return (plan_code,)

    @staticmethod
    def invalidate_cached_subscription_status(user_id: int) -> None:
        """Invalide le cache d abonnement pour un utilisateur donne."""
        invalidate_cached_subscription_status(user_id)

    @staticmethod
    def _invalidate_cached_subscription_status(user_id: int) -> None:
        """Compatibilite locale pour les appels internes encore relies a l ancien helper prive."""
        invalidate_cached_subscription_status(user_id)

    @staticmethod
    def reset_subscription_status_cache() -> None:
        """Vide completement le cache des statuts d abonnement."""
        reset_subscription_status_cache()


__all__ = [
    "BASIC_PLAN_CODE",
    "BillingPlanData",
    "BillingService",
    "BillingServiceError",
    "FREE_PLAN_CODE",
    "PLAN_CODE_TO_STRIPE_ENTITLEMENT",
    "PREMIUM_PLAN_CODE",
    "STRIPE_ENTITLEMENT_TO_PLAN_CODE",
    "SubscriptionStatusData",
]

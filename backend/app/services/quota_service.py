"""
Service de gestion des quotas utilisateur.

Ce module gère les quotas de messages journaliers des utilisateurs
en fonction de leur plan d'abonnement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from time import monotonic

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.billing import UserDailyQuotaUsageModel
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.billing_service import BillingService, SubscriptionStatusData

logger = logging.getLogger(__name__)


class QuotaServiceError(Exception):
    """Exception levée lors d'erreurs de gestion de quota."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de quota.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class QuotaStatusData(BaseModel):
    """État du quota journalier d'un utilisateur."""

    quota_date: date
    limit: int
    consumed: int
    remaining: int
    reset_at: datetime
    blocked: bool


@dataclass(frozen=True)
class _ActiveSubscriptionQuota:
    """Quota dérivé de l'abonnement actif."""

    plan_code: str
    daily_limit: int


class QuotaService:
    """
    Service de gestion des quotas de messages.

    Suit la consommation journalière des utilisateurs et applique les
    limites définies par leur plan d'abonnement.
    """
    @staticmethod
    def _utc_today() -> date:
        """Retourne la date du jour en UTC."""
        return datetime.now(UTC).date()

    @staticmethod
    def _next_reset_at(quota_date: date) -> datetime:
        """Calcule l'instant de réinitialisation du quota."""
        return datetime.combine(quota_date + timedelta(days=1), time.min, tzinfo=UTC)

    @staticmethod
    def _resolve_active_quota_from_subscription(
        *, user_id: int, subscription: SubscriptionStatusData
    ) -> _ActiveSubscriptionQuota:
        """Résout le quota depuis un abonnement donné."""
        if subscription.status != "active" or subscription.plan is None:
            raise QuotaServiceError(
                code="no_active_subscription",
                message="active subscription is required for quota consumption",
                details={"user_id": str(user_id)},
            )
        if subscription.plan.daily_message_limit <= 0:
            raise QuotaServiceError(
                code="invalid_quota_state",
                message="daily message limit is invalid",
                details={
                    "user_id": str(user_id),
                    "plan_code": subscription.plan.code,
                    "daily_message_limit": str(subscription.plan.daily_message_limit),
                },
            )
        return _ActiveSubscriptionQuota(
            plan_code=subscription.plan.code,
            daily_limit=subscription.plan.daily_message_limit,
        )

    @staticmethod
    def _resolve_active_quota(db: Session, *, user_id: int) -> _ActiveSubscriptionQuota:
        """Résout le quota depuis l'abonnement actif de l'utilisateur."""
        subscription = BillingService.get_subscription_status(db, user_id=user_id)
        return QuotaService._resolve_active_quota_from_subscription(
            user_id=user_id, subscription=subscription
        )

    @staticmethod
    def _find_or_create_usage_row(
        db: Session,
        *,
        user_id: int,
        quota_date: date,
    ) -> UserDailyQuotaUsageModel:
        """Trouve ou crée l'enregistrement d'usage journalier avec verrou."""
        query = (
            select(UserDailyQuotaUsageModel)
            .where(
                UserDailyQuotaUsageModel.user_id == user_id,
                UserDailyQuotaUsageModel.quota_date == quota_date,
            )
            .with_for_update()
            .limit(1)
        )
        usage = db.scalar(query)
        if usage is not None:
            return usage
        usage = UserDailyQuotaUsageModel(
            user_id=user_id,
            quota_date=quota_date,
            used_count=0,
        )
        try:
            with db.begin_nested():
                db.add(usage)
                db.flush()
        except IntegrityError:
            usage = db.scalar(query)
            if usage is None:
                raise
        return usage

    @staticmethod
    def _get_usage_row(
        db: Session,
        *,
        user_id: int,
        quota_date: date,
    ) -> UserDailyQuotaUsageModel | None:
        """Récupère l'enregistrement d'usage journalier s'il existe."""
        return db.scalar(
            select(UserDailyQuotaUsageModel)
            .where(
                UserDailyQuotaUsageModel.user_id == user_id,
                UserDailyQuotaUsageModel.quota_date == quota_date,
            )
            .limit(1)
        )

    @staticmethod
    def get_quota_status(
        db: Session,
        *,
        user_id: int,
        subscription: SubscriptionStatusData | None = None,
    ) -> QuotaStatusData:
        """
        Récupère l'état actuel du quota d'un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            subscription: Abonnement pré-chargé (optionnel).

        Returns:
            État du quota avec consommation et limite.
        """
        start = monotonic()
        if subscription is None:
            active_quota = QuotaService._resolve_active_quota(db, user_id=user_id)
        else:
            active_quota = QuotaService._resolve_active_quota_from_subscription(
                user_id=user_id, subscription=subscription
            )
        quota_date = QuotaService._utc_today()
        usage = QuotaService._get_usage_row(db, user_id=user_id, quota_date=quota_date)
        consumed = max(0, usage.used_count) if usage is not None else 0
        remaining = max(0, active_quota.daily_limit - consumed)
        status = QuotaStatusData(
            quota_date=quota_date,
            limit=active_quota.daily_limit,
            consumed=consumed,
            remaining=remaining,
            reset_at=QuotaService._next_reset_at(quota_date),
            blocked=remaining == 0,
        )
        observe_duration("billing_quota_status_seconds", monotonic() - start)
        return status

    @staticmethod
    def consume_quota_or_raise(
        db: Session,
        *,
        user_id: int,
        request_id: str,
    ) -> QuotaStatusData:
        """
        Consomme une unité de quota ou lève une exception si limite atteinte.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            request_id: Identifiant de requête pour le logging.

        Returns:
            État du quota après consommation.

        Raises:
            QuotaServiceError: Si le quota est épuisé.
        """
        start = monotonic()
        active_quota = QuotaService._resolve_active_quota(db, user_id=user_id)
        quota_date = QuotaService._utc_today()
        usage = QuotaService._find_or_create_usage_row(
            db,
            user_id=user_id,
            quota_date=quota_date,
        )
        if usage.used_count < 0:
            increment_counter("quota_invalid_state_total", 1.0)
            logger.error(
                "quota_invalid_state request_id=%s user_id=%s quota_date=%s used_count=%s",
                request_id,
                user_id,
                quota_date.isoformat(),
                usage.used_count,
            )
            raise QuotaServiceError(
                code="invalid_quota_state",
                message="quota usage state is invalid",
                details={
                    "user_id": str(user_id),
                    "quota_date": quota_date.isoformat(),
                    "used_count": str(usage.used_count),
                },
            )

        if usage.used_count >= active_quota.daily_limit:
            increment_counter("quota_exceeded_total", 1.0)
            remaining = 0
            logger.info(
                (
                    "quota_exceeded request_id=%s user_id=%s plan_code=%s "
                    "quota_date=%s used_count=%s limit=%s"
                ),
                request_id,
                user_id,
                active_quota.plan_code,
                quota_date.isoformat(),
                usage.used_count,
                active_quota.daily_limit,
            )
            raise QuotaServiceError(
                code="quota_exceeded",
                message="daily message quota exceeded",
                details={
                    "remaining": str(remaining),
                    "consumed": str(usage.used_count),
                    "limit": str(active_quota.daily_limit),
                    "quota_date": quota_date.isoformat(),
                    "reset_at": QuotaService._next_reset_at(quota_date).isoformat(),
                    "plan_code": active_quota.plan_code,
                },
            )

        usage.used_count += 1
        db.flush()
        increment_counter("quota_consumed_total", 1.0)
        logger.info(
            (
                "quota_consumed request_id=%s user_id=%s plan_code=%s "
                "quota_date=%s consumed=%s limit=%s"
            ),
            request_id,
            user_id,
            active_quota.plan_code,
            quota_date.isoformat(),
            usage.used_count,
            active_quota.daily_limit,
        )
        remaining = max(0, active_quota.daily_limit - usage.used_count)
        observe_duration("billing_quota_consume_seconds", monotonic() - start)
        return QuotaStatusData(
            quota_date=quota_date,
            limit=active_quota.daily_limit,
            consumed=usage.used_count,
            remaining=remaining,
            reset_at=QuotaService._next_reset_at(quota_date),
            blocked=remaining == 0,
        )

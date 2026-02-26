"""
Service de gestion des quotas d'usage B2B.

Ce module gère le suivi et le contrôle de la consommation des comptes
entreprise, avec des limites journalières et mensuelles.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, time, timedelta
from time import monotonic

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)


class B2BUsageServiceError(Exception):
    """Exception levée lors d'erreurs de gestion des quotas B2B."""

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


class B2BUsageSummaryData(BaseModel):
    """Résumé de l'état de consommation d'un credential B2B."""

    account_id: int
    credential_id: int
    usage_date: date
    month_start: date
    month_end: date
    daily_limit: int
    daily_consumed: int
    daily_remaining: int
    monthly_limit: int
    monthly_consumed: int
    monthly_remaining: int
    limit_mode: str
    blocked: bool
    overage_applied: bool


class B2BUsageService:
    """
    Service de gestion des quotas d'usage B2B.

    Suit la consommation des comptes entreprise et applique les limites
    journalières et mensuelles selon le mode configuré (blocage ou dépassement).
    """

    @staticmethod
    def _lock_enterprise_account(db: Session, *, account_id: int) -> None:
        """Verrouille un compte entreprise pour sérialiser les opérations de quota."""
        account = db.scalar(
            select(EnterpriseAccountModel)
            .where(EnterpriseAccountModel.id == account_id)
            .with_for_update()
            .limit(1)
        )
        if account is None:
            raise B2BUsageServiceError(
                code="enterprise_account_not_found",
                message="enterprise account was not found",
                details={"account_id": str(account_id)},
            )

    @staticmethod
    def _utc_today() -> date:
        """Retourne la date du jour en UTC."""
        return datetime.now(UTC).date()

    @staticmethod
    def _month_start_day(usage_date: date) -> date:
        """Retourne le premier jour du mois."""
        return usage_date.replace(day=1)

    @staticmethod
    def _month_end_day(usage_date: date) -> date:
        """Retourne le dernier jour du mois."""
        next_month = (usage_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        return next_month - timedelta(days=1)

    @staticmethod
    def _next_reset_at(usage_date: date) -> datetime:
        """Calcule l'instant de réinitialisation du quota journalier."""
        return datetime.combine(usage_date + timedelta(days=1), time.min, tzinfo=UTC)

    @staticmethod
    def _resolve_limits() -> tuple[int, int, str]:
        """Résout les limites journalières, mensuelles et le mode depuis la config."""
        daily_limit = max(1, settings.b2b_daily_usage_limit)
        monthly_limit = max(daily_limit, settings.b2b_monthly_usage_limit)
        mode = (
            settings.b2b_usage_limit_mode
            if settings.b2b_usage_limit_mode in {"block", "overage"}
            else "block"
        )
        return daily_limit, monthly_limit, mode

    @staticmethod
    def _find_or_create_daily_row(
        db: Session,
        *,
        account_id: int,
        credential_id: int,
        usage_date: date,
    ) -> EnterpriseDailyUsageModel:
        """Trouve ou crée l'enregistrement d'usage journalier avec verrou."""
        query = (
            select(EnterpriseDailyUsageModel)
            .where(
                EnterpriseDailyUsageModel.enterprise_account_id == account_id,
                EnterpriseDailyUsageModel.credential_id == credential_id,
                EnterpriseDailyUsageModel.usage_date == usage_date,
            )
            .with_for_update()
            .limit(1)
        )
        usage = db.scalar(query)
        if usage is not None:
            return usage
        usage = EnterpriseDailyUsageModel(
            enterprise_account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
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
    def _daily_consumed(
        db: Session,
        *,
        account_id: int,
        credential_id: int,
        usage_date: date,
    ) -> int:
        """Récupère la consommation journalière d'un credential."""
        value = db.scalar(
            select(EnterpriseDailyUsageModel.used_count)
            .where(
                EnterpriseDailyUsageModel.enterprise_account_id == account_id,
                EnterpriseDailyUsageModel.credential_id == credential_id,
                EnterpriseDailyUsageModel.usage_date == usage_date,
            )
            .limit(1)
        )
        return max(0, int(value)) if value is not None else 0

    @staticmethod
    def _monthly_consumed(
        db: Session,
        *,
        account_id: int,
        usage_date: date,
    ) -> int:
        """Calcule la consommation mensuelle totale d'un compte."""
        month_start = B2BUsageService._month_start_day(usage_date)
        month_end = B2BUsageService._month_end_day(usage_date)
        value = db.scalar(
            select(func.coalesce(func.sum(EnterpriseDailyUsageModel.used_count), 0)).where(
                EnterpriseDailyUsageModel.enterprise_account_id == account_id,
                EnterpriseDailyUsageModel.usage_date >= month_start,
                EnterpriseDailyUsageModel.usage_date <= month_end,
            )
        )
        return max(0, int(value)) if value is not None else 0

    @staticmethod
    def _summary_from_values(
        *,
        account_id: int,
        credential_id: int,
        usage_date: date,
        daily_limit: int,
        monthly_limit: int,
        limit_mode: str,
        daily_consumed: int,
        monthly_consumed: int,
        overage_applied: bool = False,
    ) -> B2BUsageSummaryData:
        """Construit un résumé d'usage à partir des valeurs calculées."""
        daily_remaining = max(0, daily_limit - daily_consumed)
        monthly_remaining = max(0, monthly_limit - monthly_consumed)
        blocked = limit_mode == "block" and (daily_remaining == 0 or monthly_remaining == 0)
        return B2BUsageSummaryData(
            account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
            month_start=B2BUsageService._month_start_day(usage_date),
            month_end=B2BUsageService._month_end_day(usage_date),
            daily_limit=daily_limit,
            daily_consumed=daily_consumed,
            daily_remaining=daily_remaining,
            monthly_limit=monthly_limit,
            monthly_consumed=monthly_consumed,
            monthly_remaining=monthly_remaining,
            limit_mode=limit_mode,
            blocked=blocked,
            overage_applied=overage_applied,
        )

    @staticmethod
    def get_usage_summary(
        db: Session,
        *,
        account_id: int,
        credential_id: int,
    ) -> B2BUsageSummaryData:
        """
        Récupère le résumé d'usage actuel d'un credential.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.
            credential_id: Identifiant du credential API.

        Returns:
            Résumé incluant consommations et limites journalières/mensuelles.
        """
        start = monotonic()
        usage_date = B2BUsageService._utc_today()
        daily_limit, monthly_limit, mode = B2BUsageService._resolve_limits()
        daily_consumed = B2BUsageService._daily_consumed(
            db,
            account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
        )
        monthly_consumed = B2BUsageService._monthly_consumed(
            db,
            account_id=account_id,
            usage_date=usage_date,
        )
        observe_duration("b2b_usage_summary_seconds", monotonic() - start)
        return B2BUsageService._summary_from_values(
            account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            limit_mode=mode,
            daily_consumed=daily_consumed,
            monthly_consumed=monthly_consumed,
        )

    @staticmethod
    def consume_or_raise(
        db: Session,
        *,
        account_id: int,
        credential_id: int,
        request_id: str,
        units: int = 1,
    ) -> B2BUsageSummaryData:
        """
        Consomme des unités de quota ou lève une exception si limite atteinte.

        Opération transactionnelle qui vérifie et incrémente les compteurs
        d'usage journalier et mensuel.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.
            credential_id: Identifiant du credential API.
            request_id: Identifiant de la requête pour le logging.
            units: Nombre d'unités à consommer.

        Returns:
            Résumé d'usage après consommation.

        Raises:
            B2BUsageServiceError: Si le quota est dépassé en mode blocage.
        """
        start = monotonic()
        if units <= 0:
            raise B2BUsageServiceError(
                code="invalid_usage_units",
                message="usage units must be positive",
                details={"units": str(units)},
            )
        usage_date = B2BUsageService._utc_today()
        daily_limit, monthly_limit, mode = B2BUsageService._resolve_limits()

        # Serialize quota decisions per enterprise account in transactional databases.
        B2BUsageService._lock_enterprise_account(db, account_id=account_id)
        row = B2BUsageService._find_or_create_daily_row(
            db,
            account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
        )
        if row.used_count < 0:
            increment_counter("b2b_usage_invalid_state_total", 1.0)
            raise B2BUsageServiceError(
                code="invalid_b2b_usage_state",
                message="b2b usage state is invalid",
                details={
                    "account_id": str(account_id),
                    "credential_id": str(credential_id),
                    "usage_date": usage_date.isoformat(),
                    "used_count": str(row.used_count),
                },
            )

        monthly_before = B2BUsageService._monthly_consumed(
            db,
            account_id=account_id,
            usage_date=usage_date,
        )
        daily_after = row.used_count + units
        monthly_after = monthly_before + units
        daily_exceeded = daily_after > daily_limit
        monthly_exceeded = monthly_after > monthly_limit
        overage_applied = False

        if daily_exceeded or monthly_exceeded:
            increment_counter("b2b_quota_exceeded_total", 1.0)
            logger.info(
                (
                    "b2b_quota_exceeded request_id=%s account_id=%s credential_id=%s "
                    "daily_after=%s daily_limit=%s monthly_after=%s monthly_limit=%s mode=%s"
                ),
                request_id,
                account_id,
                credential_id,
                daily_after,
                daily_limit,
                monthly_after,
                monthly_limit,
                mode,
            )
            if mode == "block":
                raise B2BUsageServiceError(
                    code="b2b_quota_exceeded",
                    message="b2b contractual usage limit exceeded",
                    details={
                        "daily_limit": str(daily_limit),
                        "daily_consumed": str(row.used_count),
                        "monthly_limit": str(monthly_limit),
                        "monthly_consumed": str(monthly_before),
                        "limit_mode": mode,
                        "reset_at": B2BUsageService._next_reset_at(usage_date).isoformat(),
                    },
                )
            overage_applied = True

        row.used_count = daily_after
        db.flush()
        increment_counter("b2b_usage_events_total", float(units))
        observe_duration("b2b_usage_consume_seconds", monotonic() - start)
        return B2BUsageService._summary_from_values(
            account_id=account_id,
            credential_id=credential_id,
            usage_date=usage_date,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
            limit_mode=mode,
            daily_consumed=daily_after,
            monthly_consumed=monthly_after,
            overage_applied=overage_applied,
        )

"""
Service de facturation B2B.

Ce module gère la facturation des comptes entreprise : cycles de facturation,
calcul des consommations et génération des relevés.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from time import monotonic

from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)


class B2BBillingServiceError(Exception):
    """Exception levée lors d'erreurs de facturation B2B."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de facturation B2B.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class B2BBillingCycleData(BaseModel):
    """Données d'un cycle de facturation B2B."""

    cycle_id: int
    account_id: int
    plan_id: int
    plan_code: str
    plan_display_name: str
    period_start: date
    period_end: date
    status: str
    currency: str
    fixed_amount_cents: int
    included_units: int
    consumed_units: int
    billable_units: int
    unit_price_cents: int
    variable_amount_cents: int
    total_amount_cents: int
    limit_mode: str
    overage_applied: bool
    calculation_snapshot: dict[str, object]
    closed_by_user_id: int | None
    created_at: datetime
    updated_at: datetime


class B2BBillingCycleListData(BaseModel):
    """Liste paginée de cycles de facturation B2B."""

    items: list[B2BBillingCycleData]
    total: int
    limit: int
    offset: int


class B2BBillingClosePayload(BaseModel):
    """Payload pour clôturer un cycle de facturation."""

    account_id: int
    period_start: date
    period_end: date


class B2BBillingService:
    """
    Service de facturation pour comptes entreprise B2B.

    Gère les cycles de facturation, le calcul des montants basés sur
    la consommation et les plans tarifaires.
    """
    @staticmethod
    def _ensure_active_account(db: Session, *, account_id: int) -> EnterpriseAccountModel:
        """
        Vérifie qu'un compte entreprise existe et est actif.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.

        Returns:
            Modèle du compte entreprise.

        Raises:
            B2BBillingServiceError: Si le compte n'existe pas ou est inactif.
        """
        account = db.scalar(
            select(EnterpriseAccountModel).where(EnterpriseAccountModel.id == account_id).limit(1)
        )
        if account is None:
            raise B2BBillingServiceError(
                code="enterprise_account_not_found",
                message="enterprise account was not found",
                details={"account_id": str(account_id)},
            )
        if account.status != "active":
            raise B2BBillingServiceError(
                code="enterprise_account_inactive",
                message="enterprise account is inactive",
                details={"account_id": str(account_id), "status": account.status},
            )
        return account

    @staticmethod
    def _resolve_default_active_plan(db: Session) -> EnterpriseBillingPlanModel:
        """Récupère ou crée le plan B2B par défaut."""
        plan = db.scalar(
            select(EnterpriseBillingPlanModel)
            .where(EnterpriseBillingPlanModel.is_active.is_(True))
            .order_by(EnterpriseBillingPlanModel.id.asc())
            .limit(1)
        )
        if plan is not None:
            return plan
        created = EnterpriseBillingPlanModel(
            code="b2b_standard",
            display_name="B2B Standard",
            monthly_fixed_cents=5000,
            included_monthly_units=settings.b2b_monthly_usage_limit,
            overage_unit_price_cents=2,
            currency="EUR",
            is_active=True,
        )
        db.add(created)
        db.flush()
        return created

    @staticmethod
    def _resolve_active_plan_for_account(
        db: Session, *, account_id: int
    ) -> EnterpriseBillingPlanModel:
        """Récupère le plan actif pour un compte entreprise, ou le plan par défaut."""
        mapping = db.scalar(
            select(EnterpriseAccountBillingPlanModel)
            .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account_id)
            .limit(1)
        )
        if mapping is not None:
            plan = db.scalar(
                select(EnterpriseBillingPlanModel)
                .where(
                    EnterpriseBillingPlanModel.id == mapping.plan_id,
                    EnterpriseBillingPlanModel.is_active.is_(True),
                )
                .limit(1)
            )
            if plan is not None:
                return plan

        default_plan = B2BBillingService._resolve_default_active_plan(db)
        if mapping is None:
            link = EnterpriseAccountBillingPlanModel(
                enterprise_account_id=account_id,
                plan_id=default_plan.id,
            )
            try:
                with db.begin_nested():
                    db.add(link)
                    db.flush()
            except IntegrityError:
                # Concurrent creation of mapping; read winner row.
                pass
            mapping = db.scalar(
                select(EnterpriseAccountBillingPlanModel)
                .where(EnterpriseAccountBillingPlanModel.enterprise_account_id == account_id)
                .limit(1)
            )
            if mapping is not None:
                resolved = db.scalar(
                    select(EnterpriseBillingPlanModel)
                    .where(
                        EnterpriseBillingPlanModel.id == mapping.plan_id,
                        EnterpriseBillingPlanModel.is_active.is_(True),
                    )
                    .limit(1)
                )
                if resolved is not None:
                    return resolved
        return default_plan

    @staticmethod
    def _validate_period(*, period_start: date, period_end: date) -> None:
        """Valide que la période de facturation est cohérente."""
        if period_start > period_end:
            raise B2BBillingServiceError(
                code="invalid_billing_period",
                message="billing period is invalid",
                details={
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                },
            )

    @staticmethod
    def _consumed_units_for_period(
        db: Session, *, account_id: int, period_start: date, period_end: date
    ) -> int:
        """Calcule le total d'unités consommées sur une période."""
        value = db.scalar(
            select(func.coalesce(func.sum(EnterpriseDailyUsageModel.used_count), 0)).where(
                EnterpriseDailyUsageModel.enterprise_account_id == account_id,
                EnterpriseDailyUsageModel.usage_date >= period_start,
                EnterpriseDailyUsageModel.usage_date <= period_end,
            )
        )
        return max(0, int(value) if value is not None else 0)

    @staticmethod
    def _to_data(
        cycle: EnterpriseBillingCycleModel, plan: EnterpriseBillingPlanModel
    ) -> B2BBillingCycleData:
        """Convertit les modèles de cycle et plan en DTO."""
        return B2BBillingCycleData(
            cycle_id=cycle.id,
            account_id=cycle.enterprise_account_id,
            plan_id=cycle.plan_id,
            plan_code=plan.code,
            plan_display_name=plan.display_name,
            period_start=cycle.period_start,
            period_end=cycle.period_end,
            status=cycle.status,
            currency=cycle.currency,
            fixed_amount_cents=cycle.fixed_amount_cents,
            included_units=cycle.included_units,
            consumed_units=cycle.consumed_units,
            billable_units=cycle.billable_units,
            unit_price_cents=cycle.unit_price_cents,
            variable_amount_cents=cycle.variable_amount_cents,
            total_amount_cents=cycle.total_amount_cents,
            limit_mode=cycle.limit_mode,
            overage_applied=cycle.overage_applied,
            calculation_snapshot=dict(cycle.calculation_snapshot),
            closed_by_user_id=cycle.closed_by_user_id,
            created_at=cycle.created_at,
            updated_at=cycle.updated_at,
        )

    @staticmethod
    def _find_cycle(
        db: Session,
        *,
        account_id: int,
        period_start: date,
        period_end: date,
    ) -> EnterpriseBillingCycleModel | None:
        return db.scalar(
            select(EnterpriseBillingCycleModel)
            .where(
                EnterpriseBillingCycleModel.enterprise_account_id == account_id,
                EnterpriseBillingCycleModel.period_start == period_start,
                EnterpriseBillingCycleModel.period_end == period_end,
            )
            .limit(1)
        )

    @staticmethod
    def close_cycle(
        db: Session,
        *,
        account_id: int,
        period_start: date,
        period_end: date,
        closed_by_user_id: int | None,
    ) -> B2BBillingCycleData:
        """
        Clôture un cycle de facturation pour un compte.

        Calcule les montants basés sur la consommation et crée le cycle.
        Opération idempotente : retourne le cycle existant si déjà créé.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.
            period_start: Date de début de la période.
            period_end: Date de fin de la période.
            closed_by_user_id: Identifiant de l'utilisateur clôturant le cycle.

        Returns:
            B2BBillingCycleData du cycle créé ou existant.

        Raises:
            B2BBillingServiceError: Si le compte est invalide ou la période incorrecte.
        """
        started = monotonic()
        B2BBillingService._ensure_active_account(db, account_id=account_id)
        B2BBillingService._validate_period(period_start=period_start, period_end=period_end)
        plan = B2BBillingService._resolve_active_plan_for_account(db, account_id=account_id)

        existing = B2BBillingService._find_cycle(
            db,
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
        )
        if existing is not None:
            observe_duration("b2b_billing_close_cycle_seconds", monotonic() - started)
            return B2BBillingService._to_data(existing, plan)

        consumed_units = B2BBillingService._consumed_units_for_period(
            db,
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
        )
        included_units = max(0, int(plan.included_monthly_units))
        billable_units = max(0, consumed_units - included_units)
        unit_price = max(0, int(plan.overage_unit_price_cents))
        fixed_amount = max(0, int(plan.monthly_fixed_cents))
        variable_amount = billable_units * unit_price
        total_amount = fixed_amount + variable_amount
        limit_mode = (
            settings.b2b_usage_limit_mode
            if settings.b2b_usage_limit_mode in {"block", "overage"}
            else "block"
        )
        overage_applied = billable_units > 0 and limit_mode == "overage"

        snapshot = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "consumed_units": consumed_units,
            "included_units": included_units,
            "billable_units": billable_units,
            "unit_price_cents": unit_price,
            "fixed_amount_cents": fixed_amount,
            "variable_amount_cents": variable_amount,
            "total_amount_cents": total_amount,
            "closed_at": datetime.now(UTC).isoformat(),
        }
        created = EnterpriseBillingCycleModel(
            enterprise_account_id=account_id,
            plan_id=plan.id,
            period_start=period_start,
            period_end=period_end,
            status="closed",
            currency=plan.currency,
            fixed_amount_cents=fixed_amount,
            included_units=included_units,
            consumed_units=consumed_units,
            billable_units=billable_units,
            unit_price_cents=unit_price,
            variable_amount_cents=variable_amount,
            total_amount_cents=total_amount,
            limit_mode=limit_mode,
            overage_applied=overage_applied,
            calculation_snapshot=snapshot,
            closed_by_user_id=closed_by_user_id,
        )
        try:
            with db.begin_nested():
                db.add(created)
                db.flush()
        except IntegrityError:
            existing = B2BBillingService._find_cycle(
                db,
                account_id=account_id,
                period_start=period_start,
                period_end=period_end,
            )
            if existing is None:
                raise
            observe_duration("b2b_billing_close_cycle_seconds", monotonic() - started)
            return B2BBillingService._to_data(existing, plan)

        increment_counter("b2b_billing_cycles_closed_total", 1.0)
        increment_counter("b2b_billing_amount_cents_total", float(total_amount))
        logger.info(
            (
                "b2b_billing_cycle_closed account_id=%s period_start=%s period_end=%s "
                "fixed_cents=%s variable_cents=%s total_cents=%s consumed_units=%s "
                "billable_units=%s mode=%s"
            ),
            account_id,
            period_start.isoformat(),
            period_end.isoformat(),
            fixed_amount,
            variable_amount,
            total_amount,
            consumed_units,
            billable_units,
            limit_mode,
        )
        observe_duration("b2b_billing_close_cycle_seconds", monotonic() - started)
        return B2BBillingService._to_data(created, plan)

    @staticmethod
    def get_latest_cycle(db: Session, *, account_id: int) -> B2BBillingCycleData | None:
        """
        Récupère le dernier cycle de facturation d'un compte.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.

        Returns:
            B2BBillingCycleData du dernier cycle ou None si aucun.

        Raises:
            B2BBillingServiceError: Si le compte est invalide.
        """
        B2BBillingService._ensure_active_account(db, account_id=account_id)
        cycle = db.scalar(
            select(EnterpriseBillingCycleModel)
            .where(EnterpriseBillingCycleModel.enterprise_account_id == account_id)
            .order_by(
                desc(EnterpriseBillingCycleModel.period_end), desc(EnterpriseBillingCycleModel.id)
            )
            .limit(1)
        )
        if cycle is None:
            return None
        plan = db.scalar(
            select(EnterpriseBillingPlanModel)
            .where(EnterpriseBillingPlanModel.id == cycle.plan_id)
            .limit(1)
        )
        if plan is None:
            raise B2BBillingServiceError(
                code="b2b_billing_plan_not_found",
                message="billing plan was not found",
                details={"plan_id": str(cycle.plan_id)},
            )
        return B2BBillingService._to_data(cycle, plan)

    @staticmethod
    def list_cycles(
        db: Session,
        *,
        account_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> B2BBillingCycleListData:
        """
        Liste les cycles de facturation d'un compte avec pagination.

        Args:
            db: Session de base de données.
            account_id: Identifiant du compte entreprise.
            limit: Nombre maximum de résultats.
            offset: Décalage pour la pagination.

        Returns:
            B2BBillingCycleListData avec les cycles et métadonnées de pagination.

        Raises:
            B2BBillingServiceError: Si les paramètres de pagination sont invalides.
        """
        B2BBillingService._ensure_active_account(db, account_id=account_id)
        if limit <= 0 or limit > 100:
            raise B2BBillingServiceError(
                code="invalid_billing_pagination",
                message="billing pagination is invalid",
                details={"field": "limit"},
            )
        if offset < 0:
            raise B2BBillingServiceError(
                code="invalid_billing_pagination",
                message="billing pagination is invalid",
                details={"field": "offset"},
            )

        total = int(
            db.scalar(
                select(func.count(EnterpriseBillingCycleModel.id)).where(
                    EnterpriseBillingCycleModel.enterprise_account_id == account_id
                )
            )
            or 0
        )
        rows = db.scalars(
            select(EnterpriseBillingCycleModel)
            .where(EnterpriseBillingCycleModel.enterprise_account_id == account_id)
            .order_by(
                desc(EnterpriseBillingCycleModel.period_end), desc(EnterpriseBillingCycleModel.id)
            )
            .limit(limit)
            .offset(offset)
        ).all()
        plan_ids = {row.plan_id for row in rows}
        plans = {
            plan.id: plan
            for plan in db.scalars(
                select(EnterpriseBillingPlanModel).where(
                    EnterpriseBillingPlanModel.id.in_(plan_ids)
                )
            ).all()
        }
        items: list[B2BBillingCycleData] = []
        for row in rows:
            plan = plans.get(row.plan_id)
            if plan is None:
                increment_counter("b2b_billing_plan_missing_total", 1.0)
                continue
            items.append(B2BBillingService._to_data(row, plan))
        return B2BBillingCycleListData(items=items, total=total, limit=limit, offset=offset)

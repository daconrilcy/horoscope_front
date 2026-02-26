"""
Service de facturation B2C.

Ce module gère les abonnements utilisateurs, les plans tarifaires,
les tentatives de paiement et les changements de plan.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock
from time import monotonic

from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserSubscriptionModel,
)
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)

ENTRY_PLAN_CODE = "basic-entry"
ENTRY_PLAN_NAME = "Basic 5 EUR/mois"
ENTRY_PLAN_PRICE_CENTS = 500
ENTRY_PLAN_CURRENCY = "EUR"
ENTRY_PLAN_DAILY_LIMIT = 5
PREMIUM_PLAN_CODE = "premium-unlimited"
PREMIUM_PLAN_NAME = "Premium 20 EUR/mois"
PREMIUM_PLAN_PRICE_CENTS = 2000
PREMIUM_PLAN_CURRENCY = "EUR"
PREMIUM_PLAN_DAILY_LIMIT = 1000
_MAX_SUBSCRIPTION_CACHE_ENTRIES = 10_000
_SUBSCRIPTION_STATUS_CACHE: dict[int, tuple[float, "SubscriptionStatusData"]] = {}
_SUBSCRIPTION_STATUS_CACHE_LOCK = Lock()


class BillingServiceError(Exception):
    """Exception levée lors d'erreurs de facturation."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de facturation.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class BillingPlanData(BaseModel):
    """Modèle représentant un plan tarifaire."""

    code: str
    display_name: str
    monthly_price_cents: int
    currency: str
    daily_message_limit: int
    is_active: bool


class SubscriptionStatusData(BaseModel):
    """Modèle représentant le statut d'un abonnement utilisateur."""

    status: str
    plan: BillingPlanData | None
    failure_reason: str | None
    updated_at: datetime | None


class CheckoutPayload(BaseModel):
    """Payload pour une demande de souscription."""

    plan_code: str = ENTRY_PLAN_CODE
    payment_method_token: str = "pm_card_ok"
    idempotency_key: str


class CheckoutData(BaseModel):
    """Résultat d'une opération de checkout."""

    subscription: SubscriptionStatusData
    payment_status: str
    payment_attempt_id: int
    idempotency_key: str


class PlanChangePayload(BaseModel):
    """Payload pour un changement de plan."""

    target_plan_code: str
    idempotency_key: str


class PlanChangeData(BaseModel):
    """Résultat d'un changement de plan."""

    subscription: SubscriptionStatusData
    previous_plan_code: str
    target_plan_code: str
    plan_change_status: str
    plan_change_id: int
    idempotency_key: str


class BillingService:
    """
    Service de gestion de la facturation B2C.

    Gère les abonnements utilisateurs, les tentatives de paiement,
    les changements de plan et le cache des statuts d'abonnement.
    """
    @staticmethod
    def _subscription_cache_ttl_seconds() -> float:
        """Retourne la durée de vie du cache d'abonnement en secondes."""
        return max(0.0, settings.billing_subscription_cache_ttl_seconds)

    @staticmethod
    def _get_cached_subscription_status(user_id: int) -> SubscriptionStatusData | None:
        """
        Récupère le statut d'abonnement depuis le cache.

        Args:
            user_id: Identifiant de l'utilisateur.

        Returns:
            Statut d'abonnement caché ou None si absent/expiré.
        """
        ttl = BillingService._subscription_cache_ttl_seconds()
        if ttl <= 0:
            return None
        now = monotonic()
        with _SUBSCRIPTION_STATUS_CACHE_LOCK:
            BillingService._prune_subscription_cache_locked(now=now)
            cached = _SUBSCRIPTION_STATUS_CACHE.get(user_id)
            if cached is None:
                return None
            expires_at, payload = cached
            if now >= expires_at:
                _SUBSCRIPTION_STATUS_CACHE.pop(user_id, None)
                return None
            return payload.model_copy(deep=True)

    @staticmethod
    def _set_cached_subscription_status(user_id: int, payload: SubscriptionStatusData) -> None:
        """
        Met en cache le statut d'abonnement d'un utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur.
            payload: Statut d'abonnement à mettre en cache.
        """
        ttl = BillingService._subscription_cache_ttl_seconds()
        if ttl <= 0:
            return
        now = monotonic()
        with _SUBSCRIPTION_STATUS_CACHE_LOCK:
            BillingService._prune_subscription_cache_locked(now=now)
            _SUBSCRIPTION_STATUS_CACHE[user_id] = (
                now + ttl,
                payload.model_copy(deep=True),
            )
            while len(_SUBSCRIPTION_STATUS_CACHE) > _MAX_SUBSCRIPTION_CACHE_ENTRIES:
                _SUBSCRIPTION_STATUS_CACHE.pop(next(iter(_SUBSCRIPTION_STATUS_CACHE)))

    @staticmethod
    def _prune_subscription_cache_locked(*, now: float) -> None:
        """Supprime les entrées expirées du cache (doit être appelé avec le verrou)."""
        expired_keys = [
            cached_user_id
            for cached_user_id, (expires_at, _) in _SUBSCRIPTION_STATUS_CACHE.items()
            if now >= expires_at
        ]
        for cached_user_id in expired_keys:
            _SUBSCRIPTION_STATUS_CACHE.pop(cached_user_id, None)

    @staticmethod
    def _invalidate_cached_subscription_status(user_id: int) -> None:
        """Invalide le cache d'abonnement pour un utilisateur donné."""
        with _SUBSCRIPTION_STATUS_CACHE_LOCK:
            _SUBSCRIPTION_STATUS_CACHE.pop(user_id, None)

    @staticmethod
    def reset_subscription_status_cache() -> None:
        """Vide complètement le cache des statuts d'abonnement."""
        with _SUBSCRIPTION_STATUS_CACHE_LOCK:
            _SUBSCRIPTION_STATUS_CACHE.clear()

    @staticmethod
    def _to_plan_data(model: BillingPlanModel) -> BillingPlanData:
        """Convertit un modèle de plan en DTO."""
        return BillingPlanData(
            code=model.code,
            display_name=model.display_name,
            monthly_price_cents=model.monthly_price_cents,
            currency=model.currency,
            daily_message_limit=model.daily_message_limit,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_subscription_data(
        *,
        subscription: UserSubscriptionModel | None,
        plan: BillingPlanModel | None,
    ) -> SubscriptionStatusData:
        """
        Convertit les modèles d'abonnement et de plan en DTO de statut.

        Args:
            subscription: Modèle d'abonnement utilisateur (peut être None).
            plan: Modèle du plan associé (peut être None).

        Returns:
            SubscriptionStatusData avec le statut approprié.
        """
        if subscription is None:
            return SubscriptionStatusData(
                status="inactive",
                plan=None,
                failure_reason=None,
                updated_at=None,
            )
        exposed_status = "active" if subscription.status == "active" else "inactive"
        return SubscriptionStatusData(
            status=exposed_status,
            plan=BillingService._to_plan_data(plan) if plan is not None else None,
            failure_reason=subscription.failure_reason,
            updated_at=subscription.updated_at,
        )

    @staticmethod
    def _get_plan_by_code(db: Session, code: str) -> BillingPlanModel | None:
        """Récupère un plan par son code."""
        return db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == code).limit(1))

    @staticmethod
    def ensure_entry_plan(db: Session) -> BillingPlanModel:
        """S'assure que le plan d'entrée existe et le retourne."""
        return BillingService.ensure_default_plans(db)[ENTRY_PLAN_CODE]

    @staticmethod
    def ensure_default_plans(db: Session) -> dict[str, BillingPlanModel]:
        """
        S'assure que les plans par défaut existent en base.

        Args:
            db: Session de base de données.

        Returns:
            Dictionnaire code_plan -> modèle du plan.
        """
        defaults = {
            ENTRY_PLAN_CODE: {
                "display_name": ENTRY_PLAN_NAME,
                "monthly_price_cents": ENTRY_PLAN_PRICE_CENTS,
                "currency": ENTRY_PLAN_CURRENCY,
                "daily_message_limit": ENTRY_PLAN_DAILY_LIMIT,
            },
            PREMIUM_PLAN_CODE: {
                "display_name": PREMIUM_PLAN_NAME,
                "monthly_price_cents": PREMIUM_PLAN_PRICE_CENTS,
                "currency": PREMIUM_PLAN_CURRENCY,
                "daily_message_limit": PREMIUM_PLAN_DAILY_LIMIT,
            },
        }
        plans: dict[str, BillingPlanModel] = {}
        for code, data in defaults.items():
            existing = BillingService._get_plan_by_code(db, code)
            if existing is None:
                existing = BillingPlanModel(
                    code=code,
                    display_name=data["display_name"],
                    monthly_price_cents=data["monthly_price_cents"],
                    currency=data["currency"],
                    daily_message_limit=data["daily_message_limit"],
                    is_active=True,
                )
                db.add(existing)
                db.flush()
            plans[code] = existing
        return plans

    @staticmethod
    def _get_latest_subscription(db: Session, user_id: int) -> UserSubscriptionModel | None:
        """Récupère le dernier abonnement d'un utilisateur."""
        return db.scalar(
            select(UserSubscriptionModel)
            .where(UserSubscriptionModel.user_id == user_id)
            .order_by(desc(UserSubscriptionModel.updated_at), desc(UserSubscriptionModel.id))
            .limit(1)
        )

    @staticmethod
    def _get_payment_attempt_by_idempotency(
        db: Session,
        *,
        user_id: int,
        idempotency_key: str,
    ) -> PaymentAttemptModel | None:
        """Recherche une tentative de paiement existante par clé d'idempotence."""
        return db.scalar(
            select(PaymentAttemptModel)
            .where(
                PaymentAttemptModel.user_id == user_id,
                PaymentAttemptModel.idempotency_key == idempotency_key,
            )
            .limit(1)
        )

    @staticmethod
    def _simulate_payment_failure(payment_method_token: str) -> tuple[bool, str | None]:
        """
        Simule un échec de paiement basé sur le token.

        Args:
            payment_method_token: Token du moyen de paiement.

        Returns:
            Tuple (échec, raison) indiquant si le paiement doit échouer.
        """
        token = payment_method_token.strip().lower()
        if token in {"pm_fail", "fail", "declined"}:
            return True, "payment provider declined the payment method"
        return False, None

    @staticmethod
    def get_subscription_status(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement d'un utilisateur.

        Utilise le cache si disponible, sinon interroge la base.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            SubscriptionStatusData avec le statut actuel.
        """
        cached = BillingService._get_cached_subscription_status(user_id)
        if cached is not None:
            return cached
        BillingService.ensure_default_plans(db)
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is None:
            payload = BillingService._to_subscription_data(subscription=None, plan=None)
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload
        plan = db.get(BillingPlanModel, latest.plan_id)
        payload = BillingService._to_subscription_data(subscription=latest, plan=plan)
        BillingService._set_cached_subscription_status(user_id, payload)
        return payload

    @staticmethod
    def get_subscription_status_readonly(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement en lecture seule (sans créer de plans).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            SubscriptionStatusData avec le statut actuel.
        """
        cached = BillingService._get_cached_subscription_status(user_id)
        if cached is not None:
            return cached
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is None:
            payload = BillingService._to_subscription_data(subscription=None, plan=None)
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload
        plan = db.get(BillingPlanModel, latest.plan_id)
        payload = BillingService._to_subscription_data(subscription=latest, plan=plan)
        BillingService._set_cached_subscription_status(user_id, payload)
        return payload

    @staticmethod
    def _get_plan_change_by_idempotency(
        db: Session,
        *,
        user_id: int,
        idempotency_key: str,
        for_update: bool = False,
    ) -> SubscriptionPlanChangeModel | None:
        query = (
            select(SubscriptionPlanChangeModel)
            .where(
                SubscriptionPlanChangeModel.user_id == user_id,
                SubscriptionPlanChangeModel.idempotency_key == idempotency_key,
            )
            .limit(1)
        )
        if for_update:
            query = query.with_for_update()
        return db.scalar(query)

    @staticmethod
    def _build_plan_change_data(
        db: Session,
        *,
        user_id: int,
        plan_change: SubscriptionPlanChangeModel,
    ) -> PlanChangeData:
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        current_plan = db.get(BillingPlanModel, latest.plan_id) if latest is not None else None
        previous_plan = db.get(BillingPlanModel, plan_change.from_plan_id)
        target_plan = db.get(BillingPlanModel, plan_change.to_plan_id)
        return PlanChangeData(
            subscription=BillingService._to_subscription_data(
                subscription=latest,
                plan=current_plan,
            ),
            previous_plan_code=previous_plan.code if previous_plan is not None else "unknown",
            target_plan_code=target_plan.code if target_plan is not None else "unknown",
            plan_change_status=plan_change.status,
            plan_change_id=plan_change.id,
            idempotency_key=plan_change.idempotency_key,
        )

    @staticmethod
    def _upsert_subscription_pending(
        db: Session,
        *,
        user_id: int,
        plan_id: int,
    ) -> UserSubscriptionModel:
        subscription = BillingService._get_latest_subscription(db, user_id=user_id)
        if subscription is None:
            subscription = UserSubscriptionModel(
                user_id=user_id,
                plan_id=plan_id,
                status="pending",
                failure_reason=None,
            )
            db.add(subscription)
            db.flush()
            return subscription
        subscription.plan_id = plan_id
        subscription.status = "pending"
        subscription.failure_reason = None
        db.flush()
        return subscription

    @staticmethod
    def _apply_payment_result(
        db: Session,
        *,
        payment_attempt: PaymentAttemptModel,
        subscription: UserSubscriptionModel,
        failed: bool,
        failure_reason: str | None,
    ) -> None:
        if failed:
            payment_attempt.status = "failed"
            payment_attempt.failure_reason = failure_reason
            subscription.status = "failed"
            subscription.failure_reason = failure_reason
            subscription.started_at = None
            increment_counter("billing_checkout_failure_total", 1.0)
            return

        now = datetime.now(timezone.utc)
        payment_attempt.status = "succeeded"
        payment_attempt.failure_reason = None
        subscription.status = "active"
        subscription.failure_reason = None
        subscription.started_at = now
        increment_counter("billing_checkout_success_total", 1.0)

    @staticmethod
    def _checkout_internal(
        db: Session,
        *,
        user_id: int,
        payload: CheckoutPayload,
        action: str,
        request_id: str,
    ) -> CheckoutData:
        start = monotonic()
        BillingService._invalidate_cached_subscription_status(user_id)
        BillingService.ensure_default_plans(db)
        plan = BillingService._get_plan_by_code(db, payload.plan_code)
        if plan is None or not plan.is_active:
            raise BillingServiceError(
                code="invalid_plan",
                message="billing plan is invalid",
                details={"plan_code": payload.plan_code},
            )

        existing_attempt = BillingService._get_payment_attempt_by_idempotency(
            db,
            user_id=user_id,
            idempotency_key=payload.idempotency_key,
        )
        if existing_attempt is not None:
            latest = BillingService._get_latest_subscription(db, user_id=user_id)
            latest_plan = db.get(BillingPlanModel, latest.plan_id) if latest is not None else None
            observe_duration("billing_checkout_seconds", monotonic() - start)
            return CheckoutData(
                subscription=BillingService._to_subscription_data(
                    subscription=latest,
                    plan=latest_plan,
                ),
                payment_status=existing_attempt.status,
                payment_attempt_id=existing_attempt.id,
                idempotency_key=existing_attempt.idempotency_key,
            )

        active_subscription = db.scalar(
            select(UserSubscriptionModel)
            .where(
                UserSubscriptionModel.user_id == user_id,
                UserSubscriptionModel.status == "active",
            )
            .limit(1)
        )
        if active_subscription is not None:
            raise BillingServiceError(
                code="subscription_already_active",
                message="subscription is already active",
                details={"user_id": str(user_id)},
            )

        subscription = BillingService._upsert_subscription_pending(
            db,
            user_id=user_id,
            plan_id=plan.id,
        )
        payment_attempt = PaymentAttemptModel(
            user_id=user_id,
            plan_id=plan.id,
            action=action,
            idempotency_key=payload.idempotency_key,
            status="pending",
            failure_reason=None,
        )
        db.add(payment_attempt)
        db.flush()

        failed, failure_reason = BillingService._simulate_payment_failure(
            payload.payment_method_token
        )
        BillingService._apply_payment_result(
            db,
            payment_attempt=payment_attempt,
            subscription=subscription,
            failed=failed,
            failure_reason=failure_reason,
        )
        db.flush()
        observe_duration("billing_checkout_seconds", monotonic() - start)
        if failed:
            logger.info(
                (
                    "billing_checkout_failed request_id=%s user_id=%s "
                    "plan_code=%s payment_attempt_id=%s reason=%s"
                ),
                request_id,
                user_id,
                plan.code,
                payment_attempt.id,
                failure_reason,
            )
        else:
            logger.info(
                (
                    "billing_checkout_succeeded request_id=%s user_id=%s "
                    "plan_code=%s payment_attempt_id=%s"
                ),
                request_id,
                user_id,
                plan.code,
                payment_attempt.id,
            )
        return CheckoutData(
            subscription=BillingService._to_subscription_data(subscription=subscription, plan=plan),
            payment_status=payment_attempt.status,
            payment_attempt_id=payment_attempt.id,
            idempotency_key=payment_attempt.idempotency_key,
        )

    @staticmethod
    def create_checkout(
        db: Session, *, user_id: int, payload: CheckoutPayload, request_id: str
    ) -> CheckoutData:
        """
        Crée une nouvelle souscription pour un utilisateur.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            payload: Données du checkout.
            request_id: Identifiant de la requête pour traçabilité.

        Returns:
            CheckoutData avec le résultat de l'opération.

        Raises:
            BillingServiceError: Si le plan est invalide
                ou l'utilisateur a déjà un abonnement actif.
        """
        return BillingService._checkout_internal(
            db,
            user_id=user_id,
            payload=payload,
            action="checkout",
            request_id=request_id,
        )

    @staticmethod
    def retry_checkout(
        db: Session, *, user_id: int, payload: CheckoutPayload, request_id: str
    ) -> CheckoutData:
        """
        Réessaie une souscription après un échec de paiement.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            payload: Données du checkout.
            request_id: Identifiant de la requête pour traçabilité.

        Returns:
            CheckoutData avec le résultat de la tentative.

        Raises:
            BillingServiceError: Si l'utilisateur a déjà un abonnement actif.
        """
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is not None and latest.status == "active":
            raise BillingServiceError(
                code="subscription_already_active",
                message="subscription is already active",
                details={"user_id": str(user_id)},
            )
        increment_counter("billing_retry_total", 1.0)
        return BillingService._checkout_internal(
            db,
            user_id=user_id,
            payload=payload,
            action="retry",
            request_id=request_id,
        )

    @staticmethod
    def change_subscription_plan(
        db: Session,
        *,
        user_id: int,
        payload: PlanChangePayload,
        request_id: str,
    ) -> PlanChangeData:
        """
        Change le plan d'un abonnement actif.

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.
            payload: Données du changement de plan.
            request_id: Identifiant de la requête pour traçabilité.

        Returns:
            PlanChangeData avec le résultat du changement.

        Raises:
            BillingServiceError: Si pas d'abonnement actif, plan cible invalide,
                ou déjà sur le plan cible.
        """
        start = monotonic()
        BillingService._invalidate_cached_subscription_status(user_id)
        BillingService.ensure_default_plans(db)
        existing_change = BillingService._get_plan_change_by_idempotency(
            db,
            user_id=user_id,
            idempotency_key=payload.idempotency_key,
        )
        if existing_change is not None:
            observe_duration("billing_plan_change_seconds", monotonic() - start)
            return BillingService._build_plan_change_data(
                db,
                user_id=user_id,
                plan_change=existing_change,
            )

        subscription = db.scalar(
            select(UserSubscriptionModel)
            .where(UserSubscriptionModel.user_id == user_id)
            .with_for_update()
            .limit(1)
        )
        if subscription is None or subscription.status != "active":
            increment_counter("billing_plan_change_failure_total", 1.0)
            raise BillingServiceError(
                code="no_active_subscription",
                message="active subscription is required to change plan",
                details={"user_id": str(user_id)},
            )

        target_plan = BillingService._get_plan_by_code(db, payload.target_plan_code)
        if target_plan is None or not target_plan.is_active:
            increment_counter("billing_plan_change_failure_total", 1.0)
            raise BillingServiceError(
                code="invalid_target_plan",
                message="target billing plan is invalid",
                details={"target_plan_code": payload.target_plan_code},
            )

        current_plan = db.get(BillingPlanModel, subscription.plan_id)
        if current_plan is None:
            increment_counter("billing_plan_change_failure_total", 1.0)
            raise BillingServiceError(
                code="plan_change_not_allowed",
                message="current subscription plan is missing",
                details={"user_id": str(user_id)},
            )
        if current_plan.code == target_plan.code:
            increment_counter("billing_plan_change_failure_total", 1.0)
            raise BillingServiceError(
                code="duplicate_plan_change",
                message="subscription is already using target plan",
                details={"target_plan_code": target_plan.code},
            )

        plan_change = SubscriptionPlanChangeModel(
            user_id=user_id,
            from_plan_id=current_plan.id,
            to_plan_id=target_plan.id,
            idempotency_key=payload.idempotency_key,
            status="pending",
            failure_reason=None,
        )
        try:
            with db.begin_nested():
                db.add(plan_change)
                db.flush()
        except IntegrityError:
            existing_change = BillingService._get_plan_change_by_idempotency(
                db,
                user_id=user_id,
                idempotency_key=payload.idempotency_key,
                for_update=True,
            )
            if existing_change is None:
                raise
            observe_duration("billing_plan_change_seconds", monotonic() - start)
            return BillingService._build_plan_change_data(
                db,
                user_id=user_id,
                plan_change=existing_change,
            )

        subscription.plan_id = target_plan.id
        subscription.failure_reason = None
        db.flush()

        plan_change.status = "succeeded"
        plan_change.failure_reason = None
        db.flush()
        increment_counter("billing_plan_change_total", 1.0)
        observe_duration("billing_plan_change_seconds", monotonic() - start)

        logger.info(
            (
                "billing_plan_changed request_id=%s user_id=%s from_plan_code=%s "
                "target_plan_code=%s plan_change_id=%s"
            ),
            request_id,
            user_id,
            current_plan.code,
            target_plan.code,
            plan_change.id,
        )

        return PlanChangeData(
            subscription=BillingService._to_subscription_data(
                subscription=subscription,
                plan=target_plan,
            ),
            previous_plan_code=current_plan.code,
            target_plan_code=target_plan.code,
            plan_change_status=plan_change.status,
            plan_change_id=plan_change.id,
            idempotency_key=plan_change.idempotency_key,
        )

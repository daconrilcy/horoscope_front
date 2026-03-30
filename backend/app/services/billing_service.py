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
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.billing import (
    BillingPlanModel,
    UserSubscriptionModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.observability.metrics import increment_counter

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

# Mapping entre le plan d'accès Stripe (entitlement_plan) et le code du plan applicatif.
STRIPE_ENTITLEMENT_TO_PLAN_CODE = {
    "basic": ENTRY_PLAN_CODE,
    "premium": PREMIUM_PLAN_CODE,
}
PLAN_CODE_TO_STRIPE_ENTITLEMENT = {
    ENTRY_PLAN_CODE: "basic",
    PREMIUM_PLAN_CODE: "premium",
}

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
    subscription_status: str | None = None
    plan: BillingPlanData | None
    failure_reason: str | None
    updated_at: datetime | None


class BillingService:
    """
    Service de gestion de la facturation B2C.

    Gère les abonnements utilisateurs et le cache des statuts d'abonnement.
    Les mutations (checkout, plan change) sont désormais déléguées à Stripe.
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
    def _to_canonical_plan_data(plan: BillingPlanData | None) -> BillingPlanData | None:
        """Convertit un DTO plan vers le code canonique exposé à la lecture."""
        if plan is None:
            return None
        canonical_code = PLAN_CODE_TO_STRIPE_ENTITLEMENT.get(plan.code, plan.code)
        if canonical_code == plan.code:
            return plan
        return plan.model_copy(update={"code": canonical_code})

    @staticmethod
    def _get_default_plan_data_by_code(code: str | None) -> BillingPlanData | None:
        """Construit un DTO plan à partir des constantes applicatives par défaut."""
        defaults = {
            ENTRY_PLAN_CODE: BillingPlanData(
                code=ENTRY_PLAN_CODE,
                display_name=ENTRY_PLAN_NAME,
                monthly_price_cents=ENTRY_PLAN_PRICE_CENTS,
                currency=ENTRY_PLAN_CURRENCY,
                daily_message_limit=ENTRY_PLAN_DAILY_LIMIT,
                is_active=True,
            ),
            PREMIUM_PLAN_CODE: BillingPlanData(
                code=PREMIUM_PLAN_CODE,
                display_name=PREMIUM_PLAN_NAME,
                monthly_price_cents=PREMIUM_PLAN_PRICE_CENTS,
                currency=PREMIUM_PLAN_CURRENCY,
                daily_message_limit=PREMIUM_PLAN_DAILY_LIMIT,
                is_active=True,
            ),
        }
        return defaults.get(code)

    @staticmethod
    def _to_subscription_data(
        *,
        subscription: UserSubscriptionModel | None,
        plan: BillingPlanModel | None,
        stripe_subscription_status: str | None,
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
                subscription_status=stripe_subscription_status,
                plan=None,
                failure_reason=None,
                updated_at=None,
            )
        exposed_status = "active" if subscription.status == "active" else "inactive"
        return SubscriptionStatusData(
            status=exposed_status,
            subscription_status=stripe_subscription_status,
            plan=BillingService._to_plan_data(plan) if plan is not None else None,
            failure_reason=subscription.failure_reason,
            updated_at=subscription.updated_at,
        )

    @staticmethod
    def _get_stripe_billing_profile(
        db: Session,
        *,
        user_id: int,
    ) -> StripeBillingProfileModel | None:
        """Récupère le profil billing Stripe d'un utilisateur."""
        return db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.user_id == user_id)
            .limit(1)
        )

    @staticmethod
    def _has_usable_stripe_snapshot(profile: StripeBillingProfileModel | None) -> bool:
        """
        Détermine si un profil Stripe porte un snapshot métier exploitable.

        Un profil est considéré exploitable dès qu'il porte un statut Stripe,
        une subscription Stripe, ou un entitlement non-free.
        """
        if profile is None:
            return False
        return bool(
            profile.subscription_status
            or profile.stripe_subscription_id
            or profile.entitlement_plan not in {"", "free"}
        )

    @staticmethod
    def _get_plan_by_code(db: Session, code: str) -> BillingPlanModel | None:
        """Récupère un plan par son code."""
        return db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == code).limit(1))

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
    def _to_stripe_subscription_data(
        db: Session,
        *,
        profile: StripeBillingProfileModel,
    ) -> SubscriptionStatusData:
        """
        Convertit un profil Stripe canonique en DTO de statut (Stripe-first).
        """
        # Mapping subscription_status Stripe -> status exposé
        # trialing | active -> active
        # others -> inactive
        is_active = profile.subscription_status in {"active", "trialing"}
        exposed_status = "active" if is_active else "inactive"

        # Récupération du plan via entitlement_plan ("basic", "premium", etc.)
        # On cherche un BillingPlanModel qui correspond au code applicatif mappé.
        app_plan_code = STRIPE_ENTITLEMENT_TO_PLAN_CODE.get(profile.entitlement_plan)
        plan_model = BillingService._get_plan_by_code(db, app_plan_code) if app_plan_code else None
        if plan_model is not None:
            plan_data = BillingService._to_plan_data(plan_model)
        else:
            plan_data = BillingService._get_default_plan_data_by_code(app_plan_code)

        return SubscriptionStatusData(
            status=exposed_status,
            subscription_status=profile.subscription_status,
            plan=plan_data,
            failure_reason=None,
            updated_at=profile.updated_at,
        )

    @staticmethod
    def resolve_runtime_billing_status(subscription: SubscriptionStatusData) -> str:
        """Retourne le statut billing canonique à exposer au runtime."""
        if subscription.subscription_status is not None:
            return subscription.subscription_status
        if subscription.plan is None:
            return "none"
        return subscription.status

    @staticmethod
    def resolve_runtime_plan_code(subscription: SubscriptionStatusData) -> str:
        """
        Retourne le plan canonique à utiliser côté runtime/entitlements.

        Les plans commerciaux legacy (`basic-entry`, `premium-unlimited`) sont
        ramenés vers les codes canoniques (`basic`, `premium`) quand le snapshot
        est piloté par Stripe.
        """
        if subscription.plan is None:
            return "none"
        if subscription.subscription_status is not None:
            return PLAN_CODE_TO_STRIPE_ENTITLEMENT.get(
                subscription.plan.code,
                subscription.plan.code,
            )
        return subscription.plan.code

    @staticmethod
    def get_plan_lookup_codes(plan_code: str) -> tuple[str, ...]:
        """
        Retourne les codes de plan compatibles à essayer côté catalogue canonique.

        Permet une transition douce entre les codes commerciaux legacy
        (`basic-entry`, `premium-unlimited`) et les codes canoniques
        (`basic`, `premium`).
        """
        candidates = [plan_code]
        canonical_code = PLAN_CODE_TO_STRIPE_ENTITLEMENT.get(plan_code)
        if canonical_code and canonical_code not in candidates:
            candidates.append(canonical_code)
        commercial_code = STRIPE_ENTITLEMENT_TO_PLAN_CODE.get(plan_code)
        if commercial_code and commercial_code not in candidates:
            candidates.append(commercial_code)
        return tuple(candidates)

    @staticmethod
    def _to_read_model_subscription_data(
        subscription: SubscriptionStatusData,
    ) -> SubscriptionStatusData:
        """Normalise le contrat de lecture billing pour l'API publique."""
        return subscription.model_copy(
            update={"plan": BillingService._to_canonical_plan_data(subscription.plan)}
        )

    @staticmethod
    def get_subscription_status(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement d'un utilisateur.

        Utilise le cache si disponible, sinon interroge la base (Stripe-first).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            SubscriptionStatusData avec le statut actuel.
        """
        cached = BillingService._get_cached_subscription_status(user_id)
        if cached is not None:
            return BillingService._to_read_model_subscription_data(cached)

        BillingService.ensure_default_plans(db)

        # 1. Priorité au snapshot Stripe canonique
        stripe_profile = BillingService._get_stripe_billing_profile(db, user_id=user_id)
        if BillingService._has_usable_stripe_snapshot(stripe_profile):
            payload = BillingService._to_stripe_subscription_data(db, profile=stripe_profile)
            BillingService._set_cached_subscription_status(user_id, payload)
            return BillingService._to_read_model_subscription_data(payload)

        # 2. Fallback legacy si pas de profil Stripe exploitable
        stripe_subscription_status = None
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is None:
            payload = BillingService._to_subscription_data(
                subscription=None,
                plan=None,
                stripe_subscription_status=stripe_subscription_status,
            )
            BillingService._set_cached_subscription_status(user_id, payload)
            return BillingService._to_read_model_subscription_data(payload)

        plan = db.get(BillingPlanModel, latest.plan_id)
        payload = BillingService._to_subscription_data(
            subscription=latest,
            plan=plan,
            stripe_subscription_status=stripe_subscription_status,
        )
        BillingService._set_cached_subscription_status(user_id, payload)
        return BillingService._to_read_model_subscription_data(payload)

    @staticmethod
    def get_subscription_status_readonly(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement en lecture seule (Stripe-first).

        Args:
            db: Session de base de données.
            user_id: Identifiant de l'utilisateur.

        Returns:
            SubscriptionStatusData avec le statut actuel.
        """
        cached = BillingService._get_cached_subscription_status(user_id)
        if cached is not None:
            return cached

        # 1. Priorité au snapshot Stripe canonique
        stripe_profile = BillingService._get_stripe_billing_profile(db, user_id=user_id)
        if BillingService._has_usable_stripe_snapshot(stripe_profile):
            payload = BillingService._to_stripe_subscription_data(db, profile=stripe_profile)
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload

        # 2. Fallback legacy si pas de profil Stripe exploitable
        stripe_subscription_status = None
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is None:
            payload = BillingService._to_subscription_data(
                subscription=None,
                plan=None,
                stripe_subscription_status=stripe_subscription_status,
            )
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload

        plan = db.get(BillingPlanModel, latest.plan_id)
        payload = BillingService._to_subscription_data(
            subscription=latest,
            plan=plan,
            stripe_subscription_status=stripe_subscription_status,
        )
        BillingService._set_cached_subscription_status(user_id, payload)
        return payload

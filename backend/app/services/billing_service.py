"""
Service de facturation B2C.

Ce module gère les abonnements utilisateurs et le cache des statuts d'abonnement.
Les plans et la facturation sont pilotés par Stripe (Stripe-first).
Le fallback vers UserSubscriptionModel est maintenu uniquement pour la compatibilité des tests.
"""

from __future__ import annotations

import logging
from datetime import datetime
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

logger = logging.getLogger(__name__)

# Codes canoniques des plans
BASIC_PLAN_CODE = "basic"
PREMIUM_PLAN_CODE = "premium"
_PLAN_DEFAULTS: dict[str, dict[str, object]] = {
    BASIC_PLAN_CODE: {
        "display_name": "Basic",
        "monthly_price_cents": 900,
        "currency": "EUR",
        "daily_message_limit": 50,
    },
    PREMIUM_PLAN_CODE: {
        "display_name": "Premium",
        "monthly_price_cents": 2900,
        "currency": "EUR",
        "daily_message_limit": 1000,
    },
}

# Mappings pour compatibilité descendante (principalement pour les tests)
STRIPE_ENTITLEMENT_TO_PLAN_CODE: dict[str, str] = {}
PLAN_CODE_TO_STRIPE_ENTITLEMENT: dict[str, str] = {}

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
    Les mutations (checkout, plan change) sont déléguées à Stripe.
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
        defaults = _PLAN_DEFAULTS.get(model.code)
        monthly_price_cents = model.monthly_price_cents
        currency = model.currency
        daily_message_limit = model.daily_message_limit
        display_name = model.display_name

        # Durcissement local/runtime: certains jeux de données legacy gardent 0 en DB.
        # Le frontend ne doit pas exposer "0 €" pour les plans Stripe canoniques.
        if defaults is not None:
            if monthly_price_cents <= 0:
                monthly_price_cents = int(defaults["monthly_price_cents"])
            if not currency:
                currency = str(defaults["currency"])
            if daily_message_limit <= 0:
                daily_message_limit = int(defaults["daily_message_limit"])
            if not display_name:
                display_name = str(defaults["display_name"])

        return BillingPlanData(
            code=model.code,
            display_name=display_name,
            monthly_price_cents=monthly_price_cents,
            currency=currency,
            daily_message_limit=daily_message_limit,
            is_active=model.is_active,
        )

    @staticmethod
    def _get_default_plan_data_by_code(code: str | None) -> BillingPlanData | None:
        """Construit un DTO plan à partir des constantes applicatives par défaut (sans prix)."""
        defaults = _PLAN_DEFAULTS.get(code or "")
        if defaults is None:
            return None
        return BillingPlanData(
            code=code or "",
            display_name=str(defaults["display_name"]),
            monthly_price_cents=int(defaults["monthly_price_cents"]),
            currency=str(defaults["currency"]),
            daily_message_limit=int(defaults["daily_message_limit"]),
            is_active=True,
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
        """
        plans: dict[str, BillingPlanModel] = {}
        for code, data in _PLAN_DEFAULTS.items():
            existing = BillingService._get_plan_by_code(db, code)
            if existing is None:
                existing = BillingPlanModel(
                    code=code,
                    display_name=str(data["display_name"]),
                    monthly_price_cents=int(data["monthly_price_cents"]),
                    currency=str(data["currency"]),
                    daily_message_limit=int(data["daily_message_limit"]),
                    is_active=True,
                )
                db.add(existing)
                db.flush()
            else:
                changed = False
                if existing.monthly_price_cents <= 0:
                    existing.monthly_price_cents = int(data["monthly_price_cents"])
                    changed = True
                if not existing.currency:
                    existing.currency = str(data["currency"])
                    changed = True
                if existing.daily_message_limit <= 0:
                    existing.daily_message_limit = int(data["daily_message_limit"])
                    changed = True
                if not existing.display_name:
                    existing.display_name = str(data["display_name"])
                    changed = True
                if changed:
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
        is_active = profile.subscription_status in {"active", "trialing"}
        exposed_status = "active" if is_active else "inactive"

        app_plan_code = profile.entitlement_plan
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
        """
        if subscription.plan is None:
            return "none"
        return subscription.plan.code

    @staticmethod
    def get_plan_lookup_codes(plan_code: str) -> tuple[str, ...]:
        """
        Retourne les codes de plan compatibles à essayer côté catalogue canonique.
        Restauré pour compatibilité avec EffectiveEntitlementResolverService.
        """
        return (plan_code,)

    @staticmethod
    def get_subscription_status(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement d'un utilisateur (Stripe-first avec fallback legacy).
        Le fallback legacy est maintenu UNIQUEMENT pour la compatibilité des tests.
        """
        cached = BillingService._get_cached_subscription_status(user_id)
        if cached is not None:
            return cached

        BillingService.ensure_default_plans(db)

        # 1. Priorité au snapshot Stripe canonique
        stripe_profile = BillingService._get_stripe_billing_profile(db, user_id=user_id)
        if BillingService._has_usable_stripe_snapshot(stripe_profile):
            payload = BillingService._to_stripe_subscription_data(db, profile=stripe_profile)
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload

        # 2. Fallback legacy si pas de profil Stripe exploitable (Maintenu pour les tests)
        latest = BillingService._get_latest_subscription(db, user_id=user_id)
        if latest is not None:
            plan = db.get(BillingPlanModel, latest.plan_id)
            exposed_status = "active" if latest.status == "active" else "inactive"
            payload = SubscriptionStatusData(
                status=exposed_status,
                subscription_status=None,
                plan=BillingService._to_plan_data(plan) if plan is not None else None,
                failure_reason=latest.failure_reason,
                updated_at=latest.updated_at,
            )
            BillingService._set_cached_subscription_status(user_id, payload)
            return payload

        # 3. Par défaut : inactif
        payload = SubscriptionStatusData(
            status="inactive",
            subscription_status=None,
            plan=None,
            failure_reason=None,
            updated_at=None,
        )
        BillingService._set_cached_subscription_status(user_id, payload)
        return payload

    @staticmethod
    def get_subscription_status_readonly(db: Session, *, user_id: int) -> SubscriptionStatusData:
        """
        Récupère le statut d'abonnement en lecture seule.
        """
        return BillingService.get_subscription_status(db, user_id=user_id)

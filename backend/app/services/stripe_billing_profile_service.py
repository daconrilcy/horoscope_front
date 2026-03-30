from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.stripe_billing import StripeBillingProfileModel

logger = logging.getLogger(__name__)


def _build_price_entitlement_map() -> dict[str, str]:
    """Construit le mapping Price ID -> Plan applicatif depuis la config."""
    result: dict[str, str] = {}
    if settings.stripe_price_basic:
        result[settings.stripe_price_basic] = "basic"
    if settings.stripe_price_premium:
        result[settings.stripe_price_premium] = "premium"
    return result


# Mapping centralisé des Price IDs Stripe vers les plans applicatifs.
STRIPE_PRICE_ENTITLEMENT_MAP: dict[str, str] = _build_price_entitlement_map()


def derive_entitlement_plan(
    subscription_status: str | None,
    stripe_price_id: str | None,
    current_entitlement: str = "free",
) -> str:
    """
    Décide du plan d'accès (entitlement) basé sur le statut et le prix Stripe.
    Fonction pure testable.
    """
    if subscription_status in ("active", "trialing"):
        plan = STRIPE_PRICE_ENTITLEMENT_MAP.get(stripe_price_id or "")
        if plan is None:
            # Fail-closed : price_id inconnu -> jamais d'élévation par défaut
            logger.warning(
                "stripe_billing: unknown stripe_price_id=%r, defaulting to free",
                stripe_price_id,
            )
            return "free"
        return plan

    if subscription_status == "past_due":
        # Grace period : on conserve le plan actuel pour ne pas couper l'accès brutalement
        return current_entitlement

    # canceled, unpaid, incomplete, incomplete_expired, paused, or None -> free
    return "free"


class StripeBillingProfileService:
    """
    Service gérant le mapping entre les utilisateurs SaaS et leurs profils Stripe.
    """

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> StripeBillingProfileModel | None:
        """
        Récupère le profil de facturation pour un utilisateur donné.
        Ne crée PAS le profil s'il n'existe pas (lecture seule).
        """
        return db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.user_id == user_id)
            .limit(1)
        )

    @staticmethod
    def get_or_create_profile(db: Session, user_id: int) -> StripeBillingProfileModel:
        """
        Récupère ou crée un profil de facturation Stripe pour un utilisateur.
        Idempotent et sûr sous concurrence.
        """
        existing = db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.user_id == user_id)
            .limit(1)
        )
        if existing is not None:
            return existing

        profile = StripeBillingProfileModel(user_id=user_id, entitlement_plan="free")
        try:
            # Utilisation d'un point de sauvegarde pour gérer proprement l'IntegrityError
            # sans invalider toute la transaction parente.
            with db.begin_nested():
                db.add(profile)
                db.flush()
            return profile
        except IntegrityError:
            # Course concurrente : un autre thread/process a créé le profil
            # entre notre SELECT et notre INSERT.
            # begin_nested() a déjà rollback le savepoint automatiquement —
            # NE PAS appeler db.rollback() ici, cela détruirait la transaction parente.
            return db.scalar(
                select(StripeBillingProfileModel)
                .where(StripeBillingProfileModel.user_id == user_id)
                .limit(1)
            )

    @staticmethod
    def get_by_stripe_customer_id(
        db: Session, stripe_customer_id: str
    ) -> StripeBillingProfileModel | None:
        """Résolution d'un profil par l'identifiant Customer Stripe."""
        return db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.stripe_customer_id == stripe_customer_id)
            .limit(1)
        )

    @staticmethod
    def get_by_stripe_subscription_id(
        db: Session, stripe_subscription_id: str
    ) -> StripeBillingProfileModel | None:
        """Résolution d'un profil par l'identifiant Subscription Stripe."""
        return db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.stripe_subscription_id == stripe_subscription_id)
            .limit(1)
        )

    @staticmethod
    def get_entitlement_plan(db: Session, user_id: int) -> str:
        """
        Détermine le plan d'accès effectif d'un utilisateur.
        Retourne "free" si aucun profil n'existe.
        """
        profile = db.scalar(
            select(StripeBillingProfileModel)
            .where(StripeBillingProfileModel.user_id == user_id)
            .limit(1)
        )
        if profile is None:
            return "free"
        return profile.entitlement_plan

    @staticmethod
    def update_from_event_payload(
        db: Session, user_id: int, event_data: dict
    ) -> StripeBillingProfileModel:
        """
        Met à jour le profil Stripe à partir d'un payload d'événement Stripe.
        Gère l'idempotence stricte et le désordre des événements.
        """
        event_id: str | None = event_data.get("id")
        event_created_ts: int | None = event_data.get("created")
        event_created = (
            datetime.fromtimestamp(event_created_ts, tz=timezone.utc) if event_created_ts else None
        )
        event_type: str | None = event_data.get("type")

        # Accès aux données de l'objet Stripe (Subscription ou Customer)
        data_obj = event_data.get("data", {}).get("object", {})
        if not data_obj:
            # Si pas de data.object, on ne peut pas mettre à jour le métier,
            # mais on peut au moins s'assurer que le profil existe.
            return StripeBillingProfileService.get_or_create_profile(db, user_id)

        profile = StripeBillingProfileService.get_or_create_profile(db, user_id)

        # Garde 1 : même event_id -> on ignore (déjà traité)
        if event_id and profile.last_stripe_event_id == event_id:
            return profile

        # Garde 2 : event plus ancien (hors-ordre) -> on ignore
        last_created = profile.last_stripe_event_created
        if last_created and last_created.tzinfo is None:
            last_created = last_created.replace(tzinfo=timezone.utc)

        if event_created is not None and last_created is not None and event_created < last_created:
            return profile

        # Mise à jour des pivots et statuts depuis l'objet Stripe
        # Note: on ne met à jour que si les champs sont présents dans l'objet
        if "customer" in data_obj:
            # Dans un event subscription.*, l'ID customer est dans 'customer'
            profile.stripe_customer_id = data_obj["customer"]
        elif data_obj.get("object") == "customer":
            # Dans un event customer.*, l'ID est 'id'
            profile.stripe_customer_id = data_obj["id"]

        if data_obj.get("object") == "subscription":
            profile.stripe_subscription_id = data_obj.get("id")
            profile.subscription_status = data_obj.get("status")
            # Stripe peut envoyer null → on force un bool pour respecter NOT NULL
            profile.cancel_at_period_end = bool(data_obj.get("cancel_at_period_end") or False)

            period_end_ts = data_obj.get("current_period_end")
            if period_end_ts:
                profile.current_period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc)

            # Extraction du Price ID (premier item de la subscription)
            # Garder la valeur existante si l'event ne fournit pas de price.id valide
            items = data_obj.get("items", {}).get("data", [])
            if items:
                price_id = items[0].get("price", {}).get("id")
                if price_id:
                    profile.stripe_price_id = price_id

        # Mise à jour de l'email de facturation si présent
        email = data_obj.get("email") or data_obj.get("billing_details", {}).get("email")
        if email:
            profile.billing_email = email

        # Recalcul de l'accès produit (entitlement)
        profile.entitlement_plan = derive_entitlement_plan(
            subscription_status=profile.subscription_status,
            stripe_price_id=profile.stripe_price_id,
            current_entitlement=profile.entitlement_plan,
        )

        # Métadonnées d'idempotence et d'audit
        profile.last_stripe_event_id = event_id
        profile.last_stripe_event_created = event_created
        profile.last_stripe_event_type = event_type
        profile.synced_at = datetime.now(timezone.utc)

        # 5. Invalidation du cache de facturation (Story 61.58)
        # Import retardé pour éviter les dépendances circulaires
        from app.services.billing_service import BillingService
        BillingService._invalidate_cached_subscription_status(user_id)

        db.flush()
        return profile

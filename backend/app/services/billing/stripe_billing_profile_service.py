from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.stripe.client import get_stripe_client

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

        object_type = data_obj.get("object")

        # Garde 2 : event plus ancien (hors-ordre) -> on ignore
        last_created = profile.last_stripe_event_created
        if last_created and last_created.tzinfo is None:
            last_created = last_created.replace(tzinfo=timezone.utc)

        can_enrich_checkout_only_snapshot = (
            object_type == "subscription"
            and profile.subscription_status is None
            and profile.last_stripe_event_type == "checkout.session.completed"
        )

        if (
            event_created is not None
            and last_created is not None
            and event_created < last_created
            and not can_enrich_checkout_only_snapshot
        ):
            return profile

        # Mise à jour des pivots et statuts depuis l'objet Stripe
        # Note: on ne met à jour que si les champs sont présents dans l'objet
        if "customer" in data_obj:
            # Dans un event subscription.*, l'ID customer est dans 'customer'
            profile.stripe_customer_id = data_obj["customer"]
        elif data_obj.get("object") == "customer":
            # Dans un event customer.*, l'ID est 'id'
            profile.stripe_customer_id = data_obj["id"]

        if object_type == "subscription":
            StripeBillingProfileService._apply_subscription_snapshot(profile, data_obj)

        elif object_type == "checkout.session":
            profile.stripe_subscription_id = (
                data_obj.get("subscription") or profile.stripe_subscription_id
            )
            StripeBillingProfileService._hydrate_subscription_snapshot_from_checkout(
                profile,
                data_obj,
            )

        elif object_type == "subscription_schedule":
            # Mise à jour directe depuis l'objet schedule
            # (évite un retrieve si c'est l'event schedule lui-même)
            StripeBillingProfileService._update_schedule_fields(profile, data_obj)

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
        profile.synced_at = datetime_provider.utcnow()

        # 5. Invalidation du cache de facturation (Story 61.58)
        # Import retardé pour éviter les dépendances circulaires
        from app.services.billing.service import BillingService

        BillingService._invalidate_cached_subscription_status(user_id)

        db.flush()
        return profile

    @staticmethod
    def _apply_subscription_snapshot(
        profile: StripeBillingProfileModel,
        subscription_data: dict,
    ) -> None:
        profile.stripe_subscription_id = (
            subscription_data.get("id") or profile.stripe_subscription_id
        )
        profile.subscription_status = subscription_data.get("status") or profile.subscription_status
        cancel_at_ts = subscription_data.get("cancel_at")
        cancel_at_period_end_flag = bool(subscription_data.get("cancel_at_period_end") or False)

        period_start_ts = subscription_data.get("current_period_start")
        if period_start_ts:
            profile.current_period_start = datetime.fromtimestamp(period_start_ts, tz=timezone.utc)

        period_end_ts = subscription_data.get("current_period_end")
        if period_end_ts:
            profile.current_period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc)

        has_scheduled_cancellation = cancel_at_period_end_flag or bool(cancel_at_ts)
        profile.cancel_at_period_end = has_scheduled_cancellation

        if cancel_at_ts:
            profile.pending_cancellation_effective_at = datetime.fromtimestamp(
                cancel_at_ts, tz=timezone.utc
            )
        elif has_scheduled_cancellation and profile.current_period_end:
            profile.pending_cancellation_effective_at = profile.current_period_end
        else:
            profile.pending_cancellation_effective_at = None

        schedule_id = subscription_data.get("schedule")
        if schedule_id and profile.subscription_status != "canceled":
            try:
                client = get_stripe_client()
                if client:
                    schedule = client.subscription_schedules.retrieve(schedule_id)
                    StripeBillingProfileService._update_schedule_fields(profile, schedule)
            except Exception as e:
                logger.warning(
                    "stripe_billing: failed to retrieve subscription schedule %s: %s",
                    schedule_id,
                    e,
                )
        else:
            profile.scheduled_plan_code = None
            profile.scheduled_change_effective_at = None

        if profile.subscription_status == "canceled":
            profile.scheduled_plan_code = None
            profile.scheduled_change_effective_at = None
            profile.pending_cancellation_effective_at = None
            profile.cancel_at_period_end = False

        items = subscription_data.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id")
            if price_id:
                profile.stripe_price_id = price_id

    @staticmethod
    def _hydrate_subscription_snapshot_from_checkout(
        profile: StripeBillingProfileModel,
        checkout_session_data: dict,
    ) -> None:
        subscription_id = checkout_session_data.get("subscription")
        if not subscription_id:
            return

        if (
            profile.current_period_start is not None
            and profile.current_period_end is not None
            and profile.subscription_status is not None
        ):
            return

        try:
            client = get_stripe_client()
            if client is None:
                return
            subscription = client.subscriptions.retrieve(subscription_id)
            if hasattr(subscription, "to_dict"):
                subscription_data = subscription.to_dict()
            elif isinstance(subscription, dict):
                subscription_data = subscription
            else:
                to_dict_recursive = getattr(subscription, "to_dict_recursive", None)
                subscription_data = to_dict_recursive() if callable(to_dict_recursive) else {}
            if isinstance(subscription_data, dict) and subscription_data:
                StripeBillingProfileService._apply_subscription_snapshot(
                    profile,
                    subscription_data,
                )
        except Exception as exc:
            logger.warning(
                "stripe_billing: failed to hydrate subscription snapshot from checkout session "
                "subscription_id=%s: %s",
                subscription_id,
                exc,
            )

    @staticmethod
    def _update_schedule_fields(profile: StripeBillingProfileModel, schedule: dict) -> None:
        """Helper pour extraire le plan programmé d'une Subscription Schedule."""
        phases = schedule.get("phases", [])
        if not phases:
            profile.scheduled_plan_code = None
            profile.scheduled_change_effective_at = None
            return

        now_ts = datetime_provider.utcnow().timestamp()
        # On cherche la prochaine phase dont le début est futur
        next_phase = next(
            (p for p in phases if p.get("start_date", 0) > now_ts),
            None,
        )
        if next_phase:
            next_price_items = next_phase.get("items", [])
            if next_price_items:
                next_price_id = next_price_items[0].get("price")
                profile.scheduled_plan_code = STRIPE_PRICE_ENTITLEMENT_MAP.get(next_price_id)
                profile.scheduled_change_effective_at = datetime.fromtimestamp(
                    next_phase["start_date"], tz=timezone.utc
                )
        else:
            profile.scheduled_plan_code = None
            profile.scheduled_change_effective_at = None

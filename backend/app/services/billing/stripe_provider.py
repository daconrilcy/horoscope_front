"""Encapsule l acces au snapshot Stripe utilise par le billing runtime."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.infra.db.models.billing import UserSubscriptionModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel


def get_stripe_billing_profile(db: Session, *, user_id: int) -> StripeBillingProfileModel | None:
    """Recupere le profil Stripe d un utilisateur."""
    return db.scalar(
        select(StripeBillingProfileModel)
        .where(StripeBillingProfileModel.user_id == user_id)
        .limit(1)
    )


def has_usable_stripe_snapshot(profile: StripeBillingProfileModel | None) -> bool:
    """Indique si le profil Stripe porte un snapshot metier exploitable."""
    if profile is None:
        return False
    return bool(
        profile.subscription_status
        or profile.stripe_subscription_id
        or profile.entitlement_plan not in {"", "free"}
    )


def get_latest_subscription(db: Session, user_id: int) -> UserSubscriptionModel | None:
    """Recupere le dernier abonnement legacy d un utilisateur."""
    return db.scalar(
        select(UserSubscriptionModel)
        .where(UserSubscriptionModel.user_id == user_id)
        .order_by(desc(UserSubscriptionModel.updated_at), desc(UserSubscriptionModel.id))
        .limit(1)
    )

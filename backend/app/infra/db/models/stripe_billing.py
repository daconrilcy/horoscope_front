from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StripeBillingProfileModel(Base):
    __tablename__ = "stripe_billing_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_stripe_billing_profiles_user_id"),
        # Partiel : un stripe_customer_id ne peut appartenir qu'à un seul user
        # Implémenter en PostgreSQL via Index partiel
        Index(
            "uq_stripe_billing_profiles_customer_id",
            "stripe_customer_id",
            unique=True,
            postgresql_where=text("stripe_customer_id IS NOT NULL"),
        ),
        Index(
            "uq_stripe_billing_profiles_subscription_id",
            "stripe_subscription_id",
            unique=True,
            postgresql_where=text("stripe_subscription_id IS NOT NULL"),
        ),
        Index("ix_stripe_billing_profiles_stripe_customer_id", "stripe_customer_id"),
        Index("ix_stripe_billing_profiles_stripe_subscription_id", "stripe_subscription_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    # Pivot identité user SaaS ↔ Customer Stripe
    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Pivot accès produit ↔ Subscription Stripe
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Statuts Stripe : trialing|active|past_due|canceled|unpaid|paused|incomplete|etc.
    subscription_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Nouveaux champs pour la cohérence plan effectif vs programmé (Story 61-65)
    scheduled_plan_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    scheduled_change_effective_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pending_cancellation_effective_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Source de vérité accès produit : "free" | "basic" | "premium"
    entitlement_plan: Mapped[str] = mapped_column(String(32), default="free", nullable=False)

    billing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Idempotence webhooks Stripe (tri-champs)
    last_stripe_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_stripe_event_created: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_stripe_event_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Horodatage du dernier snapshot synchronisé depuis Stripe (debug / resync jobs)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

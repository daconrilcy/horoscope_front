from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class StripeWebhookEventModel(Base):
    __tablename__ = "stripe_webhook_events"
    __table_args__ = (
        UniqueConstraint("stripe_event_id", name="uq_stripe_webhook_events_event_id"),
        Index("ix_stripe_webhook_events_event_type", "event_type"),
        Index("ix_stripe_webhook_events_stripe_object_id", "stripe_object_id"),
        Index("ix_stripe_webhook_events_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stripe_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    stripe_object_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    livemode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # processing | processed | failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing")
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base


def _utc_now() -> datetime:
    return datetime_provider.utcnow()


class CanonicalEntitlementMutationAlertEventHandlingEventModel(Base):
    __tablename__ = "canonical_entitlement_mutation_alert_event_handling_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("canonical_entitlement_mutation_alert_events.id"),
        nullable=False,
        index=True,
    )
    handling_status: Mapped[str] = mapped_column(String(32), nullable=False)
    handled_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    handled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utc_now, index=True
    )
    ops_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    suppression_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

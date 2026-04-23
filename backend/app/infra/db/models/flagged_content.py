from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class FlaggedContentModel(Base):
    __tablename__ = "flagged_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    content_type: Mapped[str] = mapped_column(
        String(32)
    )  # e.g. "chat_message", "natal_interpretation"
    content_ref_id: Mapped[str] = mapped_column(String(128))  # ID of the message or interpretation
    excerpt: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending, resolved, dismissed

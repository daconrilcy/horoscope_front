from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class ChatConversationModel(Base):
    __tablename__ = "chat_conversations"
    __table_args__ = (
        Index(
            "ix_chat_conversations_user_status_updated_id",
            "user_id",
            "status",
            "updated_at",
            "id",
        ),
        Index("ix_chat_conversations_user_updated_id", "user_id", "updated_at", "id"),
        Index(
            "ix_chat_conversations_user_persona_active",
            "user_id",
            "persona_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    persona_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_personas.id"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

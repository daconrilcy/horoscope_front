from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    UUID,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base


class UserTokenUsageLogModel(Base):
    """
    Append-only log of token usage for a user.
    Used for auditing, usage reporting, and billing verification.
    """

    __tablename__ = "user_token_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feature_code: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_model: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_total: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    llm_call_log_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_call_logs.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user = relationship("UserModel")
    llm_call_log = relationship("LlmCallLogModel")

    __table_args__ = (
        CheckConstraint(
            "tokens_total = tokens_in + tokens_out", name="check_tokens_total_consistency"
        ),
        CheckConstraint("tokens_in >= 0", name="check_tokens_in_positive"),
        CheckConstraint("tokens_out >= 0", name="check_tokens_out_positive"),
        Index("ix_user_token_usage_logs_user_created_at", "user_id", "created_at"),
        Index(
            "ix_user_token_usage_logs_user_feature_created_at",
            "user_id",
            "feature_code",
            "created_at",
        ),
    )

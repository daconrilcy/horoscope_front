from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base


class LlmValidationStatus(str, Enum):
    VALID = "valid"
    REPAIR_SUCCESS = "repair_success"
    FALLBACK = "fallback"
    ERROR = "error"


def map_status_to_enum(raw_status: str) -> LlmValidationStatus:
    """
    Maps gateway string status to DB Enum values.
    Ensures consistency between runtime and storage.
    """
    if raw_status in ["valid", "omitted"]:
        return LlmValidationStatus.VALID
    if raw_status == "repaired":
        return LlmValidationStatus.REPAIR_SUCCESS
    if raw_status == "fallback":
        return LlmValidationStatus.FALLBACK
    return LlmValidationStatus.ERROR


class LlmCallLogModel(Base):
    """
    Logs every call to the LLM Gateway for observability and evaluation.
    Sensitive user data is NEVER stored in clear text here.
    """

    __tablename__ = "llm_call_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case: Mapped[str] = mapped_column(String(100), nullable=False)

    assembly_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_assembly_configs.id"), nullable=True
    )
    feature: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subfeature: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan: Mapped[str | None] = mapped_column(String(64), nullable=True)
    template_source: Mapped[str | None] = mapped_column(String(32), nullable=True)

    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_prompt_versions.id"), nullable=True
    )
    persona_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_personas.id"), nullable=True
    )

    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="openai")
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd_estimated: Mapped[float] = mapped_column(Float, nullable=False)

    validation_status: Mapped[LlmValidationStatus] = mapped_column(
        SqlEnum(LlmValidationStatus), nullable=False
    )
    repair_attempted: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    request_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False)

    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    environment: Mapped[str] = mapped_column(String(20), nullable=False)  # dev, staging, prod

    evidence_warnings_count: Mapped[int] = mapped_column(Integer, default=0)

    # Operational Observability (Story 66.25)
    pipeline_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    execution_path_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fallback_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    requested_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resolved_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    executed_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    context_compensation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_final: Mapped[int | None] = mapped_column(Integer, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=90),
        nullable=False,
    )

    # Relationships
    prompt_version = relationship("LlmPromptVersionModel")
    persona = relationship("LlmPersonaModel")
    replay_snapshot = relationship(
        "LlmReplaySnapshotModel", back_populates="call_log", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_llm_call_logs_use_case_timestamp", "use_case", "timestamp"),
        Index("ix_llm_call_logs_prompt_v_timestamp", "prompt_version_id", "timestamp"),
        Index("ix_llm_call_logs_status_timestamp", "validation_status", "timestamp"),
    )


class LlmReplaySnapshotModel(Base):
    """
    Stores encrypted input snapshots for a short period to allow replaying requests.
    TTL is much shorter than call logs (7 days).
    """

    __tablename__ = "llm_replay_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("llm_call_logs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    input_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)  # AES-256 encrypted JSON

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=7),
        nullable=False,
    )

    # Relationships
    call_log = relationship("LlmCallLogModel", back_populates="replay_snapshot")

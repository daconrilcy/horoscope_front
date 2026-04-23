# Modèles DB d'observabilité et de rejeu LLM.
"""Déclare les journaux d'appels LLM et les instantanés chiffrés de rejeu."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import ClassVar

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
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base
from app.infra.db.models.llm.llm_constraints import allowed_values_check


class LlmValidationStatus(str, Enum):
    """Liste les états de validation persistés pour une réponse LLM."""

    VALID = "valid"
    REPAIR_SUCCESS = "repair_success"
    FALLBACK = "fallback"
    ERROR = "error"


def map_status_to_enum(raw_status: str) -> LlmValidationStatus:
    """Convertit un statut gateway en statut DB canonique."""
    if raw_status in ["valid", "omitted"]:
        return LlmValidationStatus.VALID
    if raw_status == "repaired":
        return LlmValidationStatus.REPAIR_SUCCESS
    if raw_status == "fallback":
        return LlmValidationStatus.FALLBACK
    return LlmValidationStatus.ERROR


class LlmCallLogModel(Base):
    """Journalise chaque appel gateway LLM sans stocker de données sensibles en clair."""

    __tablename__ = "llm_call_logs"
    authoritative_provider_fields: ClassVar[frozenset[str]] = frozenset(
        {"requested_provider", "resolved_provider", "executed_provider"}
    )

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

    provider_compat: Mapped[str] = mapped_column(String(32), nullable=False, default="openai")
    model: Mapped[str] = mapped_column(String(100), nullable=False)
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
    context_quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    context_compensation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_final: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Operational Hardening (Story 66.33 AC13)
    executed_provider_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    attempt_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider_error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    runtime_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    breaker_state: Mapped[str | None] = mapped_column(String(20), nullable=True)
    breaker_scope: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Release Snapshot Observability (Story 66.32 AC12)
    active_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    active_snapshot_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    manifest_entry_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime_provider.utcnow(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime_provider.utcnow() + timedelta(days=90),
        nullable=False,
    )

    # Relationships
    prompt_version = relationship("LlmPromptVersionModel")
    persona = relationship("LlmPersonaModel")
    replay_snapshot = relationship(
        "LlmReplaySnapshotModel", back_populates="call_log", cascade="all, delete-orphan"
    )
    operational_metadata = relationship(
        "LlmCallLogOperationalMetadataModel",
        back_populates="call_log",
        cascade="all, delete-orphan",
        uselist=False,
    )

    __table_args__ = (
        allowed_values_check(
            "ck_llm_call_logs_provider",
            "provider_compat",
            ("openai", "anthropic"),
        ),
        allowed_values_check(
            "ck_llm_call_logs_environment",
            "environment",
            ("development", "dev", "staging", "production", "prod", "test", "testing", "local"),
        ),
        allowed_values_check(
            "ck_llm_call_logs_pipeline_kind",
            "pipeline_kind",
            ("nominal", "nominal_canonical", "transitional_governance"),
        ),
        allowed_values_check(
            "ck_llm_call_logs_breaker_state",
            "breaker_state",
            ("closed", "open", "half_open"),
        ),
        Index("ix_llm_call_logs_timestamp", "timestamp"),
        Index("ix_llm_call_logs_trace_id", "trace_id"),
        Index("ix_llm_call_logs_scope_timestamp", "feature", "subfeature", "plan", "timestamp"),
        Index("ix_llm_call_logs_active_snapshot_version", "active_snapshot_version"),
        Index("ix_llm_call_logs_executed_provider_timestamp", "executed_provider", "timestamp"),
        Index("ix_llm_call_logs_prompt_v_timestamp", "prompt_version_id", "timestamp"),
        Index("ix_llm_call_logs_status_timestamp", "validation_status", "timestamp"),
    )


class LlmCallLogOperationalMetadataModel(Base):
    """Isole les dimensions operationnelles d'un appel LLM journalise."""

    __tablename__ = "llm_call_log_operational_metadata"
    authoritative_provider_fields: ClassVar[frozenset[str]] = frozenset(
        {"requested_provider", "resolved_provider", "executed_provider"}
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("llm_call_logs.id", ondelete="CASCADE"),
        nullable=False,
    )

    pipeline_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    execution_path_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fallback_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    requested_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resolved_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    executed_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    context_quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    context_compensation_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    max_output_tokens_final: Mapped[int | None] = mapped_column(Integer, nullable=True)
    executed_provider_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    attempt_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider_error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    runtime_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    breaker_state: Mapped[str | None] = mapped_column(String(20), nullable=True)
    breaker_scope: Mapped[str | None] = mapped_column(String(100), nullable=True)
    active_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    active_snapshot_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    manifest_entry_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    call_log = relationship("LlmCallLogModel", back_populates="operational_metadata")

    __table_args__ = (
        UniqueConstraint("call_log_id", name="uq_llm_call_log_operational_metadata_call_log"),
        allowed_values_check(
            "ck_llm_call_log_operational_metadata_pipeline_kind",
            "pipeline_kind",
            ("nominal", "nominal_canonical", "transitional_governance"),
        ),
        allowed_values_check(
            "ck_llm_call_log_operational_metadata_breaker_state",
            "breaker_state",
            ("closed", "open", "half_open"),
        ),
        Index(
            "ix_llm_call_log_operational_metadata_provider",
            "executed_provider",
            "pipeline_kind",
        ),
        Index(
            "ix_llm_call_log_operational_metadata_snapshot",
            "active_snapshot_version",
        ),
    )


class LlmReplaySnapshotModel(Base):
    """Stocke brièvement les entrées chiffrées nécessaires au rejeu contrôlé."""

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
        default=lambda: datetime_provider.utcnow() + timedelta(days=7),
        nullable=False,
    )

    # Relationships
    call_log = relationship("LlmCallLogModel", back_populates="replay_snapshot")

# Modèles DB d'observabilité et de rejeu LLM.
"""Declare les journaux d appels LLM et les instantanes chiffres de rejeu."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import ClassVar

from sqlalchemy import (
    UUID,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_audit import utc_now, utc_now_plus_days
from app.infra.db.models.llm.llm_constraints import allowed_values_check
from app.infra.db.models.llm.llm_field_lengths import (
    CONTEXT_QUALITY_LENGTH,
    ERROR_CODE_LENGTH,
    EXECUTION_PATH_KIND_LENGTH,
    FALLBACK_KIND_LENGTH,
    FEATURE_LENGTH,
    MANIFEST_ENTRY_ID_LENGTH,
    MODEL_LENGTH,
    PIPELINE_KIND_LENGTH,
    PLAN_LENGTH,
    PROVIDER_LENGTH,
    REQUEST_ID_LENGTH,
    SHORT_STATUS_LENGTH,
    SUBFEATURE_LENGTH,
    TRACE_ID_LENGTH,
    USE_CASE_LENGTH,
    VERSION_LENGTH,
)


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
    """Journalise chaque appel gateway LLM sans stocker de donnees sensibles en clair."""

    __tablename__ = "llm_call_logs"
    authoritative_provider_fields: ClassVar[frozenset[str]] = frozenset(
        {"requested_provider", "resolved_provider", "executed_provider"}
    )
    operational_metadata_fields: ClassVar[frozenset[str]] = frozenset(
        {
            "pipeline_kind",
            "execution_path_kind",
            "fallback_kind",
            "requested_provider",
            "resolved_provider",
            "executed_provider",
            "context_quality",
            "context_compensation_status",
            "max_output_tokens_source",
            "max_output_tokens_final",
            "executed_provider_mode",
            "attempt_count",
            "provider_error_code",
            "runtime_error_code",
            "breaker_state",
            "breaker_scope",
            "active_snapshot_id",
            "active_snapshot_version",
            "manifest_entry_id",
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case: Mapped[str] = mapped_column(String(USE_CASE_LENGTH), nullable=False)

    assembly_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_assembly_configs.id"), nullable=True
    )
    feature: Mapped[str | None] = mapped_column(String(FEATURE_LENGTH), nullable=True)
    subfeature: Mapped[str | None] = mapped_column(String(SUBFEATURE_LENGTH), nullable=True)
    plan: Mapped[str | None] = mapped_column(String(PLAN_LENGTH), nullable=True)
    template_source: Mapped[str | None] = mapped_column(
        String(CONTEXT_QUALITY_LENGTH), nullable=True
    )

    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_prompt_versions.id"), nullable=True
    )
    persona_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_personas.id"), nullable=True
    )

    model: Mapped[str] = mapped_column(String(MODEL_LENGTH), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd_estimated: Mapped[float] = mapped_column(Float, nullable=False)

    validation_status: Mapped[LlmValidationStatus] = mapped_column(
        SqlEnum(LlmValidationStatus), nullable=False
    )
    repair_attempted: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    request_id: Mapped[str] = mapped_column(String(REQUEST_ID_LENGTH), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(TRACE_ID_LENGTH), nullable=False)

    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    environment: Mapped[str] = mapped_column(
        String(SHORT_STATUS_LENGTH), nullable=False
    )  # dev, staging, prod

    evidence_warnings_count: Mapped[int] = mapped_column(Integer, default=0)

    timestamp: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        default=utc_now_plus_days(90),
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

    def __init__(self, **kwargs: object) -> None:
        """Isole explicitement les champs operationnels dans la relation one-to-one dediee."""
        metadata_kwargs = {
            key: kwargs.pop(key)
            for key in tuple(kwargs)
            if key in self.operational_metadata_fields and kwargs.get(key) is not None
        }

        super().__init__(**kwargs)

        if metadata_kwargs:
            current = self.operational_metadata or LlmCallLogOperationalMetadataModel()
            for key, value in metadata_kwargs.items():
                setattr(current, key, value)
            self.operational_metadata = current

    def _get_operational_value(self, field_name: str) -> object | None:
        """Lit un champ operationnel depuis la relation de compatibilite dediee."""
        if self.operational_metadata is None:
            return None
        return getattr(self.operational_metadata, field_name)

    def _set_operational_value(self, field_name: str, value: object | None) -> None:
        """Ecrit un champ operationnel dans la relation dediee sans repolluer la table coeur."""
        if self.operational_metadata is None:
            self.operational_metadata = LlmCallLogOperationalMetadataModel()
        setattr(self.operational_metadata, field_name, value)

    __table_args__ = (
        allowed_values_check(
            "ck_llm_call_logs_environment",
            "environment",
            ("development", "dev", "staging", "production", "prod", "test", "testing", "local"),
        ),
        Index("ix_llm_call_logs_timestamp", "timestamp"),
        Index("ix_llm_call_logs_trace_id", "trace_id"),
        Index("ix_llm_call_logs_scope_timestamp", "feature", "subfeature", "plan", "timestamp"),
        Index("ix_llm_call_logs_prompt_v_timestamp", "prompt_version_id", "timestamp"),
        Index("ix_llm_call_logs_status_timestamp", "validation_status", "timestamp"),
    )

    @property
    def manifest_entry_id(self) -> str | None:
        return self._get_operational_value("manifest_entry_id")

    @manifest_entry_id.setter
    def manifest_entry_id(self, value: str | None) -> None:
        self._set_operational_value("manifest_entry_id", value)

    @property
    def active_snapshot_version(self) -> str | None:
        return self._get_operational_value("active_snapshot_version")

    @active_snapshot_version.setter
    def active_snapshot_version(self, value: str | None) -> None:
        self._set_operational_value("active_snapshot_version", value)

    @property
    def active_snapshot_id(self) -> uuid.UUID | None:
        return self._get_operational_value("active_snapshot_id")

    @active_snapshot_id.setter
    def active_snapshot_id(self, value: uuid.UUID | None) -> None:
        self._set_operational_value("active_snapshot_id", value)

    @property
    def pipeline_kind(self) -> str | None:
        return self._get_operational_value("pipeline_kind")

    @pipeline_kind.setter
    def pipeline_kind(self, value: str | None) -> None:
        self._set_operational_value("pipeline_kind", value)

    @property
    def execution_path_kind(self) -> str | None:
        return self._get_operational_value("execution_path_kind")

    @execution_path_kind.setter
    def execution_path_kind(self, value: str | None) -> None:
        self._set_operational_value("execution_path_kind", value)

    @property
    def fallback_kind(self) -> str | None:
        return self._get_operational_value("fallback_kind")

    @fallback_kind.setter
    def fallback_kind(self, value: str | None) -> None:
        self._set_operational_value("fallback_kind", value)

    @property
    def requested_provider(self) -> str | None:
        return self._get_operational_value("requested_provider")

    @requested_provider.setter
    def requested_provider(self, value: str | None) -> None:
        self._set_operational_value("requested_provider", value)

    @property
    def resolved_provider(self) -> str | None:
        return self._get_operational_value("resolved_provider")

    @resolved_provider.setter
    def resolved_provider(self, value: str | None) -> None:
        self._set_operational_value("resolved_provider", value)

    @property
    def executed_provider(self) -> str | None:
        return self._get_operational_value("executed_provider")

    @executed_provider.setter
    def executed_provider(self, value: str | None) -> None:
        self._set_operational_value("executed_provider", value)

    @property
    def context_quality(self) -> str | None:
        return self._get_operational_value("context_quality")

    @context_quality.setter
    def context_quality(self, value: str | None) -> None:
        self._set_operational_value("context_quality", value)

    @property
    def context_compensation_status(self) -> str | None:
        return self._get_operational_value("context_compensation_status")

    @context_compensation_status.setter
    def context_compensation_status(self, value: str | None) -> None:
        self._set_operational_value("context_compensation_status", value)

    @property
    def max_output_tokens_source(self) -> str | None:
        return self._get_operational_value("max_output_tokens_source")

    @max_output_tokens_source.setter
    def max_output_tokens_source(self, value: str | None) -> None:
        self._set_operational_value("max_output_tokens_source", value)

    @property
    def max_output_tokens_final(self) -> int | None:
        return self._get_operational_value("max_output_tokens_final")

    @max_output_tokens_final.setter
    def max_output_tokens_final(self, value: int | None) -> None:
        self._set_operational_value("max_output_tokens_final", value)

    @property
    def executed_provider_mode(self) -> str | None:
        return self._get_operational_value("executed_provider_mode")

    @executed_provider_mode.setter
    def executed_provider_mode(self, value: str | None) -> None:
        self._set_operational_value("executed_provider_mode", value)

    @property
    def attempt_count(self) -> int | None:
        return self._get_operational_value("attempt_count")

    @attempt_count.setter
    def attempt_count(self, value: int | None) -> None:
        self._set_operational_value("attempt_count", value)

    @property
    def provider_error_code(self) -> str | None:
        return self._get_operational_value("provider_error_code")

    @provider_error_code.setter
    def provider_error_code(self, value: str | None) -> None:
        self._set_operational_value("provider_error_code", value)

    @property
    def runtime_error_code(self) -> str | None:
        return self._get_operational_value("runtime_error_code")

    @runtime_error_code.setter
    def runtime_error_code(self, value: str | None) -> None:
        self._set_operational_value("runtime_error_code", value)

    @property
    def breaker_state(self) -> str | None:
        return self._get_operational_value("breaker_state")

    @breaker_state.setter
    def breaker_state(self, value: str | None) -> None:
        self._set_operational_value("breaker_state", value)

    @property
    def breaker_scope(self) -> str | None:
        return self._get_operational_value("breaker_scope")

    @breaker_scope.setter
    def breaker_scope(self, value: str | None) -> None:
        self._set_operational_value("breaker_scope", value)


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

    pipeline_kind: Mapped[str | None] = mapped_column(String(PIPELINE_KIND_LENGTH), nullable=True)
    execution_path_kind: Mapped[str | None] = mapped_column(
        String(EXECUTION_PATH_KIND_LENGTH), nullable=True
    )
    fallback_kind: Mapped[str | None] = mapped_column(String(FALLBACK_KIND_LENGTH), nullable=True)
    requested_provider: Mapped[str | None] = mapped_column(String(PROVIDER_LENGTH), nullable=True)
    resolved_provider: Mapped[str | None] = mapped_column(String(PROVIDER_LENGTH), nullable=True)
    executed_provider: Mapped[str | None] = mapped_column(String(PROVIDER_LENGTH), nullable=True)
    context_quality: Mapped[str | None] = mapped_column(
        String(CONTEXT_QUALITY_LENGTH), nullable=True
    )
    context_compensation_status: Mapped[str | None] = mapped_column(
        String(CONTEXT_QUALITY_LENGTH), nullable=True
    )
    max_output_tokens_source: Mapped[str | None] = mapped_column(
        String(CONTEXT_QUALITY_LENGTH), nullable=True
    )
    max_output_tokens_final: Mapped[int | None] = mapped_column(Integer, nullable=True)
    executed_provider_mode: Mapped[str | None] = mapped_column(
        String(PROVIDER_LENGTH), nullable=True
    )
    attempt_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider_error_code: Mapped[str | None] = mapped_column(
        String(ERROR_CODE_LENGTH), nullable=True
    )
    runtime_error_code: Mapped[str | None] = mapped_column(String(ERROR_CODE_LENGTH), nullable=True)
    breaker_state: Mapped[str | None] = mapped_column(String(SHORT_STATUS_LENGTH), nullable=True)
    breaker_scope: Mapped[str | None] = mapped_column(String(USE_CASE_LENGTH), nullable=True)
    active_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    active_snapshot_version: Mapped[str | None] = mapped_column(
        String(VERSION_LENGTH), nullable=True
    )
    manifest_entry_id: Mapped[str | None] = mapped_column(
        String(MANIFEST_ENTRY_ID_LENGTH), nullable=True
    )

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
        default=utc_now_plus_days(7),
        nullable=False,
    )

    # Relationships
    call_log = relationship("LlmCallLogModel", back_populates="replay_snapshot")

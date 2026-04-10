from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    UUID,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.infra.db.base import Base
from app.infra.db.models.llm_prompt import PromptStatus


class LlmExecutionProfileModel(Base):
    """
    Admin-managed execution parameters for LLM engines (Story 66.11).
    Decouples engine choices from prompt text.
    """

    __tablename__ = "llm_execution_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Admin label

    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="openai")
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Internal stable profiles (Story 66.11 D4)
    reasoning_profile: Mapped[str] = mapped_column(String(20), nullable=False, default="off")
    verbosity_profile: Mapped[str] = mapped_column(String(20), nullable=False, default="balanced")
    output_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="free_text")
    tool_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="none")

    max_output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    fallback_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("llm_execution_profiles.id"), nullable=True
    )

    # Target (waterfall resolution)
    feature: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subfeature: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    plan: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    status: Mapped[PromptStatus] = mapped_column(
        String(20), nullable=False, default=PromptStatus.DRAFT
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    @validates("status")
    def validate_status_change(self, key: str, value: PromptStatus) -> PromptStatus:
        """
        AC3.1: Enforce provider support when transition to PUBLISHED.
        AC5: Reject legacy nominal features on publication.
        """
        if value == PromptStatus.PUBLISHED:
            from app.llm_orchestration.feature_taxonomy import (
                NATAL_CANONICAL_FEATURE,
                assert_nominal_feature_allowed,
                is_natal_subfeature_canonical,
            )
            from app.llm_orchestration.services.observability_service import log_governance_event
            from app.llm_orchestration.supported_providers import is_provider_supported

            # AC2, AC5: Validate feature taxonomy
            if self.feature:
                assert_nominal_feature_allowed(self.feature)

                # AC6: Ensure subfeature is canonical if feature is natal
                if self.feature == NATAL_CANONICAL_FEATURE and self.subfeature:
                    if not is_natal_subfeature_canonical(self.subfeature):
                        raise ValueError(
                            f"Subfeature '{self.subfeature}' is not canonical "
                            f"for feature '{self.feature}'."
                        )

            # AC3.1, AC5: Enforce provider support when transition to PUBLISHED.
            # We strictly reject on nominal paths, but tolerate on non-nominal/test paths.
            CANONICAL_FAMILIES = {"chat", "guidance", "natal", "horoscope_daily"}
            is_nominal = self.feature in CANONICAL_FAMILIES
            provider_to_check = self.provider or "openai"

            if not is_provider_supported(provider_to_check):
                if is_nominal:
                    log_governance_event(
                        event_type="publish_rejected",
                        provider=provider_to_check,
                        feature=self.feature,
                        is_nominal=True,
                    )
                    raise ValueError(
                        f"ExecutionProfile cannot be published for nominal feature "
                        f"'{self.feature}': Provider '{provider_to_check}' "
                        "is not nominally supported."
                    )
                else:
                    # Non-nominal: we allow but log a warning (AC5)
                    log_governance_event(
                        event_type="non_nominal_publish_tolerated",
                        provider=provider_to_check,
                        feature=self.feature,
                        is_nominal=False,
                    )
                    import logging

                    logging.getLogger(__name__).warning(
                        "ExecutionProfile published with non-nominal provider '%s' "
                        "for feature '%s'. This will trigger fallback at runtime.",
                        provider_to_check,
                        self.feature,
                    )
        return value

    # Relationship for fallback
    fallback_profile = relationship("LlmExecutionProfileModel", remote_side=[id])

    __table_args__ = (
        Index(
            "ix_llm_execution_profile_active_unique",
            "feature",
            func.coalesce(subfeature, ""),
            func.coalesce(plan, ""),
            unique=True,
            postgresql_where=(status == PromptStatus.PUBLISHED),
            sqlite_where=(status == PromptStatus.PUBLISHED),
        ),
        Index("ix_llm_execution_profiles_feature", "feature"),
        Index("ix_llm_execution_profiles_status", "status"),
    )

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.datetime_provider import datetime_provider
from app.infra.db.base import Base
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus


def utc_now() -> datetime:
    return datetime_provider.utcnow()


class PromptAssemblyConfigModel(Base):
    __tablename__ = "llm_assembly_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature: Mapped[str] = mapped_column(String(64), index=True)
    subfeature: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    plan: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    locale: Mapped[str] = mapped_column(String(16), index=True, default="fr-FR")

    feature_template_ref: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("llm_prompt_versions.id", ondelete="RESTRICT")
    )
    subfeature_template_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_prompt_versions.id", ondelete="SET NULL"), nullable=True
    )
    persona_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_personas.id", ondelete="SET NULL"), nullable=True
    )
    execution_profile_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("llm_execution_profiles.id", ondelete="SET NULL"), nullable=True
    )
    plan_rules_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    execution_config: Mapped[dict] = mapped_column(JSON)
    output_contract_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    length_budget: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    interaction_mode: Mapped[str] = mapped_column(String(16), default="structured")
    user_question_policy: Mapped[str] = mapped_column(String(16), default="none")
    fallback_use_case: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    feature_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    subfeature_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    persona_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    plan_rules_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    status: Mapped[PromptStatus] = mapped_column(String(16), index=True, default=PromptStatus.DRAFT)

    created_by: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @validates("status")
    def validate_status_change(self, key: str, value: PromptStatus) -> PromptStatus:
        """
        AC5: Reject legacy nominal features on publication.
        """
        if value == PromptStatus.PUBLISHED:
            from app.domain.llm.governance.feature_taxonomy import (
                NATAL_CANONICAL_FEATURE,
                assert_nominal_feature_allowed,
                is_natal_subfeature_canonical,
            )

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
        return value

    # Relationships
    feature_template: Mapped[LlmPromptVersionModel] = relationship(
        "LlmPromptVersionModel", foreign_keys=[feature_template_ref]
    )
    subfeature_template: Mapped[Optional[LlmPromptVersionModel]] = relationship(
        "LlmPromptVersionModel", foreign_keys=[subfeature_template_ref]
    )
    persona: Mapped[Optional[LlmPersonaModel]] = relationship(
        "LlmPersonaModel", foreign_keys=[persona_ref]
    )

    __table_args__ = (
        Index(
            "ix_llm_assembly_config_active_unique",
            "feature",
            func.coalesce(subfeature, ""),
            func.coalesce(plan, ""),
            "locale",
            unique=True,
            postgresql_where=(status == PromptStatus.PUBLISHED),
            sqlite_where=(status == PromptStatus.PUBLISHED),
        ),
        Index("ix_llm_assembly_configs_created_at", "created_at"),
    )

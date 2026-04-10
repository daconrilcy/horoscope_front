from __future__ import annotations

import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.llm_orchestration.admin_models import (
    PromptAssemblyConfig,
    PromptAssemblyPreview,
)
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import (
    build_assembly_preview,
    validate_placeholders,
)
from app.llm_orchestration.services.observability_service import log_governance_event

logger = logging.getLogger(__name__)


class AssemblyAdminService:
    """Service for admin management of LLM Prompt Assembly configurations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.registry = AssemblyRegistry(session)

    async def _execute(self, stmt):
        """Unified executor for sync/async sessions."""
        from sqlalchemy.ext.asyncio import AsyncSession

        if isinstance(self.session, AsyncSession):
            return await self.session.execute(stmt)
        return self.session.execute(stmt)

    async def list_configs(self, feature: Optional[str] = None) -> List[PromptAssemblyConfigModel]:
        """List all assembly configurations, optionally filtered by feature."""
        stmt = select(PromptAssemblyConfigModel).options(
            selectinload(PromptAssemblyConfigModel.feature_template),
            selectinload(PromptAssemblyConfigModel.subfeature_template),
            selectinload(PromptAssemblyConfigModel.persona),
        )
        if feature:
            stmt = stmt.where(PromptAssemblyConfigModel.feature == feature)

        result = await self._execute(stmt)
        return list(result.scalars().all())

    async def get_config(self, config_id: uuid.UUID) -> Optional[PromptAssemblyConfigModel]:
        """Get a specific assembly configuration by ID."""
        return await self.registry.get_config_by_id(config_id)

    async def create_draft(
        self, config_in: PromptAssemblyConfig, created_by: str
    ) -> PromptAssemblyConfigModel:
        """Create a new draft assembly configuration."""
        # AC6: Validate placeholders for BOTH templates before saving draft

        # 1. Feature Template
        stmt = select(LlmPromptVersionModel).where(
            LlmPromptVersionModel.id == config_in.feature_template_ref
        )
        res = await self._execute(stmt)
        fv = res.scalar_one_or_none()
        if fv:
            invalid = validate_placeholders(fv.developer_prompt, config_in.feature)
            if invalid:
                raise ValueError(f"Invalid placeholders in feature template: {', '.join(invalid)}")

        # 2. Subfeature Template (if provided)
        if config_in.subfeature_template_ref:
            stmt_sub = select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.id == config_in.subfeature_template_ref
            )
            res_sub = await self._execute(stmt_sub)
            sv = res_sub.scalar_one_or_none()
            if sv:
                invalid_sub = validate_placeholders(sv.developer_prompt, config_in.feature)
                if invalid_sub:
                    raise ValueError(
                        f"Invalid placeholders in subfeature template: {', '.join(invalid_sub)}"
                    )

        new_config = PromptAssemblyConfigModel(
            feature=config_in.feature,
            subfeature=config_in.subfeature,
            plan=config_in.plan,
            locale=config_in.locale,
            feature_template_ref=config_in.feature_template_ref,
            subfeature_template_ref=config_in.subfeature_template_ref,
            persona_ref=config_in.persona_ref,
            plan_rules_ref=config_in.plan_rules_ref,
            execution_config=config_in.execution_config.model_dump(),
            output_contract_ref=config_in.output_contract_ref,
            interaction_mode=config_in.interaction_mode,
            user_question_policy=config_in.user_question_policy,
            fallback_use_case=config_in.fallback_use_case,
            feature_enabled=config_in.feature_enabled,
            subfeature_enabled=config_in.subfeature_enabled,
            persona_enabled=config_in.persona_enabled,
            plan_rules_enabled=config_in.plan_rules_enabled,
            status=PromptStatus.DRAFT,
            created_by=created_by,
        )
        self.session.add(new_config)
        await self.session.flush()
        return new_config

    async def _validate_provider_support(self, config: PromptAssemblyConfigModel) -> str:
        """
        Validates that the provider for this config is nominally supported.
        Returns the resolved provider name.
        """
        from app.llm_orchestration.supported_providers import is_provider_supported

        provider = "openai"  # Default

        if config.execution_profile_ref:
            from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel

            stmt_p = select(LlmExecutionProfileModel.provider).where(
                LlmExecutionProfileModel.id == config.execution_profile_ref
            )
            res_p = await self._execute(stmt_p)
            profile_provider = res_p.scalar_one_or_none()
            if profile_provider:
                provider = profile_provider
        else:
            # Check if provider is explicitly in execution_config (even if not in current admin_models)
            provider = config.execution_config.get("provider", "openai")

        if not is_provider_supported(provider):
            log_governance_event(
                event_type="publish_rejected",
                provider=provider,
                feature=config.feature,
                is_nominal=True,
            )
            logger.error(
                "assembly_publication_rejected_unsupported_provider config_id=%s provider=%s",
                str(config.id),
                provider,
            )
            raise ValueError(
                f"Publication rejected: Provider '{provider}' is not nominally supported."
            )

        return provider

    async def publish_config(self, config_id: uuid.UUID) -> Tuple[PromptAssemblyConfigModel, int]:
        """
        Publish a configuration using registry.
        """
        # AC6: Re-validate ALL templates before publishing
        config = await self.get_config(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")

        # Story 66.22 AC3: Validate provider support on publication
        await self._validate_provider_support(config)

        invalid = validate_placeholders(config.feature_template.developer_prompt, config.feature)
        if invalid:
            raise ValueError(f"Invalid placeholders in feature template: {', '.join(invalid)}")

        if config.subfeature_template:
            invalid_sub = validate_placeholders(
                config.subfeature_template.developer_prompt, config.feature
            )
            if invalid_sub:
                raise ValueError(
                    f"Invalid placeholders in subfeature template: {', '.join(invalid_sub)}"
                )

        return await self.registry.publish_config(config_id)

    async def rollback_config(
        self,
        feature: str,
        subfeature: Optional[str],
        plan: Optional[str],
        locale: str,
        target_id: uuid.UUID,
    ) -> PromptAssemblyConfigModel:
        """Rollback using registry."""
        # Story 66.22 AC3: Validate provider support on rollback (Finding 2)
        config = await self.get_config(target_id)
        if config:
            await self._validate_provider_support(config)

        return await self.registry.rollback_config(feature, subfeature, plan, locale, target_id)

    async def get_assembly_preview(self, config_id: uuid.UUID) -> PromptAssemblyPreview:
        """
        Build a full preview of an assembly configuration.
        Implements AC7, AC12.
        """
        config = await self.get_config(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")

        return build_assembly_preview(config)

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import PromptStatus, LlmPromptVersionModel
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.llm_orchestration.admin_models import (
    PromptAssemblyConfig,
    PromptAssemblyPreview,
    PromptAssemblyTarget,
    ResolvedAssembly,
    PlaceholderInfo,
    ExecutionConfigAdmin,
)
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.assembly_resolver import (
    assemble_developer_prompt,
    build_assembly_preview,
    resolve_assembly,
    validate_placeholders,
)
from app.llm_orchestration.services.prompt_renderer import PromptRenderer
from app.llm_orchestration.policies.hard_policy import get_hard_policy


class AssemblyAdminService:
    """Service for admin management of LLM Prompt Assembly configurations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.registry = AssemblyRegistry(session)

    async def list_configs(self, feature: Optional[str] = None) -> List[PromptAssemblyConfigModel]:
        """List all assembly configurations, optionally filtered by feature."""
        stmt = select(PromptAssemblyConfigModel).options(
            selectinload(PromptAssemblyConfigModel.feature_template),
            selectinload(PromptAssemblyConfigModel.subfeature_template),
            selectinload(PromptAssemblyConfigModel.persona),
        )
        if feature:
            stmt = stmt.where(PromptAssemblyConfigModel.feature == feature)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_config(self, config_id: uuid.UUID) -> Optional[PromptAssemblyConfigModel]:
        """Get a specific assembly configuration by ID."""
        return await self.registry.get_config_by_id(config_id)

    async def create_draft(self, config_in: PromptAssemblyConfig, created_by: str) -> PromptAssemblyConfigModel:
        """Create a new draft assembly configuration."""
        # AC6: Validate placeholders before saving draft
        # 1. Fetch feature template to get developer_prompt
        stmt = select(LlmPromptVersionModel).where(LlmPromptVersionModel.id == config_in.feature_template_ref)
        res = await self.session.execute(stmt)
        fv = res.scalar_one_or_none()
        if fv:
            invalid = validate_placeholders(fv.developer_prompt, config_in.feature)
            if invalid:
                raise ValueError(f"Invalid placeholders in feature template: {', '.join(invalid)}")

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

    async def publish_config(self, config_id: uuid.UUID) -> Tuple[PromptAssemblyConfigModel, int]:
        """
        Publish a configuration using registry.
        """
        # AC6: Re-validate placeholders before publishing
        config = await self.get_config(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")
            
        invalid = validate_placeholders(config.feature_template.developer_prompt, config.feature)
        if invalid:
            raise ValueError(f"Invalid placeholders in feature template: {', '.join(invalid)}")
            
        return await self.registry.publish_config(config_id)

    async def rollback_config(self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str, target_id: uuid.UUID) -> PromptAssemblyConfigModel:
        """Rollback using registry."""
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

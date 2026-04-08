from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import PromptStatus


class AssemblyRegistry:
    """Registry for managing and resolving LLM Prompt Assembly configurations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _execute(self, stmt):
        """Unified executor for sync/async sessions."""
        from sqlalchemy.ext.asyncio import AsyncSession
        if isinstance(self.session, AsyncSession):
            return await self.session.execute(stmt)
        return self.session.execute(stmt)

    async def get_active_config(
        self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str = "fr-FR"
    ) -> Optional[PromptAssemblyConfigModel]:
        """
        Resolve the best matching active (PUBLISHED) assembly config using waterfall logic.
        Waterfall: (feature, subfeature, plan) -> (feature, subfeature, None) -> (feature, None, None)
        """
        # Search patterns in order of priority
        search_patterns = [
            (feature, subfeature, plan),
            (feature, subfeature, None),
            (feature, None, None),
        ]

        for f, sf, p in search_patterns:
            stmt = (
                select(PromptAssemblyConfigModel)
                .where(
                    and_(
                        PromptAssemblyConfigModel.feature == f,
                        PromptAssemblyConfigModel.subfeature == sf,
                        PromptAssemblyConfigModel.plan == p,
                        PromptAssemblyConfigModel.locale == locale,
                        PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                    )
                )
                .options(
                    selectinload(PromptAssemblyConfigModel.feature_template),
                    selectinload(PromptAssemblyConfigModel.subfeature_template),
                    selectinload(PromptAssemblyConfigModel.persona),
                )
            )
            result = await self._execute(stmt)
            config = result.scalar_one_or_none()
            if config:
                return config

        return None

    async def get_config_by_id(self, assembly_id: uuid.UUID) -> Optional[PromptAssemblyConfigModel]:
        """Fetch an assembly config by its unique ID."""
        stmt = (
            select(PromptAssemblyConfigModel)
            .where(PromptAssemblyConfigModel.id == assembly_id)
            .options(
                selectinload(PromptAssemblyConfigModel.feature_template),
                selectinload(PromptAssemblyConfigModel.subfeature_template),
                selectinload(PromptAssemblyConfigModel.persona),
            )
        )
        result = await self._execute(stmt)
        return result.scalar_one_or_none()

    async def publish_config(self, config_id: uuid.UUID) -> PromptAssemblyConfigModel:
        """
        Publish a configuration, archiving the previous active one for the same target.
        Implements AC9.
        """
        config = await self.get_config_by_id(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")

        # 1. Archive current active config for this target
        from sqlalchemy import update
        archive_stmt = (
            update(PromptAssemblyConfigModel)
            .where(
                and_(
                    PromptAssemblyConfigModel.feature == config.feature,
                    PromptAssemblyConfigModel.subfeature == config.subfeature,
                    PromptAssemblyConfigModel.plan == config.plan,
                    PromptAssemblyConfigModel.locale == config.locale,
                    PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                    PromptAssemblyConfigModel.id != config_id
                )
            )
            .values(status=PromptStatus.ARCHIVED)
        )
        archived_result = await self._execute(archive_stmt)
        archived_count = archived_result.rowcount if hasattr(archived_result, "rowcount") else 0

        # 2. Publish this config
        config.status = PromptStatus.PUBLISHED
        from datetime import datetime, timezone
        config.published_at = datetime.now(timezone.utc)
        
        # 3. Handle session commit/flush
        from sqlalchemy.ext.asyncio import AsyncSession
        if isinstance(self.session, AsyncSession):
            await self.session.commit()
        else:
            self.session.commit()
            
        return config, archived_count

    async def rollback_config(self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str, target_id: uuid.UUID) -> PromptAssemblyConfigModel:
        """
        Rollback to a specific archived configuration.
        """
        # Follows pattern: archive current published, publish target archived
        current_active = await self.get_active_config(feature, subfeature, plan, locale)
        if current_active:
            current_active.status = PromptStatus.ARCHIVED
            
        target_config = await self.get_config_by_id(target_id)
        if not target_config:
            raise ValueError(f"Target config {target_id} not found")
            
        target_config.status = PromptStatus.PUBLISHED
        from datetime import datetime, timezone
        target_config.published_at = datetime.now(timezone.utc)
        
        from sqlalchemy.ext.asyncio import AsyncSession
        if isinstance(self.session, AsyncSession):
            await self.session.commit()
        else:
            self.session.commit()
            
        return target_config

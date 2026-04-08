from __future__ import annotations

import uuid
import logging
import time
from typing import Optional, Dict, Tuple, Any

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.db.models.llm_persona import LlmPersonaModel

logger = logging.getLogger(__name__)

# AC8: TTL Cache for resolved configs
# M4 Fix: Store serialized dicts instead of ORM instances
_ASSEMBLY_CACHE: Dict[str, Tuple[Dict[str, Any], float]] = {}
CACHE_TTL = 60.0


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

    def _serialize_config(self, config: PromptAssemblyConfigModel) -> Dict[str, Any]:
        """Convert ORM model to a serializable dict for cache (including relationships)."""
        data = {
            "id": config.id,
            "feature": config.feature,
            "subfeature": config.subfeature,
            "plan": config.plan,
            "locale": config.locale,
            "feature_template_ref": config.feature_template_ref,
            "subfeature_template_ref": config.subfeature_template_ref,
            "persona_ref": config.persona_ref,
            "plan_rules_ref": config.plan_rules_ref,
            "execution_config": config.execution_config,
            "output_contract_ref": config.output_contract_ref,
            "feature_enabled": config.feature_enabled,
            "subfeature_enabled": config.subfeature_enabled,
            "persona_enabled": config.persona_enabled,
            "plan_rules_enabled": config.plan_rules_enabled,
            "status": config.status,
            "created_by": config.created_by,
            "created_at": config.created_at,
            "published_at": config.published_at,
        }
        
        # Serialize relationships if loaded
        if config.feature_template:
            data["_feature_template"] = {
                "id": config.feature_template.id,
                "use_case_key": config.feature_template.use_case_key,
                "developer_prompt": config.feature_template.developer_prompt,
                "model": config.feature_template.model,
            }
        if config.subfeature_template:
            data["_subfeature_template"] = {
                "id": config.subfeature_template.id,
                "use_case_key": config.subfeature_template.use_case_key,
                "developer_prompt": config.subfeature_template.developer_prompt,
                "model": config.subfeature_template.model,
            }
        if config.persona:
            data["_persona"] = {
                "id": config.persona.id,
                "name": config.persona.name,
                "description": config.persona.description,
                "tone": config.persona.tone,
                "verbosity": config.persona.verbosity,
            }
        return data

    def _reconstruct_config(self, data: Dict[str, Any]) -> PromptAssemblyConfigModel:
        """Reconstruct a detached ORM instance from serialized dict."""
        data_copy = data.copy()
        feat_data = data_copy.pop("_feature_template", None)
        sub_data = data_copy.pop("_subfeature_template", None)
        pers_data = data_copy.pop("_persona", None)
        
        config = PromptAssemblyConfigModel(**data_copy)
        if feat_data:
            config.feature_template = LlmPromptVersionModel(**feat_data)
        if sub_data:
            config.subfeature_template = LlmPromptVersionModel(**sub_data)
        if pers_data:
            config.persona = LlmPersonaModel(**pers_data)
            
        return config

    async def get_active_config(
        self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str = "fr-FR"
    ) -> Optional[PromptAssemblyConfigModel]:
        """
        Resolve the best matching active (PUBLISHED) assembly config using waterfall logic.
        Waterfall: (feature, subfeature, plan) -> (feature, subfeature, None) -> (feature, None, None)
        """
        cache_key = f"{feature}:{subfeature or ''}:{plan or ''}:{locale}"
        now = time.time()
        
        # AC8: Cache lookup
        if cache_key in _ASSEMBLY_CACHE:
            data, expiry = _ASSEMBLY_CACHE[cache_key]
            if now < expiry:
                # Return a detached instance
                return self._reconstruct_config(data)
            del _ASSEMBLY_CACHE[cache_key]

        # Search patterns in order of priority
        search_patterns = [
            (feature, subfeature, plan),
            (feature, subfeature, None),
            (feature, None, None),
        ]

        resolved_config = None
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
                resolved_config = config
                break

        if resolved_config:
            # AC8: Update cache with serialized data
            _ASSEMBLY_CACHE[cache_key] = (self._serialize_config(resolved_config), now + CACHE_TTL)
            
        return resolved_config

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

    async def publish_config(self, config_id: uuid.UUID) -> Tuple[PromptAssemblyConfigModel, int]:
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
            
        # H1: Invalidate cache on publish
        self.invalidate_cache()
            
        return config, archived_count

    async def rollback_config(self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str, target_id: uuid.UUID) -> PromptAssemblyConfigModel:
        """
        Rollback to a specific archived configuration.
        """
        # L2 Fix: Single transaction for atomicity
        async def _do_rollback():
            current_active = await self.get_active_config(feature, subfeature, plan, locale)
            if current_active:
                current_active.status = PromptStatus.ARCHIVED
                
            target_config = await self.get_config_by_id(target_id)
            if not target_config:
                raise ValueError(f"Target config {target_id} not found")
                
            target_config.status = PromptStatus.PUBLISHED
            from datetime import datetime, timezone
            target_config.published_at = datetime.now(timezone.utc)
            return target_config

        if isinstance(self.session, AsyncSession):
            # Atomic transaction
            res = await _do_rollback()
            await self.session.commit()
        else:
            res = await _do_rollback()
            self.session.commit()
            
        # H1: Invalidate cache on rollback
        self.invalidate_cache()
        return res

    def invalidate_cache(self) -> None:
        """H1: Clears the in-memory assembly configuration cache."""
        _ASSEMBLY_CACHE.clear()
        logger.info("assembly_registry_cache_invalidated")

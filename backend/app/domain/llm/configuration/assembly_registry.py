from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import and_, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_provider import datetime_provider
from app.domain.llm.governance.feature_taxonomy import (
    assert_nominal_feature_allowed,
    normalize_feature,
    normalize_subfeature,
)
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel, PromptStatus
from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel
from app.infra.db.utils import reconstruct_orm, serialize_orm

logger = logging.getLogger(__name__)

# AC8: TTL Cache for resolved configs
# M4 Fix: Store serialized dicts instead of ORM instances
# Story 66.32 AC14: Partition cache by active_snapshot_id
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
        # Story 66.32: Robust serialization for Manifest and Cache
        data = serialize_orm(config)

        # Serialize relationships if loaded (recursive serialization)
        if config.feature_template:
            data["_feature_template"] = serialize_orm(config.feature_template)
        if config.subfeature_template:
            data["_subfeature_template"] = serialize_orm(config.subfeature_template)
        if config.persona:
            data["_persona"] = serialize_orm(config.persona)

        # Story 66.32 AC12: Persist runtime observability metadata in serialized data
        for attr in [
            "_active_snapshot_id",
            "_active_snapshot_version",
            "_manifest_entry_id",
            "_snapshot_bundle",
        ]:
            if hasattr(config, attr):
                val = getattr(config, attr)
                # Ensure UUIDs are stringified for JSON compatibility if needed
                if attr == "_active_snapshot_id" and isinstance(val, uuid.UUID):
                    val = str(val)
                data[attr] = val

        return data

    def _reconstruct_config(self, data: Dict[str, Any]) -> PromptAssemblyConfigModel:
        """
        Reconstruct a detached ORM instance from serialized dict
        with automatic type conversion.
        """
        data_copy = data.copy()

        # 1. Pop nested data and metadata to avoid constructor errors
        feat_data = data_copy.pop("_feature_template", None)
        sub_data = data_copy.pop("_subfeature_template", None)
        pers_data = data_copy.pop("_persona", None)

        # Metadata fields
        meta = {}
        for attr in [
            "_active_snapshot_id",
            "_active_snapshot_version",
            "_manifest_entry_id",
            "_snapshot_bundle",
        ]:
            if attr in data_copy:
                meta[attr] = data_copy.pop(attr)

        # 2. Reconstruct main object
        config = reconstruct_orm(PromptAssemblyConfigModel, data_copy)

        # 3. Restore metadata
        for attr, val in meta.items():
            if attr == "_active_snapshot_id" and isinstance(val, str):
                try:
                    val = uuid.UUID(val)
                except ValueError:
                    pass
            setattr(config, attr, val)

        # 4. Reconstruct relationships
        if feat_data:
            config.feature_template = reconstruct_orm(LlmPromptVersionModel, feat_data)
        if sub_data:
            config.subfeature_template = reconstruct_orm(LlmPromptVersionModel, sub_data)
        if pers_data:
            config.persona = reconstruct_orm(LlmPersonaModel, pers_data)

        return config

    async def _get_active_release_snapshot(self) -> Optional[LlmReleaseSnapshotModel]:
        """Fetch the currently active release snapshot."""
        from app.infra.db.models.llm.llm_release import (
            LlmActiveReleaseModel,
            LlmReleaseSnapshotModel,
        )

        stmt = (
            select(LlmReleaseSnapshotModel)
            .join(LlmActiveReleaseModel)
            .order_by(desc(LlmActiveReleaseModel.activated_at))
            .limit(1)
        )
        result = await self._execute(stmt)
        return result.scalar_one_or_none()

    def _get_active_release_snapshot_sync(self) -> Optional[LlmReleaseSnapshotModel]:
        """Fetch the currently active release snapshot (Sync)."""
        from sqlalchemy.orm import Session

        if not isinstance(self.session, Session):
            return None
        from app.infra.db.models.llm.llm_release import (
            LlmActiveReleaseModel,
            LlmReleaseSnapshotModel,
        )

        stmt = (
            select(LlmReleaseSnapshotModel)
            .join(LlmActiveReleaseModel)
            .order_by(desc(LlmActiveReleaseModel.activated_at))
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    async def get_active_config(
        self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str = "fr-FR"
    ) -> Optional[PromptAssemblyConfigModel]:
        """
        Resolve the best matching active assembly config.
        AC10: Use the active snapshot manifest if available.
        Waterfall: (feature, subfeature, plan) -> (feature, subfeature, None)
                   -> (feature, None, None)
        """
        # Story 66.23: Hardened taxonomy resolution
        assert_nominal_feature_allowed(feature)

        feature = normalize_feature(feature)
        subfeature = normalize_subfeature(feature, subfeature)

        # Story 66.32 AC10, AC14: Resolve active snapshot first
        snapshot = await self._get_active_release_snapshot()
        snapshot_id = str(snapshot.id) if snapshot else "none"

        cache_key = f"{snapshot_id}:{feature}:{subfeature or ''}:{plan or ''}:{locale}"
        now = time.time()

        # AC8: Cache lookup
        if cache_key in _ASSEMBLY_CACHE:
            data, expiry = _ASSEMBLY_CACHE[cache_key]
            if now < expiry:
                return self._reconstruct_config(data)
            del _ASSEMBLY_CACHE[cache_key]

        # Resolution Logic
        resolved_config = None

        if snapshot:
            # AC10: Resolve from snapshot manifest
            manifest = snapshot.manifest
            targets = manifest.get("targets", {})

            # Waterfall resolution within snapshot
            search_patterns = [
                f"{feature}:{subfeature}:{plan}:{locale}",
                f"{feature}:{subfeature}:None:{locale}",
                f"{feature}:None:None:{locale}",
            ]

            for key in search_patterns:
                bundle = targets.get(key)
                if bundle and "assembly" in bundle:
                    resolved_config = self._reconstruct_config(bundle["assembly"])
                    # Story 66.32: Attach the snapshot bundle for transitive resolution (AC4)
                    setattr(resolved_config, "_snapshot_bundle", bundle)
                    # Attach the snapshot ID for observability (AC12)
                    setattr(resolved_config, "_active_snapshot_id", snapshot.id)
                    setattr(resolved_config, "_active_snapshot_version", snapshot.version)
                    setattr(resolved_config, "_manifest_entry_id", key)
                    break
        else:
            # Legacy resolution from tables (only if no active snapshot)
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
                    resolved_config = config
                    break

        if resolved_config:
            # AC8: Update cache with serialized data
            _ASSEMBLY_CACHE[cache_key] = (self._serialize_config(resolved_config), now + CACHE_TTL)

        return resolved_config

    def get_active_config_sync(
        self, feature: str, subfeature: Optional[str], plan: Optional[str], locale: str = "fr-FR"
    ) -> Optional[PromptAssemblyConfigModel]:
        """
        Synchronous version of get_active_config.
        """
        assert_nominal_feature_allowed(feature)

        feature = normalize_feature(feature)
        subfeature = normalize_subfeature(feature, subfeature)

        # Story 66.32 AC10, AC14: Resolve active snapshot first
        snapshot = self._get_active_release_snapshot_sync()
        snapshot_id = str(snapshot.id) if snapshot else "none"

        cache_key = f"{snapshot_id}:{feature}:{subfeature or ''}:{plan or ''}:{locale}"
        now = time.time()

        if cache_key in _ASSEMBLY_CACHE:
            data, expiry = _ASSEMBLY_CACHE[cache_key]
            if now < expiry:
                return self._reconstruct_config(data)
            del _ASSEMBLY_CACHE[cache_key]

        resolved_config = None

        if snapshot:
            manifest = snapshot.manifest
            targets = manifest.get("targets", {})
            search_patterns = [
                f"{feature}:{subfeature}:{plan}:{locale}",
                f"{feature}:{subfeature}:None:{locale}",
                f"{feature}:None:None:{locale}",
            ]
            for key in search_patterns:
                bundle = targets.get(key)
                if bundle and "assembly" in bundle:
                    resolved_config = self._reconstruct_config(bundle["assembly"])
                    # Story 66.32: Attach the snapshot bundle for transitive resolution (AC4)
                    setattr(resolved_config, "_snapshot_bundle", bundle)
                    setattr(resolved_config, "_active_snapshot_id", snapshot.id)
                    setattr(resolved_config, "_active_snapshot_version", snapshot.version)
                    setattr(resolved_config, "_manifest_entry_id", key)
                    break
        else:
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
                from sqlalchemy.orm import Session

                if not isinstance(self.session, Session):
                    logger.warning("assembly_registry_get_sync_with_async_session_fallback")
                    return None

                config = self.session.execute(stmt).scalar_one_or_none()
                if config:
                    resolved_config = config
                    break

        if resolved_config:
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
                    PromptAssemblyConfigModel.id != config_id,
                )
            )
            .values(status=PromptStatus.ARCHIVED)
        )
        archived_result = await self._execute(archive_stmt)
        archived_count = archived_result.rowcount if hasattr(archived_result, "rowcount") else 0

        # 2. Publish this config
        config.status = PromptStatus.PUBLISHED

        config.published_at = datetime_provider.utcnow()

        # 3. Handle session commit/flush
        from sqlalchemy.ext.asyncio import AsyncSession

        if isinstance(self.session, AsyncSession):
            await self.session.commit()
        else:
            self.session.commit()

        # H1: Invalidate cache on publish
        self.invalidate_cache()

        return config, archived_count

    async def rollback_config(
        self,
        feature: str,
        subfeature: Optional[str],
        plan: Optional[str],
        locale: str,
        target_id: uuid.UUID,
    ) -> PromptAssemblyConfigModel:
        """
        Rollback to a specific archived configuration.
        """

        # L2 Fix: Single transaction for atomicity
        # M4 Fix: Use direct update for the archive step to avoid issues with detached instances
        async def _do_rollback():
            # Archive current active
            archive_stmt = (
                update(PromptAssemblyConfigModel)
                .where(
                    and_(
                        PromptAssemblyConfigModel.feature == feature,
                        PromptAssemblyConfigModel.subfeature == subfeature,
                        PromptAssemblyConfigModel.plan == plan,
                        PromptAssemblyConfigModel.locale == locale,
                        PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED,
                    )
                )
                .values(status=PromptStatus.ARCHIVED)
            )
            await self._execute(archive_stmt)

            # Publish target
            target_config = await self.get_config_by_id(target_id)
            if not target_config:
                raise ValueError(f"Target config {target_id} not found")

            target_config.status = PromptStatus.PUBLISHED

            target_config.published_at = datetime_provider.utcnow()
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

    @staticmethod
    def invalidate_cache() -> None:
        """H1: Clears the in-memory assembly configuration cache."""
        _ASSEMBLY_CACHE.clear()
        logger.info("assembly_registry_cache_invalidated")

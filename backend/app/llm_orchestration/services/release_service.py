from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.models.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.utils import reconstruct_orm, serialize_orm
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.config_coherence_validator import (
    ConfigCoherenceValidator,
    ValidationResult,
)
from app.llm_orchestration.services.execution_profile_registry import (
    ExecutionProfileRegistry,
)

logger = logging.getLogger(__name__)

NOMINAL_PERIMETER = ["chat", "guidance", "natal", "horoscope_daily"]


class ReleaseService:
    """
    Story 66.32: Manages LLM configuration releases (Snapshots).
    Handles build, validation, activation and rollback.
    """

    def __init__(self, session: Union[AsyncSession, Session]):
        self.session = session

    async def _execute(self, stmt):
        from sqlalchemy.ext.asyncio import AsyncSession

        if isinstance(self.session, AsyncSession):
            return await self.session.execute(stmt)
        return self.session.execute(stmt)

    async def build_snapshot(
        self, version: str, created_by: str, comment: Optional[str] = None
    ) -> LlmReleaseSnapshotModel:
        """
        AC1, AC3: Builds a new immutable snapshot from currently published artefacts.
        """
        # 1. Collect all published assemblies for nominal perimeter
        # We also collect for other families if they are published, to be safe.
        stmt = (
            select(PromptAssemblyConfigModel)
            .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
            .options(
                selectinload(PromptAssemblyConfigModel.feature_template),
                selectinload(PromptAssemblyConfigModel.subfeature_template),
                selectinload(PromptAssemblyConfigModel.persona),
            )
        )
        res = await self._execute(stmt)
        assemblies = res.scalars().all()

        manifest = {"targets": {}}
        assembly_registry = AssemblyRegistry(self.session)

        for assembly in assemblies:
            target_key = (
                f"{assembly.feature}:{assembly.subfeature}:{assembly.plan}:{assembly.locale}"
            )

            # Resolve dependencies (Frozen Copy strategy - AC4)
            bundle = await self._build_bundle(assembly, assembly_registry)
            manifest["targets"][target_key] = bundle

        snapshot = LlmReleaseSnapshotModel(
            version=version,
            manifest=manifest,
            status=ReleaseStatus.DRAFT,
            created_by=created_by,
            comment=comment,
        )
        self.session.add(snapshot)

        if isinstance(self.session, AsyncSession):
            await self.session.commit()
            await self.session.refresh(snapshot)
        else:
            self.session.commit()
            self.session.refresh(snapshot)

        return snapshot

    async def _build_bundle(
        self, assembly: PromptAssemblyConfigModel, registry: AssemblyRegistry
    ) -> Dict[str, Any]:
        """Serializes assembly and its transitive dependencies."""
        # 1. Assembly & Persona & Templates (already handled by registry helper)
        bundle = {"assembly": registry._serialize_config(assembly)}

        # 2. Execution Profile
        profile = None
        if assembly.execution_profile_ref:
            # Explicit ref
            stmt = select(LlmExecutionProfileModel).where(
                LlmExecutionProfileModel.id == assembly.execution_profile_ref
            )
            res = await self._execute(stmt)
            profile = res.scalar_one_or_none()
        else:
            # Waterfall resolution (Sync/Async wrapper)
            if isinstance(self.session, Session):
                profile = ExecutionProfileRegistry.get_active_profile(
                    self.session,
                    feature=assembly.feature,
                    subfeature=assembly.subfeature,
                    plan=assembly.plan,
                )
            else:
                # Manual waterfall for async
                candidates = [
                    (assembly.feature, assembly.subfeature, assembly.plan),
                    (assembly.feature, assembly.subfeature, None) if assembly.subfeature else None,
                    (assembly.feature, None, None),
                ]
                for c in candidates:
                    if not c:
                        continue
                    f, sf, p = c
                    stmt = select(LlmExecutionProfileModel).where(
                        LlmExecutionProfileModel.feature == f,
                        LlmExecutionProfileModel.subfeature == sf,
                        LlmExecutionProfileModel.plan == p,
                        LlmExecutionProfileModel.status == PromptStatus.PUBLISHED,
                    )
                    res = await self._execute(stmt)
                    profile = res.scalar_one_or_none()
                    if profile:
                        break

        if profile:
            bundle["profile"] = self._serialize_profile(profile)

        # 3. Output Schema
        if assembly.output_contract_ref:
            schema = await self._resolve_output_schema(assembly.output_contract_ref)
            if schema:
                bundle["schema"] = self._serialize_schema(schema)

        return bundle

    async def _resolve_output_schema(self, ref: str) -> Optional[LlmOutputSchemaModel]:
        try:
            schema_id = uuid.UUID(ref)
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.id == schema_id)
        except (ValueError, TypeError):
            stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == ref)

        res = await self._execute(stmt)
        return res.scalar_one_or_none()

    def _serialize_profile(self, profile: LlmExecutionProfileModel) -> Dict[str, Any]:
        """Generic serialization for execution profiles."""
        return serialize_orm(profile)

    def _serialize_schema(self, schema: LlmOutputSchemaModel) -> Dict[str, Any]:
        """Generic serialization for output schemas."""
        return serialize_orm(schema)

    async def validate_snapshot(self, snapshot_id: uuid.UUID) -> ValidationResult:
        """
        AC5, AC6: Validates a snapshot using ConfigCoherenceValidator.
        """
        stmt = select(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id)
        res = await self._execute(stmt)
        snapshot = res.scalar_one_or_none()
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        validator = ConfigCoherenceValidator(self.session)
        result = ValidationResult(is_valid=True)

        manifest = snapshot.manifest
        targets = manifest.get("targets", {})

        for target_key, bundle in targets.items():
            # Reconstruction for validation
            assembly_data = bundle.get("assembly")
            if not assembly_data:
                result.add_error("missing_assembly", f"Target {target_key} missing assembly data")
                continue

            # Reconstruct model from dict (Registry helper)
            registry = AssemblyRegistry(self.session)
            assembly = registry._reconstruct_config(assembly_data)

            # Validate using the bundle for transitive dependencies (Finding 5)
            target_res = await validator.validate_assembly(assembly, bundle=bundle)
            if not target_res.is_valid:
                for err in target_res.errors:
                    result.add_error(
                        err.error_code, f"Target {target_key}: {err.message}", err.details
                    )

        if result.is_valid:
            snapshot.status = ReleaseStatus.VALIDATED
            snapshot.validated_at = datetime.now(timezone.utc)

            if isinstance(self.session, AsyncSession):
                await self.session.commit()
            else:
                self.session.commit()

        return result

    async def activate_snapshot(
        self, snapshot_id: uuid.UUID, activated_by: str
    ) -> LlmReleaseSnapshotModel:
        """
        AC7: Atomic activation of a snapshot.
        """
        stmt = select(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id)
        res = await self._execute(stmt)
        snapshot = res.scalar_one_or_none()

        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        if snapshot.status not in [ReleaseStatus.VALIDATED, ReleaseStatus.ACTIVE]:
            # Re-validate just in case
            val_res = await self.validate_snapshot(snapshot_id)
            if not val_res.is_valid:
                raise ValueError("Cannot activate invalid snapshot")

        # 1. Update Active Release pointer
        # We can either update the only row or add a new one and use the latest.
        # Let's use a single row for simplicity if possible, but the table has id.
        # We'll just delete previous ones.

        async def _do_activate():
            # 1. Clear previous active pointer(s)
            # Use a query to load them into session then delete to ensure identity map sync
            stmt_select = select(LlmActiveReleaseModel)
            res_select = await self._execute(stmt_select)
            for old_active in res_select.scalars().all():
                self.session.delete(old_active)

            # Flush to ensure deletes are processed and identity map is updated
            if isinstance(self.session, AsyncSession):
                await self.session.flush()
            else:
                self.session.flush()

            # 2. Add new active pointer
            active = LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by=activated_by,
                activated_at=datetime.now(timezone.utc),
            )
            self.session.add(active)

            # 3. Update snapshot status
            # Archive previous active ones
            await self._execute(
                update(LlmReleaseSnapshotModel)
                .where(LlmReleaseSnapshotModel.status == ReleaseStatus.ACTIVE)
                .values(status=ReleaseStatus.ARCHIVED)
            )

            snapshot.status = ReleaseStatus.ACTIVE
            snapshot.activated_at = datetime.now(timezone.utc)
            snapshot.activated_by = activated_by
            return snapshot


        if isinstance(self.session, AsyncSession):
            res_snapshot = await _do_activate()
            await self.session.commit()
        else:
            res_snapshot = await _do_activate()
            self.session.commit()

        # AC14: Invalidate caches post-commit
        self.invalidate_all_caches()

        return res_snapshot

    async def rollback(self, activated_by: str) -> LlmReleaseSnapshotModel:
        """
        AC8, AC9: Rollback to N-1 snapshot.
        """
        # 1. Find the current active snapshot
        stmt = select(LlmActiveReleaseModel).order_by(desc(LlmActiveReleaseModel.activated_at))
        res = await self._execute(stmt)
        current_active = res.scalar_one_or_none()

        if not current_active:
            raise ValueError("No active release to rollback from")

        # 2. Find the previous active (which should be ARCHIVED now)
        stmt = (
            select(LlmReleaseSnapshotModel)
            .where(LlmReleaseSnapshotModel.status == ReleaseStatus.ARCHIVED)
            .order_by(desc(LlmReleaseSnapshotModel.activated_at))
            .limit(1)
        )
        res = await self._execute(stmt)
        previous = res.scalar_one_or_none()

        if not previous:
            raise ValueError("No previous snapshot found for rollback")

        # 3. Activate it
        return await self.activate_snapshot(previous.id, activated_by)

    def invalidate_all_caches(self):
        """AC14: Global invalidation of runtime registries."""
        AssemblyRegistry.invalidate_cache()
        ExecutionProfileRegistry.invalidate_cache()
        logger.info("release_service_all_caches_invalidated")

    @staticmethod
    async def get_active_release_id(session: Union[AsyncSession, Session]) -> Optional[uuid.UUID]:
        """Helper to get the active release ID (can be cached in memory)."""
        # For efficiency, we could cache this in a global variable for a few seconds
        stmt = (
            select(LlmActiveReleaseModel.release_snapshot_id)
            .order_by(desc(LlmActiveReleaseModel.activated_at))
            .limit(1)
        )

        if isinstance(session, AsyncSession):
            res = await session.execute(stmt)
        else:
            res = session.execute(stmt)

        return res.scalar_one_or_none()

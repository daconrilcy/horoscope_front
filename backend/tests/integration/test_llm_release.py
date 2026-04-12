import uuid

import pytest
from sqlalchemy import delete, select

from app.infra.db.models.llm_release import (
    LlmActiveReleaseModel,
    ReleaseStatus,
)
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.execution_profile_registry import ExecutionProfileRegistry
from app.llm_orchestration.services.release_service import ReleaseService


@pytest.mark.asyncio
async def test_llm_release_lifecycle():
    """
    Test Story 66.32: Full lifecycle of an LLM configuration release.
    Build -> Validate -> Activate -> Resolve -> Rollback.
    """
    db = SessionLocal()
    try:
        # 0. Cleanup
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()

        AssemblyRegistry.invalidate_cache()
        ExecutionProfileRegistry.invalidate_cache()

        service = ReleaseService(db)
        version = f"test-release-{uuid.uuid4().hex[:8]}"

        # 1. Build Snapshot
        snapshot = await service.build_snapshot(version=version, created_by="test_admin")
        assert snapshot.id is not None
        assert snapshot.status == ReleaseStatus.DRAFT
        assert "targets" in snapshot.manifest

        # 2. Validate Snapshot
        val_result = await service.validate_snapshot(snapshot.id)
        assert val_result.is_valid is True
        assert snapshot.status == ReleaseStatus.VALIDATED

        # 3. Activate Snapshot
        snapshot = await service.activate_snapshot(snapshot.id, activated_by="test_admin")
        assert snapshot.status == ReleaseStatus.ACTIVE

        # Verify active pointer
        stmt = select(LlmActiveReleaseModel).where(
            LlmActiveReleaseModel.release_snapshot_id == snapshot.id
        )
        active = db.execute(stmt).scalar_one_or_none()
        assert active is not None

        # 4. Runtime Resolution
        registry = AssemblyRegistry(db)
        target_keys = list(snapshot.manifest["targets"].keys())
        if target_keys:
            target_keys.sort()
            target_key = target_keys[0]
            f, sf, p, loc = target_key.split(":")
            sf = sf if sf != "None" else None
            p = p if p != "None" else None

            config = await registry.get_active_config(feature=f, subfeature=sf, plan=p, locale=loc)
            assert config is not None
            assert str(getattr(config, "_active_snapshot_id", "")) == str(snapshot.id)
            assert getattr(config, "_manifest_entry_id", "") == target_key

        # 5. Rollback
        # Create a second snapshot to have something to rollback to
        snapshot2 = await service.build_snapshot(version=version + "-v2", created_by="test_admin")
        await service.activate_snapshot(snapshot2.id, activated_by="test_admin")
        assert snapshot2.status == ReleaseStatus.ACTIVE

        # Previous one should be archived
        db.refresh(snapshot)
        assert snapshot.status == ReleaseStatus.ARCHIVED

        # Rollback
        rolled_back = await service.rollback(activated_by="test_admin")
        assert rolled_back.id == snapshot.id
        assert rolled_back.status == ReleaseStatus.ACTIVE

    finally:
        # Final cleanup of test data
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()

import uuid
import pytest
from sqlalchemy import delete, select, update
from app.infra.db.models.llm_release import LlmActiveReleaseModel, LlmReleaseSnapshotModel, ReleaseStatus
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_observability import LlmCallLogModel
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.assembly_registry import AssemblyRegistry
from app.llm_orchestration.services.execution_profile_registry import ExecutionProfileRegistry
from app.llm_orchestration.services.release_service import ReleaseService
from app.llm_orchestration.gateway import LLMGateway, LLMExecutionRequest, ExecutionUserInput, ExecutionContext, ExecutionFlags

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

        # 4. Runtime Resolution (Registry Level)
        registry = AssemblyRegistry(db)
        target_keys = list(snapshot.manifest["targets"].keys())
        assert len(target_keys) > 0
        target_keys.sort()
        
        # Pick a target that is NOT natal_interpretation to avoid schema requirements in mock plan test
        # or just ensure we use the correct use_case for the target.
        target_key = None
        for tk in target_keys:
            if "horoscope_daily" in tk or "chat" in tk:
                target_key = tk
                break
        if not target_key:
            target_key = target_keys[0]
            
        f, sf, p, loc = target_key.split(":")
        sf = sf if sf != "None" else None
        p = p if p != "None" else None
        
        # Identify appropriate use_case
        use_case = "chat" if f == "chat" else "horoscope_daily"
        if f == "natal": use_case = "natal_long_free" # Doesn't require schema

        config = await registry.get_active_config(feature=f, subfeature=sf, plan=p, locale=loc)
        assert config is not None
        assert str(getattr(config, "_active_snapshot_id", "")) == str(snapshot.id)
        assert getattr(config, "_manifest_entry_id", "") == target_key
        assert hasattr(config, "_snapshot_bundle") # Finding 1 fix

        # 5. Frozen Contract Verification (Finding 1)
        # Modify the profile in the DB and verify that resolution still uses the snapshotted version
        if config.execution_profile_ref:
            profile_id = config.execution_profile_ref
            original_profile = db.get(LlmExecutionProfileModel, profile_id)
            original_model = original_profile.model
            
            # Change model in DB
            db.execute(update(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id).values(model="gpt-snapshot-test-override"))
            db.commit()
            
            # Resolve profile via registry using the assembly
            resolved_profile = ExecutionProfileRegistry.get_profile_by_id(db, profile_id, assembly=config)
            assert resolved_profile.model == original_model
            assert resolved_profile.model != "gpt-snapshot-test-override"
            
            # Restore DB
            db.execute(update(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id).values(model=original_model))
            db.commit()

        # 6. Observability Traceability (Finding 3)
        gateway = LLMGateway()
        # Mock request for the target
        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(use_case=use_case, feature=f, subfeature=sf, plan=p, locale=loc),
            context=ExecutionContext(),
            flags=ExecutionFlags(),
            request_id=f"test-req-{uuid.uuid4().hex[:8]}",
            trace_id=f"test-trace-{uuid.uuid4().hex[:8]}"
        )
        
        # We don't actually call the LLM, we just test _resolve_plan
        plan, qualified_ctx = await gateway._resolve_plan(request, db)
        assert str(plan.active_snapshot_id) == str(snapshot.id)
        assert plan.active_snapshot_version == snapshot.version
        assert plan.manifest_entry_id == target_key

        # 7. Rollback
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

@pytest.mark.asyncio
async def test_snapshot_validation_independence():
    """
    Test Finding 5: Snapshot validation should be independent of live tables.
    """
    db = SessionLocal()
    try:
        service = ReleaseService(db)
        version = f"test-indep-{uuid.uuid4().hex[:8]}"
        
        # 1. Build Snapshot
        snapshot = await service.build_snapshot(version=version, created_by="test_admin")
        
        # 2. Break live tables (archive all profiles)
        db.execute(update(LlmExecutionProfileModel).values(status="archived"))
        db.commit()
        ExecutionProfileRegistry.invalidate_cache()
        
        # 3. Validate Snapshot - should still pass because it uses the bundle!
        val_result = await service.validate_snapshot(snapshot.id)
        assert val_result.is_valid is True
        
        # 4. Cleanup and verify live resolution fails (as a control)
        # Note: we need to use a new registry to avoid cache
        from app.llm_orchestration.services.config_coherence_validator import ConfigCoherenceValidator
        registry = AssemblyRegistry(db)
        target_keys = list(snapshot.manifest["targets"].keys())
        target_key = target_keys[0]
        f, sf, p, loc = target_key.split(":")
        sf = sf if sf != "None" else None
        p = p if p != "None" else None
        
        # Without an active snapshot, live resolution of profile should fail validation
        assembly = db.query(PromptAssemblyConfigModel).filter(PromptAssemblyConfigModel.feature == f).first()
        validator = ConfigCoherenceValidator(db)
        res_live = await validator.validate_assembly(assembly)
        assert res_live.is_valid is False # Because profiles are archived
        
    finally:
        # Restore profiles for other tests
        db.execute(update(LlmExecutionProfileModel).values(status="published"))
        db.commit()
        db.close()

@pytest.mark.asyncio
async def test_startup_validation_uses_snapshot():
    """
    Test Finding 6: Startup validation should prioritize the active snapshot.
    """
    db = SessionLocal()
    try:
        service = ReleaseService(db)
        snapshot = await service.build_snapshot(version="startup-test", created_by="test_admin")
        await service.activate_snapshot(snapshot.id, activated_by="test_admin")
        
        from app.llm_orchestration.services.config_coherence_validator import ConfigCoherenceValidator
        validator = ConfigCoherenceValidator(db)
        
        # Break live tables
        db.execute(update(LlmExecutionProfileModel).values(status="archived"))
        db.commit()
        ExecutionProfileRegistry.invalidate_cache()
        
        # Startup validation should still pass because it validates the snapshot!
        results = await validator.scan_active_configurations()
        assert len(results) == 0 # All valid
        
    finally:
        db.execute(update(LlmExecutionProfileModel).values(status="published"))
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()

@pytest.mark.asyncio
async def test_non_fr_locale_resolution():
    """Test Finding 4: Profile resolution should respect locale in snapshots."""
    db = SessionLocal()
    try:
        # Ensure we have at least one assembly for en-US
        stmt = select(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.locale == "en-US")
        en_assembly = db.execute(stmt).scalars().first()
        
        if not en_assembly:
            # Create a mock en-US assembly for testing
            fr_assembly = db.query(PromptAssemblyConfigModel).first()
            en_assembly = PromptAssemblyConfigModel(
                feature=fr_assembly.feature,
                subfeature=fr_assembly.subfeature,
                plan=fr_assembly.plan,
                locale="en-US",
                status="published",
                created_by="test",
                execution_profile_ref=fr_assembly.execution_profile_ref,
                feature_template_ref=fr_assembly.feature_template_ref,
                execution_config={} # Fix NOT NULL constraint
            )
            db.add(en_assembly)
            db.commit()

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(version="locale-test", created_by="test_admin")
        await service.activate_snapshot(snapshot.id, activated_by="test_admin")
        
        registry = ExecutionProfileRegistry()
        profile = registry.get_active_profile(
            db, 
            feature=en_assembly.feature, 
            subfeature=en_assembly.subfeature, 
            plan=en_assembly.plan, 
            locale="en-US"
        )
        assert profile is not None
        
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()

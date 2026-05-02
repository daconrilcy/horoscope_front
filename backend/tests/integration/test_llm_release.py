"""Tests release LLM utilisant le helper DB canonique d'intégration."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.llm.configuration.assembly_registry import AssemblyRegistry
from app.domain.llm.configuration.config_coherence_validator import (
    ConfigCoherenceValidator,
)
from app.domain.llm.configuration.execution_profile_registry import (
    ExecutionProfileRegistry,
)
from app.domain.llm.runtime.contracts import (
    ExecutionContext,
    ExecutionFlags,
    ExecutionUserInput,
    LLMExecutionRequest,
)
from app.domain.llm.runtime.gateway import LLMGateway
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_prompt import PromptStatus
from app.infra.db.models.llm.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.session import get_db_session
from app.main import app
from app.ops.llm.release_service import ReleaseService
from app.services.api_contracts.admin.llm.releases import ActivationQualificationEvidence
from tests.integration.app_db import open_app_db_session


def _ensure_published_assembly_for_release_snapshots(db: Session) -> None:
    """build_snapshot() ne sérialise que les assemblies au statut publié."""
    has_published = db.execute(
        select(PromptAssemblyConfigModel.id)
        .where(PromptAssemblyConfigModel.status == PromptStatus.PUBLISHED)
        .limit(1)
    ).scalar_one_or_none()
    if has_published:
        return
    any_id = db.execute(select(PromptAssemblyConfigModel.id).limit(1)).scalar_one_or_none()
    if any_id is None:
        pytest.skip("Aucune assembly en base : impossible de tester les snapshots de release.")
    db.execute(
        update(PromptAssemblyConfigModel)
        .where(PromptAssemblyConfigModel.id == any_id)
        .values(status=PromptStatus.PUBLISHED, published_at=datetime.now(timezone.utc))
    )
    db.commit()


def _default_manifest_entry_id(snapshot) -> str:
    targets = (snapshot.manifest or {}).get("targets", {})
    if not targets:
        raise ValueError("Snapshot has no manifest targets.")
    return str(next(iter(targets.keys())))


def _qualification_evidence(snapshot, verdict: str = "go", manifest_entry_id: str | None = None):
    resolved_manifest_entry_id = manifest_entry_id or _default_manifest_entry_id(snapshot)
    return type(
        "QualificationEvidence",
        (),
        {
            "verdict": verdict,
            "active_snapshot_id": snapshot.id,
            "active_snapshot_version": snapshot.version,
            "manifest_entry_id": resolved_manifest_entry_id,
            "generated_at": datetime.now(timezone.utc),
        },
    )()


def _golden_evidence(snapshot, verdict: str = "pass", manifest_entry_id: str | None = None):
    resolved_manifest_entry_id = manifest_entry_id or _default_manifest_entry_id(snapshot)
    return type(
        "GoldenEvidence",
        (),
        {
            "verdict": verdict,
            "active_snapshot_id": snapshot.id,
            "active_snapshot_version": snapshot.version,
            "manifest_entry_id": resolved_manifest_entry_id,
            "generated_at": datetime.now(timezone.utc),
        },
    )()


def _smoke_evidence(
    snapshot,
    status: str = "pass",
    fallback: bool = False,
    manifest_entry_id: str | None = None,
):
    resolved_manifest_entry_id = manifest_entry_id or _default_manifest_entry_id(snapshot)
    return {
        "status": status,
        "active_snapshot_id": str(snapshot.id),
        "active_snapshot_version": snapshot.version,
        "manifest_entry_id": resolved_manifest_entry_id,
        "forbidden_fallback_detected": fallback,
    }


def _sqlite_async_database_url() -> str | None:
    db_url = settings.database_url
    if not db_url.startswith("sqlite:///"):
        return None
    return db_url.replace("sqlite:///", "sqlite+aiosqlite:///")


def _release_version(label: str) -> str:
    """Retourne une version de release unique pour eviter les collisions SQLite."""
    return f"{label}-{uuid.uuid4().hex[:8]}"


def test_activation_evidence_requires_timezone_aware_datetime():
    with pytest.raises(ValidationError, match="timezone"):
        ActivationQualificationEvidence(
            active_snapshot_id=uuid.uuid4(),
            active_snapshot_version="v-test",
            manifest_entry_id="chat:None:None:fr-FR",
            verdict="go",
            generated_at="2026-04-15T10:00:00",
        )


def test_activate_endpoint_rejects_naive_generated_at_with_422():
    client = TestClient(app)
    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    try:
        snapshot_id = uuid.uuid4()
        payload = {
            "qualification_report": {
                "active_snapshot_id": str(snapshot_id),
                "active_snapshot_version": "v-test",
                "manifest_entry_id": "chat:None:None:fr-FR",
                "verdict": "go",
                "generated_at": "2026-04-15T10:00:00",
            },
            "golden_report": {
                "active_snapshot_id": str(snapshot_id),
                "active_snapshot_version": "v-test",
                "manifest_entry_id": "chat:None:None:fr-FR",
                "verdict": "pass",
                "generated_at": "2026-04-15T10:00:00+02:00",
            },
            "smoke_result": {
                "status": "pass",
                "active_snapshot_id": str(snapshot_id),
                "active_snapshot_version": "v-test",
                "manifest_entry_id": "chat:None:None:fr-FR",
                "forbidden_fallback_detected": False,
            },
        }

        response = client.post(f"/v1/admin/llm/releases/{snapshot_id}/activate", json=payload)

        assert response.status_code == 422
        assert "generated_at" in response.text
        assert "timezone offset" in response.text
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_llm_release_lifecycle():
    """
    Test Story 66.32: Full lifecycle of an LLM configuration release.
    Build -> Validate -> Activate -> Resolve -> Rollback.
    """
    db = open_app_db_session()
    try:
        # 0. Cleanup
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()

        AssemblyRegistry.invalidate_cache()
        ExecutionProfileRegistry.invalidate_cache()

        _ensure_published_assembly_for_release_snapshots(db)

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
        snapshot = await service.activate_snapshot(
            snapshot.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot),
            golden_report=_golden_evidence(snapshot),
            smoke_result=_smoke_evidence(snapshot),
        )
        assert snapshot.status == ReleaseStatus.ACTIVE
        assert snapshot.manifest["release_health"]["status"] in {"activated", "monitoring"}
        monitoring_events = [
            event
            for event in snapshot.manifest["release_health"]["history"]
            if event.get("status") == "monitoring"
        ]
        assert monitoring_events
        latest_monitoring = monitoring_events[-1]
        assert latest_monitoring["signals"]["active_snapshot_id"] == str(snapshot.id)
        assert latest_monitoring["signals"][
            "qualification_manifest_entry_id"
        ] == _default_manifest_entry_id(snapshot)
        assert latest_monitoring["signals"][
            "golden_manifest_entry_id"
        ] == _default_manifest_entry_id(snapshot)

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

        # Pick a target that avoids schema-heavy and known legacy prompt pitfalls when possible.
        target_key = None
        for tk in target_keys:
            if "horoscope_daily" in tk:
                target_key = tk
                break
        if not target_key:
            for tk in target_keys:
                if "natal" in tk:
                    target_key = tk
                    break
        if not target_key:
            for tk in target_keys:
                if "guidance" in tk:
                    target_key = tk
                    break
        if not target_key:
            target_key = target_keys[0]

        f, sf, p, loc = target_key.split(":")
        sf = sf if sf != "None" else None
        p = p if p != "None" else None

        # Identify appropriate use_case
        use_case = "chat" if f == "chat" else "horoscope_daily"
        if f == "natal":
            use_case = "natal_long_free"  # Doesn't require schema.

        config = await registry.get_active_config(feature=f, subfeature=sf, plan=p, locale=loc)
        assert config is not None
        assert str(getattr(config, "_active_snapshot_id", "")) == str(snapshot.id)
        assert getattr(config, "_manifest_entry_id", "") == target_key
        assert hasattr(config, "_snapshot_bundle")  # Finding 1 fix

        # 5. Frozen Contract Verification (Finding 1)
        # Modify the profile in the DB and verify that resolution still uses the snapshotted version
        if config.execution_profile_ref:
            profile_id = config.execution_profile_ref
            original_profile = db.get(LlmExecutionProfileModel, profile_id)
            original_model = original_profile.model

            # Change model in DB
            db.execute(
                update(LlmExecutionProfileModel)
                .where(LlmExecutionProfileModel.id == profile_id)
                .values(model="gpt-snapshot-test-override")
            )
            db.commit()

            # Resolve profile via registry using the assembly
            resolved_profile = ExecutionProfileRegistry.get_profile_by_id(
                db, profile_id, assembly=config
            )
            assert resolved_profile.model == original_model
            assert resolved_profile.model != "gpt-snapshot-test-override"

            # Restore DB
            db.execute(
                update(LlmExecutionProfileModel)
                .where(LlmExecutionProfileModel.id == profile_id)
                .values(model=original_model)
            )
            db.commit()

        # 6. Observability Traceability (Finding 3)
        gateway = LLMGateway()
        request = LLMExecutionRequest(
            user_input=ExecutionUserInput(
                use_case=use_case, feature=f, subfeature=sf, plan=p, locale=loc
            ),
            context=ExecutionContext(),
            flags=ExecutionFlags(),
            request_id=f"test-req-{uuid.uuid4().hex[:8]}",
            trace_id=f"test-trace-{uuid.uuid4().hex[:8]}",
        )
        plan, qualified_ctx = await gateway._resolve_plan(request, db)
        assert str(plan.active_snapshot_id) == str(snapshot.id)
        assert plan.active_snapshot_version == snapshot.version
        assert plan.manifest_entry_id == target_key

        # 7. Rollback
        # Create a second snapshot to have something to rollback to
        snapshot2 = await service.build_snapshot(version=version + "-v2", created_by="test_admin")
        await service.activate_snapshot(
            snapshot2.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot2),
            golden_report=_golden_evidence(snapshot2),
            smoke_result=_smoke_evidence(snapshot2),
        )
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
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

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
        # Note: validation here is deliberately done without snapshot bundle context.
        target_keys = list(snapshot.manifest["targets"].keys())
        target_key = target_keys[0]
        f, sf, p, loc = target_key.split(":")
        sf = sf if sf != "None" else None
        p = p if p != "None" else None

        # Without an active snapshot, live resolution of profile should fail validation
        assembly = (
            db.query(PromptAssemblyConfigModel)
            .filter(PromptAssemblyConfigModel.feature == f)
            .first()
        )
        assert assembly is not None
        validator = ConfigCoherenceValidator(db)
        res_live = await validator.validate_assembly(assembly)
        assert res_live.is_valid is False  # Because profiles are archived.

    finally:
        # Restore profiles for other tests
        db.execute(update(LlmExecutionProfileModel).values(status="published"))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_async_activation_keeps_single_active_pointer():
    """Ensure async activation deletes stale active pointers before inserting the new one."""
    async_db_url = _sqlite_async_database_url()
    if not async_db_url:
        pytest.skip("Async SQLite integration test requires a sqlite database_url")

    engine = create_async_engine(async_db_url, future=True)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    sync_db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(sync_db)
    finally:
        sync_db.close()

    try:
        async with session_factory() as db:
            await db.execute(delete(LlmActiveReleaseModel))
            await db.commit()

            AssemblyRegistry.invalidate_cache()
            ExecutionProfileRegistry.invalidate_cache()

            service = ReleaseService(db)
            base_version = f"async-release-{uuid.uuid4().hex[:8]}"

            snapshot_1 = await service.build_snapshot(
                version=f"{base_version}-1", created_by="test_admin"
            )
            await service.validate_snapshot(snapshot_1.id)
            await service.activate_snapshot(
                snapshot_1.id,
                activated_by="test_admin",
                qualification_report=_qualification_evidence(snapshot_1),
                golden_report=_golden_evidence(snapshot_1),
                smoke_result=_smoke_evidence(snapshot_1),
            )

            snapshot_2 = await service.build_snapshot(
                version=f"{base_version}-2", created_by="test_admin"
            )
            await service.validate_snapshot(snapshot_2.id)
            await service.activate_snapshot(
                snapshot_2.id,
                activated_by="test_admin",
                qualification_report=_qualification_evidence(snapshot_2),
                golden_report=_golden_evidence(snapshot_2),
                smoke_result=_smoke_evidence(snapshot_2),
            )

            res = await db.execute(select(LlmActiveReleaseModel))
            active_rows = res.scalars().all()

            assert len(active_rows) == 1
            assert active_rows[0].release_snapshot_id == snapshot_2.id
    finally:
        async with session_factory() as cleanup_db:
            await cleanup_db.execute(delete(LlmActiveReleaseModel))
            await cleanup_db.commit()
        await engine.dispose()


@pytest.mark.asyncio
async def test_startup_validation_uses_snapshot():
    """
    Test Finding 6: Startup validation should prioritize the active snapshot.
    """
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=_release_version("startup-test"), created_by="test_admin"
        )
        await service.activate_snapshot(
            snapshot.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot),
            golden_report=_golden_evidence(snapshot),
            smoke_result=_smoke_evidence(snapshot),
        )

        validator = ConfigCoherenceValidator(db)

        # Break live tables
        db.execute(update(LlmExecutionProfileModel).values(status="archived"))
        db.commit()
        ExecutionProfileRegistry.invalidate_cache()

        # Startup validation should still pass because it validates the snapshot!
        results = await validator.scan_active_configurations()
        assert len(results) == 0  # All valid.

    finally:
        db.execute(update(LlmExecutionProfileModel).values(status="published"))
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_non_fr_locale_resolution():
    """Test Finding 4: Profile resolution should respect locale in snapshots."""
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        # Ensure we have at least one assembly for en-US
        stmt = select(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.locale == "en-US")
        en_assembly = db.execute(stmt).scalars().first()

        if not en_assembly:
            # Create a mock en-US assembly for testing
            fr_assembly = db.query(PromptAssemblyConfigModel).first()
            if fr_assembly is None:
                pytest.skip("Aucune assembly de référence pour dupliquer en en-US.")
            en_assembly = PromptAssemblyConfigModel(
                feature=fr_assembly.feature,
                subfeature=fr_assembly.subfeature,
                plan=fr_assembly.plan,
                locale="en-US",
                status="published",
                created_by="test",
                execution_profile_ref=fr_assembly.execution_profile_ref,
                feature_template_ref=fr_assembly.feature_template_ref,
                execution_config={},  # Fix NOT NULL constraint.
            )
            db.add(en_assembly)
            db.commit()

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=_release_version("locale-test"), created_by="test_admin"
        )
        await service.activate_snapshot(
            snapshot.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot),
            golden_report=_golden_evidence(snapshot),
            smoke_result=_smoke_evidence(snapshot),
        )

        registry = ExecutionProfileRegistry()
        profile = registry.get_active_profile(
            db,
            feature=en_assembly.feature,
            subfeature=en_assembly.subfeature,
            plan=en_assembly.plan,
            locale="en-US",
        )
        assert profile is not None

    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_activation_is_blocked_without_correlated_evidence():
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=_release_version("gate-block-test"), created_by="test_admin"
        )
        await service.validate_snapshot(snapshot.id)

        wrong_qualification = type(
            "WrongQualificationEvidence",
            (),
            {
                "verdict": "go",
                "active_snapshot_id": uuid.uuid4(),
                "active_snapshot_version": "wrong-version",
                "manifest_entry_id": "chat:None:None:fr-FR",
                "generated_at": datetime.now(timezone.utc),
            },
        )()

        with pytest.raises(ValueError, match="Activation blocked"):
            await service.activate_snapshot(
                snapshot.id,
                activated_by="test_admin",
                qualification_report=wrong_qualification,
                golden_report=_golden_evidence(snapshot),
                smoke_result=_smoke_evidence(snapshot),
            )

        mismatched_manifest_qualification = type(
            "MismatchedManifestQualificationEvidence",
            (),
            {
                "verdict": "go",
                "active_snapshot_id": snapshot.id,
                "active_snapshot_version": snapshot.version,
                "manifest_entry_id": "does:not:exist:fr-FR",
                "generated_at": datetime.now(timezone.utc),
            },
        )()

        with pytest.raises(ValueError, match="manifest_entry_id"):
            await service.activate_snapshot(
                snapshot.id,
                activated_by="test_admin",
                qualification_report=mismatched_manifest_qualification,
                golden_report=_golden_evidence(snapshot),
                smoke_result=_smoke_evidence(snapshot),
            )
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_release_health_recommends_rollback_on_threshold_breach():
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=_release_version("health-test"), created_by="test_admin"
        )
        db.execute(
            update(LlmReleaseSnapshotModel)
            .where(LlmReleaseSnapshotModel.id == snapshot.id)
            .values(status=ReleaseStatus.VALIDATED)
        )
        db.commit()
        db.refresh(snapshot)
        await service.activate_snapshot(
            snapshot.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot),
            golden_report=_golden_evidence(snapshot),
            smoke_result=_smoke_evidence(snapshot),
            monitoring_thresholds={
                "error_rate": 0.01,
                "p95_latency_ms": 1200.0,
                "fallback_rate": 0.01,
            },
        )

        decision = await service.evaluate_release_health(
            snapshot.id,
            signals={"error_rate": 0.03, "p95_latency_ms": 900.0, "fallback_rate": 0.0},
            triggered_by="ops_user",
            auto_rollback=False,
        )
        assert decision["status"] == "rollback_recommended"
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_rollback_marks_faulty_snapshot_as_rolled_back():
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        service = ReleaseService(db)
        snapshot_a = await service.build_snapshot(
            version=_release_version("rollback-a"), created_by="test_admin"
        )
        snapshot_b = await service.build_snapshot(
            version=_release_version("rollback-b"), created_by="test_admin"
        )
        await service.validate_snapshot(snapshot_a.id)
        await service.validate_snapshot(snapshot_b.id)

        await service.activate_snapshot(
            snapshot_a.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot_a),
            golden_report=_golden_evidence(snapshot_a),
            smoke_result=_smoke_evidence(snapshot_a),
        )
        await service.activate_snapshot(
            snapshot_b.id,
            activated_by="test_admin",
            qualification_report=_qualification_evidence(snapshot_b),
            golden_report=_golden_evidence(snapshot_b),
            smoke_result=_smoke_evidence(snapshot_b),
        )

        restored_snapshot = await service.rollback(activated_by="ops_user")
        assert restored_snapshot.id == snapshot_a.id

        db.refresh(snapshot_a)
        db.refresh(snapshot_b)
        snapshot_a_history = snapshot_a.manifest["release_health"]["history"]
        assert snapshot_a_history[-1]["reason"].startswith(
            "Rollback restored previous snapshot without synthetic"
        )
        smoke_pass_events = [
            event
            for event in snapshot_a_history
            if event["reason"] == "Post-activation smoke passed."
        ]
        assert len(smoke_pass_events) == 1
        assert snapshot_b.manifest["release_health"]["status"] == "rolled_back"
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()


@pytest.mark.asyncio
async def test_activation_with_naive_timestamp_is_rejected_without_500():
    db = open_app_db_session()
    try:
        _ensure_published_assembly_for_release_snapshots(db)

        service = ReleaseService(db)
        snapshot = await service.build_snapshot(
            version=_release_version("naive-ts"), created_by="test_admin"
        )
        await service.validate_snapshot(snapshot.id)
        manifest_entry_id = _default_manifest_entry_id(snapshot)

        naive_qualification = type(
            "NaiveQualificationEvidence",
            (),
            {
                "verdict": "go",
                "active_snapshot_id": snapshot.id,
                "active_snapshot_version": snapshot.version,
                "manifest_entry_id": manifest_entry_id,
                "generated_at": datetime.now(),  # intentionally naive
            },
        )()

        with pytest.raises(ValueError, match="stale"):
            await service.activate_snapshot(
                snapshot.id,
                activated_by="test_admin",
                qualification_report=naive_qualification,
                golden_report=_golden_evidence(snapshot, manifest_entry_id=manifest_entry_id),
                smoke_result=_smoke_evidence(snapshot, manifest_entry_id=manifest_entry_id),
            )
    finally:
        db.execute(delete(LlmActiveReleaseModel))
        db.commit()
        db.close()

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.dependencies.auth import require_admin_user
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.models.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.models.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.session import SessionLocal, get_db_session
from app.infra.db.utils import serialize_orm
from app.main import app


async def mock_admin_user():
    return MagicMock(id=123, role="admin")


def _build_manifest(manifest_entry_id: str) -> dict:
    return {
        "targets": {
            manifest_entry_id: {
                "assembly": {
                    "id": str(uuid.uuid4()),
                    "feature": "chat",
                    "subfeature": "chat_default",
                    "plan": "premium",
                    "locale": "fr-FR",
                    "status": "published",
                    "output_contract_ref": "contract-chat",
                },
                "profile": {
                    "id": str(uuid.uuid4()),
                    "provider": "openai",
                    "model": "gpt-5",
                },
            }
        },
        "release_health": {"status": "monitoring"},
    }


def test_admin_llm_catalog_returns_active_snapshot_entries_with_runtime_signals():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    snapshot_id = uuid.uuid4()
    log_id = uuid.uuid4()

    try:
        db.execute(delete(LlmActiveReleaseModel))
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-catalog-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            LlmCallLogModel(
                id=log_id,
                use_case="chat_astrologer",
                model="gpt-5",
                latency_ms=1200,
                tokens_in=500,
                tokens_out=700,
                cost_usd_estimated=0.02,
                validation_status=LlmValidationStatus.VALID,
                repair_attempted=False,
                fallback_triggered=False,
                request_id="req-test-catalog",
                trace_id="trace-test-catalog",
                input_hash="a" * 64,
                environment="test",
                manifest_entry_id=manifest_entry_id,
                execution_path_kind="nominal",
                context_compensation_status="none",
                max_output_tokens_source="execution_profile",
                timestamp=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                provider="openai",
            )
        )
        db.commit()

        response = client.get("/v1/admin/llm/catalog?search=chat_default&page=1&page_size=10")
        assert response.status_code == 200
        payload = response.json()
        assert payload["meta"]["total"] >= 1
        row = payload["data"][0]
        assert row["manifest_entry_id"] == manifest_entry_id
        assert row["source_of_truth_status"] == "active_snapshot"
        assert row["assembly_status"] == "published"
        assert row["release_health_status"] == "monitoring"
        assert row["runtime_signal_status"] == "fresh"
        assert row["provider"] == "openai"
        assert row["execution_path_kind"] == "nominal"
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmCallLogModel).where(LlmCallLogModel.id == log_id))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_admin_llm_catalog_marks_stale_runtime_signal():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    manifest_entry_id = "chat:chat_default:stale:fr-FR"
    snapshot_id = uuid.uuid4()
    log_id = uuid.uuid4()

    try:
        db.execute(delete(LlmActiveReleaseModel))
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-catalog-stale",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            LlmCallLogModel(
                id=log_id,
                use_case="chat_astrologer",
                model="gpt-5",
                latency_ms=1000,
                tokens_in=300,
                tokens_out=400,
                cost_usd_estimated=0.01,
                validation_status=LlmValidationStatus.VALID,
                repair_attempted=False,
                fallback_triggered=False,
                request_id="req-test-stale",
                trace_id="trace-test-stale",
                input_hash="b" * 64,
                environment="test",
                manifest_entry_id=manifest_entry_id,
                execution_path_kind="nominal",
                context_compensation_status="none",
                max_output_tokens_source="execution_profile",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=5),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                provider="openai",
            )
        )
        db.commit()

        response = client.get(f"/v1/admin/llm/catalog?search={manifest_entry_id}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["data"][0]["runtime_signal_status"] == "stale"
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmCallLogModel).where(LlmCallLogModel.id == log_id))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_admin_llm_catalog_resolves_signals_beyond_hot_500_rows():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    hot_manifest_entry = "chat:chat_default:hot:fr-FR"
    secondary_manifest_entry = "chat:chat_default:secondary:fr-FR"
    snapshot_id = uuid.uuid4()
    hot_log_ids: list[uuid.UUID] = []
    secondary_log_id = uuid.uuid4()

    try:
        db.execute(delete(LlmActiveReleaseModel))
        manifest = _build_manifest(hot_manifest_entry)
        manifest["targets"][secondary_manifest_entry] = {
            "assembly": {
                "id": str(uuid.uuid4()),
                "feature": "chat",
                "subfeature": "chat_default",
                "plan": "secondary",
                "locale": "fr-FR",
                "status": "published",
                "output_contract_ref": "contract-chat",
            },
            "profile": {
                "id": str(uuid.uuid4()),
                "provider": "openai",
                "model": "gpt-5",
            },
        }
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-catalog-hot-window",
            manifest=manifest,
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )

        for index in range(0, 550):
            log_id = uuid.uuid4()
            hot_log_ids.append(log_id)
            db.add(
                LlmCallLogModel(
                    id=log_id,
                    use_case="chat_astrologer",
                    model="gpt-5",
                    latency_ms=1000,
                    tokens_in=200,
                    tokens_out=300,
                    cost_usd_estimated=0.01,
                    validation_status=LlmValidationStatus.VALID,
                    repair_attempted=False,
                    fallback_triggered=False,
                    request_id=f"req-hot-{index}",
                    trace_id=f"trace-hot-{index}",
                    input_hash=f"{index:064x}"[-64:],
                    environment="test",
                    manifest_entry_id=hot_manifest_entry,
                    execution_path_kind="nominal",
                    context_compensation_status="none",
                    max_output_tokens_source="execution_profile",
                    timestamp=datetime.now(timezone.utc) - timedelta(seconds=index),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                    provider="openai",
                )
            )

        db.add(
            LlmCallLogModel(
                id=secondary_log_id,
                use_case="chat_astrologer",
                model="gpt-5",
                latency_ms=900,
                tokens_in=210,
                tokens_out=320,
                cost_usd_estimated=0.01,
                validation_status=LlmValidationStatus.VALID,
                repair_attempted=False,
                fallback_triggered=False,
                request_id="req-secondary",
                trace_id="trace-secondary",
                input_hash="c" * 64,
                environment="test",
                manifest_entry_id=secondary_manifest_entry,
                execution_path_kind="nominal",
                context_compensation_status="none",
                max_output_tokens_source="execution_profile",
                timestamp=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                provider="openai",
            )
        )
        db.commit()

        response = client.get("/v1/admin/llm/catalog?feature=chat")
        assert response.status_code == 200
        payload = response.json()
        rows_by_manifest = {row["manifest_entry_id"]: row for row in payload["data"]}
        assert rows_by_manifest[hot_manifest_entry]["runtime_signal_status"] == "fresh"
        assert rows_by_manifest[secondary_manifest_entry]["runtime_signal_status"] == "fresh"
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        if hot_log_ids:
            db.execute(delete(LlmCallLogModel).where(LlmCallLogModel.id.in_(hot_log_ids)))
        db.execute(delete(LlmCallLogModel).where(LlmCallLogModel.id == secondary_log_id))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_admin_llm_catalog_resolved_detail_exposes_sources_pipeline_and_placeholders():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    use_case_key = f"chat_astrologer_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Chat",
                description="Chat astrologique",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Base prompt {{locale}} {{last_user_msg}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="chat",
            subfeature="chat_default",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="chat",
                subfeature="chat_default",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-detail-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        snapshot.manifest["targets"][manifest_entry_id]["profile"] = {
            "id": str(profile_id),
            "name": "snapshot-profile",
            "provider": "openai",
            "model": "gpt-5",
            "reasoning_profile": "medium",
            "verbosity_profile": "concise",
            "output_mode": "free_text",
            "tool_mode": "none",
            "max_output_tokens": 777,
            "timeout_seconds": 42,
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = client.get(f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved")
        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["manifest_entry_id"] == manifest_entry_id
        assert payload["inspection_mode"] == "assembly_preview"
        pip = payload["transformation_pipeline"]["post_injectors_prompt"]
        assert "last_user_msg" in pip, pip[:500]
        ph_by_name = {p["name"]: p for p in payload["resolved_result"]["placeholders"]}
        assert ph_by_name["last_user_msg"]["status"] == "expected_missing_in_preview"
        assert payload["source_of_truth_status"] == "active_snapshot"
        assert payload["composition_sources"]["feature_template"]["content"]
        assert payload["composition_sources"]["hard_policy"]["content"]
        assert payload["transformation_pipeline"]["assembled_prompt"] is not None
        assert payload["transformation_pipeline"]["post_injectors_prompt"] is not None
        assert payload["transformation_pipeline"]["rendered_prompt"] is not None
        assert payload["resolved_result"]["provider_messages"]["system_hard_policy"]
        assert isinstance(payload["resolved_result"]["placeholders"], list)
        assert (
            payload["resolved_result"]["provider_messages"]["execution_parameters"][
                "max_output_tokens_final"
            ]
            == 777
        )
        assert (
            payload["resolved_result"]["provider_messages"]["execution_parameters"][
                "timeout_seconds"
            ]
            == 42
        )
        assert isinstance(payload["resolved_result"]["placeholders"], list)
        assert "render_error" in payload["resolved_result"]["provider_messages"]

        runtime_response = client.get(
            f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview"
        )
        assert runtime_response.status_code == 200
        runtime_payload = runtime_response.json()["data"]
        assert runtime_payload["inspection_mode"] == "runtime_preview"
        rph = {p["name"]: p for p in runtime_payload["resolved_result"]["placeholders"]}
        assert rph["last_user_msg"]["status"] == "blocking_missing"

        live_response = client.get(
            f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=live_execution"
        )
        assert live_response.status_code == 200
        assert live_response.json()["data"]["inspection_mode"] == "live_execution"
        lph = {
            p["name"]: p for p in live_response.json()["data"]["resolved_result"]["placeholders"]
        }
        assert lph["last_user_msg"]["status"] == "blocking_missing"

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            replay_response = client.get(f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved")
            assert replay_response.status_code == 200
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_resolved_detail_returns_explicit_error_on_unusable_snapshot_bundle():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    use_case_key = f"chat_astrologer_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Chat",
                description="Chat astrologique",
            )
        )
        db.flush()
        db.add(
            LlmPromptVersionModel(
                id=template_id,
                use_case_key=use_case_key,
                status=PromptStatus.PUBLISHED,
                developer_prompt="Base prompt {{locale}} {{last_user_msg}}",
                model="gpt-5",
                temperature=0.2,
                max_output_tokens=900,
                created_by="test-admin",
            )
        )
        db.add(
            PromptAssemblyConfigModel(
                id=assembly_id,
                feature="chat",
                subfeature="chat_default",
                plan="premium",
                locale="fr-FR",
                feature_template_ref=template_id,
                execution_config={
                    "model": "gpt-5",
                    "temperature": None,
                    "max_output_tokens": 900,
                    "timeout_seconds": 30,
                },
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-detail-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {"id": str(assembly_id)}
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = client.get(f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved")
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "snapshot_bundle_unusable"
        assert payload["details"]["manifest_entry_id"] == manifest_entry_id
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_resolved_runtime_preview_with_sample_payload_no_provider_call():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{last_user_msg}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmSamplePayloadModel(
                id=sample_payload_id,
                name="natal-runtime",
                feature="natal",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=True,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            response = client.get(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview&sample_payload_id={sample_payload_id}"
            )
            assert response.status_code == 200
            payload = response.json()["data"]
            placeholders = {p["name"]: p for p in payload["resolved_result"]["placeholders"]}
            assert placeholders["chart_json"]["status"] == "resolved"
            assert placeholders["chart_json"]["resolution_source"] == "sample_payload"
            assert placeholders["last_user_msg"]["status"] == "blocking_missing"
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sample_payload_id)
        )
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_rejects_sample_payload_outside_runtime_preview():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmSamplePayloadModel(
                id=sample_payload_id,
                name="natal-runtime",
                feature="natal",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=True,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        response = client.get(
            f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=assembly_preview&sample_payload_id={sample_payload_id}"
        )
        assert response.status_code == 422
        payload = response.json()["error"]
        assert payload["code"] == "sample_payload_runtime_preview_only"

        live_response = client.get(
            f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=live_execution&sample_payload_id={sample_payload_id}"
        )
        assert live_response.status_code == 422
        live_payload = live_response.json()["error"]
        assert live_payload["code"] == "sample_payload_runtime_preview_only"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sample_payload_id)
        )
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_runtime_preview_rejects_inactive_sample_payload():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmSamplePayloadModel(
                id=sample_payload_id,
                name="natal-runtime-inactive",
                feature="natal",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=False,
                is_active=False,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            response = client.get(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview&sample_payload_id={sample_payload_id}"
            )
            assert response.status_code == 422
            payload = response.json()["error"]
            assert payload["code"] == "sample_payload_inactive"
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sample_payload_id)
        )
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_runtime_preview_sample_payload_not_found():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    missing_sample_payload_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            response = client.get(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview&sample_payload_id={missing_sample_payload_id}"
            )
            assert response.status_code == 404
            payload = response.json()["error"]
            assert payload["code"] == "sample_payload_not_found"
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_runtime_preview_sample_payload_target_mismatch():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmSamplePayloadModel(
                id=sample_payload_id,
                name="chat-runtime",
                feature="chat",
                locale="fr-FR",
                payload_json={"last_user_msg": "hello"},
                description="payload chat",
                is_default=False,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            response = client.get(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview&sample_payload_id={sample_payload_id}"
            )
            assert response.status_code == 422
            payload = response.json()["error"]
            assert payload["code"] == "sample_payload_target_mismatch"
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sample_payload_id)
        )
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_runtime_preview_rejects_non_object_payload_json():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Natal",
                description="Interpretation natale",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            model="gpt-5",
            temperature=0.2,
            max_output_tokens=900,
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            execution_config={
                "model": "gpt-5",
                "temperature": None,
                "max_output_tokens": 900,
                "timeout_seconds": 30,
            },
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="live-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1234,
                timeout_seconds=99,
                feature="natal",
                subfeature="interpretation",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmSamplePayloadModel(
                id=sample_payload_id,
                name="natal-runtime-invalid-json",
                feature="natal",
                locale="fr-FR",
                payload_json="invalid-structure",
                description="payload runtime",
                is_default=False,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="test-runtime-preview-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
        }
        db.add(snapshot)
        db.add(
            LlmActiveReleaseModel(
                release_snapshot_id=snapshot_id,
                activated_by="test-admin",
                activated_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        with patch(
            "app.llm_orchestration.providers.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
        ) as mocked_runtime:
            response = client.get(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved?inspection_mode=runtime_preview&sample_payload_id={sample_payload_id}"
            )
            assert response.status_code == 422
            payload = response.json()["error"]
            assert payload["code"] == "invalid_sample_payload"
            mocked_runtime.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.execute(
            delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sample_payload_id)
        )
        db.execute(
            delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == assembly_id)
        )
        db.execute(
            delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == profile_id)
        )
        db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == template_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_release_timeline_returns_snapshot_history_and_proofs():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    try:
        db.execute(delete(LlmActiveReleaseModel))
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="timeline-test-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
            activated_at=datetime.now(timezone.utc),
        )
        snapshot.manifest["release_health"]["history"] = [
            {
                "status": "monitoring",
                "reason": "Activation gate passed and monitoring window opened.",
                "signals": {
                    "qualification_verdict": "go",
                    "golden_verdict": "pass",
                    "active_snapshot_id": str(snapshot_id),
                    "active_snapshot_version": "timeline-test-v1",
                    "qualification_manifest_entry_id": manifest_entry_id,
                    "golden_manifest_entry_id": manifest_entry_id,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "status": "activated",
                "reason": "Post-activation smoke passed.",
                "signals": {
                    "status": "pass",
                    "manifest_entry_id": manifest_entry_id,
                    "active_snapshot_id": str(snapshot_id),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]
        db.add(snapshot)
        db.commit()

        response = client.get("/v1/admin/llm/release-snapshots/timeline")
        assert response.status_code == 200
        payload = response.json()["data"]
        assert len(payload) >= 3
        snapshot_rows = [row for row in payload if row["snapshot_id"] == str(snapshot_id)]
        event_types = {row["event_type"] for row in snapshot_rows}
        assert {"created", "monitoring", "activated"}.issubset(event_types)
        activated_row = next(row for row in snapshot_rows if row["event_type"] == "activated")
        proofs = {proof["proof_type"]: proof for proof in activated_row["proof_summaries"]}
        assert proofs["qualification"]["verdict"] == "go"
        assert proofs["qualification"]["correlated"] is True
        assert proofs["golden"]["verdict"] == "pass"
        assert proofs["golden"]["correlated"] is True
        assert proofs["smoke"]["verdict"] == "pass"
        assert proofs["smoke"]["correlated"] is True
        assert proofs["readiness"]["verdict"] == "valid"
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_admin_llm_release_timeline_keeps_unmapped_backend_events_explicit():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    snapshot_id = uuid.uuid4()
    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    try:
        db.execute(delete(LlmActiveReleaseModel))
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version="timeline-unmapped-v1",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
            activated_at=datetime.now(timezone.utc),
        )
        snapshot.manifest["release_health"]["history"] = [
            {
                "status": "new_status_from_backend",
                "reason": "Unknown status from runtime.",
                "signals": {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
        db.add(snapshot)
        db.commit()

        response = client.get("/v1/admin/llm/release-snapshots/timeline")
        assert response.status_code == 200
        payload = response.json()["data"]
        matching = [row for row in payload if row["snapshot_id"] == str(snapshot_id)]
        assert any(row["event_type"] == "backend_unmapped" for row in matching)
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snapshot_id))
        db.commit()
        db.close()


def test_admin_llm_release_snapshot_diff_returns_manifest_entry_categories():
    db = SessionLocal()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    from_snapshot_id = uuid.uuid4()
    to_snapshot_id = uuid.uuid4()
    kept_manifest_entry = "chat:chat_default:premium:fr-FR"
    added_manifest_entry = "natal:None:premium:fr-FR"
    try:
        db.execute(delete(LlmActiveReleaseModel))
        from_manifest = _build_manifest(kept_manifest_entry)
        to_manifest = _build_manifest(kept_manifest_entry)
        to_manifest["targets"][kept_manifest_entry]["profile"]["model"] = "gpt-5-mini"
        to_manifest["targets"][added_manifest_entry] = {
            "assembly": {
                "id": str(uuid.uuid4()),
                "feature": "natal",
                "subfeature": "None",
                "plan": "premium",
                "locale": "fr-FR",
                "status": "published",
                "output_contract_ref": "contract-natal",
            },
            "profile": {"id": str(uuid.uuid4()), "provider": "openai", "model": "gpt-5"},
        }
        db.add(
            LlmReleaseSnapshotModel(
                id=from_snapshot_id,
                version="diff-from",
                manifest=from_manifest,
                status=ReleaseStatus.ARCHIVED,
                created_by="test-admin",
            )
        )
        db.add(
            LlmReleaseSnapshotModel(
                id=to_snapshot_id,
                version="diff-to",
                manifest=to_manifest,
                status=ReleaseStatus.ACTIVE,
                created_by="test-admin",
            )
        )
        db.commit()

        response = client.get(
            f"/v1/admin/llm/release-snapshots/diff?from_snapshot_id={from_snapshot_id}&to_snapshot_id={to_snapshot_id}"
        )
        assert response.status_code == 200
        entries = response.json()["data"]["entries"]
        by_manifest = {entry["manifest_entry_id"]: entry for entry in entries}
        assert by_manifest[kept_manifest_entry]["category"] == "changed"
        assert by_manifest[kept_manifest_entry]["execution_profile_changed"] is True
        assert by_manifest[added_manifest_entry]["category"] == "added"
    finally:
        app.dependency_overrides.clear()
        db.execute(delete(LlmActiveReleaseModel))
        db.execute(
            delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == from_snapshot_id)
        )
        db.execute(
            delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == to_snapshot_id)
        )
        db.commit()
        db.close()

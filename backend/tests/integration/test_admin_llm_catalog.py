import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    UserAuthenticationError,
    require_admin_user,
    require_authenticated_user,
)
from app.api.v1.routers import admin_llm
from app.api.v1.routers.admin_llm import ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER
from app.domain.llm.runtime.contracts import (
    GatewayError,
    GatewayMeta,
    GatewayResult,
    OutputValidationError,
    PromptRenderError,
    UnknownUseCaseError,
    UsageInfo,
)
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.models.llm.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.models.llm.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.session import get_db_session
from app.infra.db.utils import serialize_orm
from app.main import app
from tests.integration.app_db import open_app_db_session


def _seed_admin_execute_sample_catalog(db: Session) -> dict[str, Any]:
    """Active snapshot + assembly + sample payload pour POST execute-sample (réutilisable)."""
    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    sample_payload_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    manifest_entry_id = "natal:interpretation:premium:fr-FR"
    use_case_key = f"natal_interpretation_{uuid.uuid4().hex[:8]}"

    db.execute(delete(LlmActiveReleaseModel))
    db.execute(
        delete(LlmSamplePayloadModel).where(
            LlmSamplePayloadModel.feature == "natal",
            LlmSamplePayloadModel.locale == "fr-FR",
        )
    )
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
            subfeature="interpretation",
            plan="premium",
            locale="fr-FR",
            payload_json={
                "chart_json": {"sun": "aries"},
                "last_user_msg": "hello from sample",
            },
            description="payload runtime",
            is_default=True,
            is_active=True,
        )
    )
    snapshot = LlmReleaseSnapshotModel(
        id=snapshot_id,
        version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
    return {
        "snapshot_id": snapshot_id,
        "template_id": template_id,
        "assembly_id": assembly_id,
        "sample_payload_id": sample_payload_id,
        "profile_id": profile_id,
        "manifest_entry_id": manifest_entry_id,
        "use_case_key": use_case_key,
    }


def _teardown_admin_execute_sample_catalog(db: Session, ctx: dict[str, Any]) -> None:
    db.execute(delete(LlmActiveReleaseModel))
    snap_id = ctx["snapshot_id"]
    db.execute(delete(LlmReleaseSnapshotModel).where(LlmReleaseSnapshotModel.id == snap_id))
    sp_id = ctx["sample_payload_id"]
    db.execute(delete(LlmSamplePayloadModel).where(LlmSamplePayloadModel.id == sp_id))
    asm_id = ctx["assembly_id"]
    db.execute(delete(PromptAssemblyConfigModel).where(PromptAssemblyConfigModel.id == asm_id))
    prof_id = ctx["profile_id"]
    db.execute(delete(LlmExecutionProfileModel).where(LlmExecutionProfileModel.id == prof_id))
    tpl_id = ctx["template_id"]
    db.execute(delete(LlmPromptVersionModel).where(LlmPromptVersionModel.id == tpl_id))
    uc_key = ctx["use_case_key"]
    db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == uc_key))
    db.commit()


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
    db = open_app_db_session()
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
            version=f"test-catalog-v1-{uuid.uuid4().hex[:8]}",
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
                executed_provider="openai",
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
    db = open_app_db_session()
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
            version=f"test-catalog-stale-{uuid.uuid4().hex[:8]}",
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
                executed_provider="openai",
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
    db = open_app_db_session()
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
            version=f"test-catalog-hot-window-{uuid.uuid4().hex[:8]}",
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
                    executed_provider="openai",
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
                executed_provider="openai",
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
    db = open_app_db_session()
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
        db.execute(
            delete(LlmSamplePayloadModel).where(
                LlmSamplePayloadModel.feature == "natal",
                LlmSamplePayloadModel.locale == "fr-FR",
            )
        )
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
            version=f"test-detail-v1-{uuid.uuid4().hex[:8]}",
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
        assert payload["activation"]["provider_target"] == "openai / gpt-5"
        assert payload["activation"]["policy_family"] == "astrology"
        selected_components = {item["key"]: item for item in payload["selected_components"]}
        assert selected_components["domain_instructions"]["component_type"] == "domain_instructions"
        assert selected_components["output_contract"]["impact_status"] == "reference_only"
        assert selected_components["hard_policy"]["merge_mode"] == "system_message"
        runtime_artifacts = {item["key"]: item for item in payload["runtime_artifacts"]}
        assert (
            runtime_artifacts["developer_prompt_assembled"]["artifact_type"]
            == "developer_prompt_assembled"
        )
        assert (
            runtime_artifacts["developer_prompt_after_injectors"]["injection_point"] == "developer"
        )
        assert runtime_artifacts["system_prompt"]["injection_point"] == "system"
        assert "messages" in runtime_artifacts["final_provider_payload"]["content"]
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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


def test_admin_llm_catalog_resolved_detail_uses_effective_runtime_use_case_for_natal_free():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    manifest_entry_id = "natal:interpretation:free:fr-FR"
    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    use_case_key = f"natal_interpretation_short_{uuid.uuid4().hex[:8]}"
    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Interprétation Natale (Courte)",
                description="Prompt natal canonique free",
            )
        )
        db.flush()
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Prompt natal {{chart_json}} {{locale}}",
            created_by="test-admin",
        )
        db.add(template_model)
        assembly_model = PromptAssemblyConfigModel(
            id=assembly_id,
            feature="natal",
            subfeature="interpretation",
            plan="free",
            locale="fr-FR",
            feature_template_ref=template_id,
            execution_profile_ref=profile_id,
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="natal-free-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="off",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1000,
                timeout_seconds=60,
                feature="natal",
                subfeature="interpretation",
                plan="free",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-natal-free-v1-{uuid.uuid4().hex[:8]}",
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

        response = client.get(f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved")
        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["use_case_key"] == "natal_long_free"
        assert payload["runtime_use_case_key"] == "natal_long_free"
        selected_components = {item["key"]: item for item in payload["selected_components"]}
        assert "plan_overlay" not in selected_components
        assert selected_components["use_case_overlay"]["component_type"] == "use_case_overlay"
        assert selected_components["use_case_overlay"]["editable_use_case_key"] == "natal_long_free"
        assert selected_components["use_case_overlay"]["content"]
    finally:
        client.close()
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


def test_admin_llm_catalog_resolved_detail_exposes_persona_overlay_and_runtime_delta():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    manifest_entry_id = "chat:chat_default:premium:fr-FR"
    snapshot_id = uuid.uuid4()
    template_id = uuid.uuid4()
    assembly_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    persona_id = uuid.uuid4()
    use_case_key = f"chat_premium_{uuid.uuid4().hex[:8]}"

    try:
        db.execute(delete(LlmActiveReleaseModel))
        db.add(
            LlmUseCaseConfigModel(
                key=use_case_key,
                display_name="Chat Premium",
                description="Prompt premium avec persona",
            )
        )
        db.flush()
        persona = LlmPersonaModel(
            id=persona_id,
            code=f"premium-{uuid.uuid4().hex[:6]}",
            name="Luna Premium",
            description="Persona premium",
            style_markers=["empathique"],
            boundaries=["pas de diagnostic"],
            allowed_topics=["astrologie"],
            disallowed_topics=["santé"],
            formatting={"sections": True, "bullets": False, "emojis": False},
        )
        db.add(persona)
        template_model = LlmPromptVersionModel(
            id=template_id,
            use_case_key=use_case_key,
            status=PromptStatus.PUBLISHED,
            developer_prompt="Base prompt {{locale}} {{last_user_msg}}",
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
            persona_ref=persona_id,
            execution_profile_ref=profile_id,
            status=PromptStatus.PUBLISHED,
            created_by="test-admin",
        )
        assembly_model.feature_template = template_model
        assembly_model.persona = persona
        db.add(assembly_model)
        db.add(
            LlmExecutionProfileModel(
                id=profile_id,
                name="chat-premium-profile",
                provider="openai",
                model="gpt-5",
                reasoning_profile="medium",
                verbosity_profile="balanced",
                output_mode="free_text",
                tool_mode="none",
                max_output_tokens=1200,
                timeout_seconds=60,
                feature="chat",
                subfeature="chat_default",
                plan="premium",
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-chat-premium-v1-{uuid.uuid4().hex[:8]}",
            manifest=_build_manifest(manifest_entry_id),
            status=ReleaseStatus.ACTIVE,
            created_by="test-admin",
        )
        snapshot.manifest["targets"][manifest_entry_id]["assembly"] = {
            **serialize_orm(assembly_model),
            "_feature_template": serialize_orm(template_model),
            "_persona": serialize_orm(persona),
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

        real_resolve_assembly = admin_llm.resolve_assembly

        def resolve_without_embedded_persona(*args: Any, **kwargs: Any):
            resolved = real_resolve_assembly(*args, **kwargs)
            return resolved.model_copy(update={"persona_block": None})

        with patch(
            "app.api.v1.routers.admin_llm.resolve_assembly",
            side_effect=resolve_without_embedded_persona,
        ):
            response = client.get(f"/v1/admin/llm/catalog/{manifest_entry_id}/resolved")
        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["activation"]["persona_policy"] == "enabled"
        selected_components = {item["key"]: item for item in payload["selected_components"]}
        assert selected_components["persona_overlay"]["component_type"] == "persona_overlay"
        assert selected_components["persona_overlay"]["merge_mode"] == "separate_developer_message"
        assert selected_components["persona_overlay"]["source_label"] == "Luna Premium"
        runtime_artifacts = {item["key"]: item for item in payload["runtime_artifacts"]}
        assert "developer_prompt_after_persona" in runtime_artifacts
        assert (
            "second message developer"
            in (runtime_artifacts["developer_prompt_after_persona"]["delta_note"] or "").lower()
        )
    finally:
        client.close()
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
        db.execute(delete(LlmPersonaModel).where(LlmPersonaModel.id == persona_id))
        db.execute(delete(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == use_case_key))
        db.commit()
        db.close()


def test_admin_llm_catalog_resolved_detail_returns_explicit_error_on_unusable_snapshot_bundle():
    db = open_app_db_session()
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
                status=PromptStatus.PUBLISHED,
                created_by="test-admin",
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-detail-v1-{uuid.uuid4().hex[:8]}",
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
        client.close()
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
    db = open_app_db_session()
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
                subfeature="interpretation",
                plan="premium",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=True,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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
    db = open_app_db_session()
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
                subfeature="interpretation",
                plan="premium",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=True,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
    db = open_app_db_session()
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
                subfeature="interpretation",
                plan="premium",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=False,
                is_active=False,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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
    db = open_app_db_session()
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
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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
    db = open_app_db_session()
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
                name="natal-runtime-wrong-scope",
                feature="natal",
                subfeature="interpretation",
                plan="free",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload natal mauvais plan",
                is_default=False,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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
    db = open_app_db_session()
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
                subfeature="interpretation",
                plan="premium",
                locale="fr-FR",
                payload_json="invalid-structure",
                description="payload runtime",
                is_default=False,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.domain.llm.runtime.provider_runtime_manager.ProviderRuntimeManager.execute_with_resilience"
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
    db = open_app_db_session()
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
    db = open_app_db_session()
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
    db = open_app_db_session()
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


def test_admin_llm_catalog_execute_sample_rejects_incomplete_runtime_preview():
    db = open_app_db_session()
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
        db.execute(
            delete(LlmSamplePayloadModel).where(
                LlmSamplePayloadModel.feature == "natal",
                LlmSamplePayloadModel.locale == "fr-FR",
            )
        )
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
                subfeature="interpretation",
                plan="premium",
                locale="fr-FR",
                payload_json={"chart_json": {"sun": "aries"}},
                description="payload runtime",
                is_default=True,
                is_active=True,
            )
        )
        snapshot = LlmReleaseSnapshotModel(
            id=snapshot_id,
            version=f"test-runtime-preview-v1-{uuid.uuid4().hex[:8]}",
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
            "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit"
        ) as mocked_audit:
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 422
        assert response.headers.get(ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER) == "1"
        err = response.json()["error"]
        assert err["code"] == "runtime_preview_incomplete_for_execution"
        assert err["details"]["failure_kind"] == "runtime_preview_incomplete"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "failed"
        assert mocked_audit.call_args.kwargs["manifest_entry_id"] == manifest_entry_id
        assert (
            mocked_audit.call_args.kwargs["details"]["failure_kind"] == "runtime_preview_incomplete"
        )
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


def test_admin_llm_catalog_execute_sample_success_mocked_gateway():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    use_case_key = str(ctx["use_case_key"])

    try:
        gw_result = GatewayResult(
            use_case=use_case_key,
            request_id="gw-req",
            trace_id="gw-tr",
            raw_output="mocked-llm-output",
            structured_output={"provider": "openai", "chart_json": "secret-chart"},
            usage=UsageInfo(input_tokens=3, output_tokens=5, total_tokens=8),
            meta=GatewayMeta(
                latency_ms=12,
                model="gpt-5",
                provider="openai",
                validation_status="valid",
            ),
        )
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                return_value=gw_result,
            ) as mocked_execute,
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit"
            ) as mocked_audit,
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 200
        assert response.headers.get(ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER) == "1"
        body = response.json()["data"]
        assert body["raw_output"] == "mocked-llm-output"
        assert body["structured_output_parseable"] is True
        assert body["structured_output"] is not None
        assert body["structured_output"]["provider"] == "openai"
        assert body["structured_output"]["chart_json"] == "[REDACTED]"
        assert isinstance(body["prompt_sent"], str) and len(body["prompt_sent"]) > 0
        assert isinstance(body["resolved_runtime_parameters"], dict)
        assert body["execution_path"] == "nominal"
        assert body["admin_manual_execution"] is True
        assert body["manifest_entry_id"] == manifest_entry_id
        assert body["sample_payload_id"] == str(sample_payload_id)
        assert body["use_case_key"] == use_case_key
        gateway_request = mocked_execute.await_args.args[0]
        assert gateway_request.user_input.message == "hello from sample"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "success"
        assert mocked_audit.call_args.kwargs["manifest_entry_id"] == manifest_entry_id
        assert mocked_audit.call_args.kwargs["details"]["gateway_request_id"] == "gw-req"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_success_without_structured_output_mocked():
    """Succès HTTP 200 sans sortie structurée (free text / schéma absent) — Dev Notes testing."""
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db

    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    use_case_key = str(ctx["use_case_key"])

    try:
        gw_result = GatewayResult(
            use_case=use_case_key,
            request_id="gw-req",
            trace_id="gw-tr",
            raw_output="plain text response only",
            usage=UsageInfo(input_tokens=1, output_tokens=2, total_tokens=3),
            meta=GatewayMeta(
                latency_ms=7,
                model="gpt-5",
                provider="openai",
                validation_status="valid",
            ),
        )
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                return_value=gw_result,
            ),
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit",
            ),
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 200
        body = response.json()["data"]
        assert body["raw_output"] == "plain text response only"
        assert body["structured_output"] is None
        assert body["structured_output_parseable"] is False
        assert body["validation_status"] == "valid"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_unknown_use_case_error_mocked():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    try:
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                side_effect=UnknownUseCaseError("use case not registered"),
            ),
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit",
            ) as mocked_audit,
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 422
        err = response.json()["error"]
        assert err["details"]["failure_kind"] == "unknown_use_case"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "failed"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_output_validation_error_mocked():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    try:
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                side_effect=OutputValidationError(
                    "schema mismatch", details={"errors": ["missing title"]}
                ),
            ),
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit",
            ) as mocked_audit,
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 422
        err = response.json()["error"]
        assert err["details"]["failure_kind"] == "output_validation"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "failed"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_prompt_render_error_mocked():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    try:
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                side_effect=PromptRenderError("missing placeholder"),
            ),
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit",
            ) as mocked_audit,
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 422
        err = response.json()["error"]
        assert err["details"]["failure_kind"] == "prompt_render"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "failed"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_provider_gateway_error_mocked():
    db = open_app_db_session()
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    app.dependency_overrides[get_db_session] = lambda: db
    ctx = _seed_admin_execute_sample_catalog(db)
    manifest_entry_id = str(ctx["manifest_entry_id"])
    sample_payload_id = ctx["sample_payload_id"]
    try:
        with (
            patch(
                "app.api.v1.routers.admin_llm.LLMGateway.execute_request",
                new_callable=AsyncMock,
                side_effect=GatewayError("upstream unavailable", error_code="provider_upstream"),
            ),
            patch(
                "app.api.v1.routers.admin_llm._record_admin_manual_execution_audit",
            ) as mocked_audit,
        ):
            response = client.post(
                f"/v1/admin/llm/catalog/{manifest_entry_id}/execute-sample",
                json={"sample_payload_id": str(sample_payload_id)},
            )
        assert response.status_code == 502
        err = response.json()["error"]
        assert err["details"]["failure_kind"] == "provider_error"
        assert err["details"]["gateway_error_class"] == "GatewayError"
        assert mocked_audit.call_count == 1
        assert mocked_audit.call_args.kwargs["status"] == "failed"
    finally:
        app.dependency_overrides.clear()
        db.rollback()
        _teardown_admin_execute_sample_catalog(db, ctx)
        db.close()


def test_admin_llm_catalog_execute_sample_forbidden_without_admin_role():
    """Surface execute-sample : refus hors rôle admin (garde backend, story 69.3)."""
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = lambda: (_ for _ in ()).throw(
        UserAuthenticationError(
            code="insufficient_role",
            message="admin role required",
            status_code=403,
            details={},
        )
    )
    try:
        response = client.post(
            "/v1/admin/llm/catalog/chat:chat_default:premium:fr-FR/execute-sample",
            json={"sample_payload_id": str(uuid.uuid4())},
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "insufficient_role"
        assert response.headers.get(ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER) == "1"
    finally:
        app.dependency_overrides.clear()


def test_admin_llm_catalog_execute_sample_unauthorized_without_token():
    """Refus 401 si l'identité n'est pas établie."""

    def _raise_missing() -> AuthenticatedUser:
        raise UserAuthenticationError(
            code="missing_access_token",
            message="missing bearer access token",
            status_code=401,
            details={},
        )

    client = TestClient(app)
    app.dependency_overrides[require_authenticated_user] = _raise_missing
    try:
        response = client.post(
            "/v1/admin/llm/catalog/chat:chat_default:premium:fr-FR/execute-sample",
            json={"sample_payload_id": str(uuid.uuid4())},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "missing_access_token"
        assert response.headers.get(ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER) == "1"
    finally:
        app.dependency_overrides.clear()


def test_admin_llm_catalog_execute_sample_invalid_body_request_validation_includes_manual_header():
    """422 invalid_request_payload : en-tête manuel présent avant handler (AC4)."""
    client = TestClient(app)
    app.dependency_overrides[require_admin_user] = mock_admin_user
    try:
        response = client.post(
            "/v1/admin/llm/catalog/chat:chat_default:premium:fr-FR/execute-sample",
            json={},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request_payload"
        assert response.headers.get(ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER) == "1"
    finally:
        app.dependency_overrides.clear()

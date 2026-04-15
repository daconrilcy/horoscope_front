import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.dependencies.auth import require_admin_user
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.llm_release import (
    LlmActiveReleaseModel,
    LlmReleaseSnapshotModel,
    ReleaseStatus,
)
from app.infra.db.session import SessionLocal, get_db_session
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

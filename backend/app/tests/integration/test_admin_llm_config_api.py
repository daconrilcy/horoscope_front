from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models import UserModel
from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import (
    LlmPromptVersionModel,
    LlmUseCaseConfigModel,
    PromptStatus,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(LlmUseCaseConfigModel))
        db.execute(delete(LlmOutputSchemaModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_admin_and_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="admin@test.com", password="admin-pass-123", role="admin"
        )  # noqa: E501
        db.commit()
        return auth.tokens.access_token


def test_admin_output_schema_list():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        s = LlmOutputSchemaModel(name="test_schema", json_schema={"type": "object"})
        db.add(s)
        db.commit()
        schema_id = s.id

    # List
    resp = client.get("/v1/admin/llm/output-schemas", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1

    # Detail
    resp = client.get(f"/v1/admin/llm/output-schemas/{schema_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "test_schema"


def test_admin_use_case_update_config_is_frozen():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.patch(
        "/v1/admin/llm/use-cases/guidance_daily",
        headers=headers,
        json={"persona_strategy": "required"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "forbidden_feature"


def test_admin_use_case_list_exposes_legacy_alias_audit():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.get("/v1/admin/llm/use-cases", headers=headers)
    assert resp.status_code == 200

    data = {item["key"]: item for item in resp.json()["data"]}

    assert "chat" not in data
    assert data["natal_psy_profile"]["use_case_audit"] == {
        "maintenance_surface": "legacy_maintenance",
        "status": "legacy_registry_only",
        "canonical_feature": None,
        "canonical_subfeature": None,
        "canonical_plan": None,
    }


def test_admin_assembly_publish_returns_structured_coherence_error():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        uc = LlmUseCaseConfigModel(key="chat", display_name="Chat", description="Test")
        db.add(uc)
        db.commit()
        prompt = LlmPromptVersionModel(
            use_case_key="chat",
            status=PromptStatus.PUBLISHED,
            developer_prompt="{{last_user_msg}}",
            created_by="test",
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)

        assembly = PromptAssemblyConfigModel(
            feature="chat",
            subfeature="astrologer",
            plan="free",
            locale="fr-FR",
            feature_template_ref=prompt.id,
            status=PromptStatus.DRAFT,
            created_by="test",
        )
        db.add(assembly)
        db.commit()
        assembly_id = assembly.id

    resp = client.post(f"/v1/admin/llm/assembly/configs/{assembly_id}/publish", headers=headers)
    assert resp.status_code == 400
    payload = resp.json()
    assert payload["error"]["code"] == "coherence_validation_failed"
    assert payload["error"]["details"]["errors"][0]["error_code"] == "missing_execution_profile"


def test_admin_prompt_create_draft_rejects_frozen_prompt_local_fallback():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post(
        "/v1/admin/llm/use-cases/guidance_daily/prompts",
        headers=headers,
        json={
            "developer_prompt": "Bonjour {{natal_chart_summary}} {{locale}} {{use_case}}",
            "model": "gpt-4o-mini",
            "fallback_use_case_key": "legacy_fallback",
        },
    )

    assert resp.status_code == 422


def test_admin_call_logs_filter_uses_canonical_feature_axis():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="legacy_chat_alias",
                    feature="chat",
                    subfeature="astrologer",
                    plan="premium",
                    model="gpt-4o-mini",
                    latency_ms=120,
                    tokens_in=10,
                    tokens_out=20,
                    cost_usd_estimated=0.001,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req-admin-llm-chat",
                    trace_id="trace-admin-llm-chat",
                    input_hash="hash-admin-llm-chat",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="legacy_guidance_alias",
                    feature="guidance",
                    subfeature="daily",
                    plan="free",
                    model="gpt-4o-mini",
                    latency_ms=220,
                    tokens_in=11,
                    tokens_out=21,
                    cost_usd_estimated=0.002,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req-admin-llm-guidance",
                    trace_id="trace-admin-llm-guidance",
                    input_hash="hash-admin-llm-guidance",
                    environment="test",
                ),
            ]
        )
        db.commit()

    resp = client.get("/v1/admin/llm/call-logs?use_case=chat", headers=headers)

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["request_id"] == "req-admin-llm-chat"


def test_admin_dashboard_groups_by_canonical_feature_with_bounded_legacy_bucket():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="legacy_chat_alias",
                    feature="chat",
                    subfeature="astrologer",
                    plan="premium",
                    model="gpt-4o-mini",
                    latency_ms=100,
                    tokens_in=20,
                    tokens_out=30,
                    cost_usd_estimated=0.003,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req-dashboard-chat",
                    trace_id="trace-dashboard-chat",
                    input_hash="hash-dashboard-chat",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="daily_prediction",
                    feature=None,
                    subfeature=None,
                    plan="free",
                    model="gpt-4o-mini",
                    latency_ms=300,
                    tokens_in=5,
                    tokens_out=10,
                    cost_usd_estimated=0.001,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req-dashboard-legacy",
                    trace_id="trace-dashboard-legacy",
                    input_hash="hash-dashboard-legacy",
                    environment="test",
                ),
            ]
        )
        db.commit()

    resp = client.get("/v1/admin/llm/dashboard", headers=headers)

    assert resp.status_code == 200
    data = {item["use_case"]: item for item in resp.json()["data"]}
    assert "chat" in data
    assert "legacy_removed" in data
    assert data["chat"]["request_count"] == 1
    assert data["legacy_removed"]["request_count"] == 1

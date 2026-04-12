from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models import (
    LlmOutputSchemaModel,
    LlmUseCaseConfigModel,
    UserModel,
)
from app.infra.db.models.llm_assembly import PromptAssemblyConfigModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, PromptStatus
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


def test_admin_use_case_update_config():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        uc = LlmUseCaseConfigModel(key="chat", display_name="Chat", description="Test")
        s = LlmOutputSchemaModel(name="chat_schema", json_schema={"type": "object"})
        db.add_all([uc, s])
        db.commit()
        schema_id = str(s.id)

    # Update config
    resp = client.patch(
        "/v1/admin/llm/use-cases/chat",
        headers=headers,
        json={
            "persona_strategy": "required",
            "safety_profile": "support",
            "output_schema_id": schema_id,
            "fallback_use_case_key": "safe_fallback",
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"][0]
    assert data["persona_strategy"] == "required"
    assert data["safety_profile"] == "support"
    assert data["output_schema_id"] == schema_id
    assert data["fallback_use_case_key"] == "safe_fallback"

    # Validate unknown safety profile fails
    resp = client.patch(
        "/v1/admin/llm/use-cases/chat", headers=headers, json={"safety_profile": "unknown"}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_safety_profile"


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
            model="gpt-4o",
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
            execution_config={"model": "gpt-4o", "max_output_tokens": 256},
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

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.llm_prompt import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(LlmPromptVersionModel))
        db.execute(delete(LlmUseCaseConfigModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_admin_llm_rbac():
    _cleanup_tables()
    user_token = _register_user("u@example.com", "user")
    response = client.get(
        "/v1/admin/llm/use-cases",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_admin_llm_crud_flow():
    _cleanup_tables()
    admin_token = _register_user("admin@example.com", "admin")
    headers = {"Authorization": f"Bearer {admin_token}", "X-Request-Id": "req-admin-llm-1"}

    # 1. Setup use case
    with SessionLocal() as db:
        uc = LlmUseCaseConfigModel(key="chat", display_name="Chat", description="Chat use case")
        db.add(uc)
        db.commit()

    # 2. List use cases
    resp = client.get("/v1/admin/llm/use-cases", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 1
    assert any(uc["key"] == "chat" for uc in data)

    # 3. Create draft
    draft_resp = client.post(
        "/v1/admin/llm/use-cases/chat/prompts",
        headers=headers,
        json={
            "developer_prompt": "Prompt for {{locale}} and {{use_case}}",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
        },
    )
    assert draft_resp.status_code == 200
    version_id = draft_resp.json()["data"]["id"]
    assert draft_resp.json()["data"]["status"] == "draft"

    # 4. List history
    hist_resp = client.get("/v1/admin/llm/use-cases/chat/prompts", headers=headers)
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()["data"]) == 1
    assert hist_resp.json()["data"][0]["id"] == version_id

    # 5. Publish
    pub_resp = client.patch(
        f"/v1/admin/llm/use-cases/chat/prompts/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200
    assert pub_resp.json()["data"]["status"] == "published"

    # 6. Verify active prompt in use cases list
    uc_list_resp = client.get("/v1/admin/llm/use-cases", headers=headers)
    chat_uc = next(uc for uc in uc_list_resp.json()["data"] if uc["key"] == "chat")
    assert chat_uc["active_prompt_version_id"] == version_id

    # 7. Create another draft and publish to test rollback
    draft2_resp = client.post(
        "/v1/admin/llm/use-cases/chat/prompts",
        headers=headers,
        json={
            "developer_prompt": "Prompt V2 for {{locale}} and {{use_case}}",
            "model": "gpt-4o-mini",
        },
    )
    v2_id = draft2_resp.json()["data"]["id"]
    client.patch(f"/v1/admin/llm/use-cases/chat/prompts/{v2_id}/publish", headers=headers)

    # 8. Rollback
    rb_resp = client.post("/v1/admin/llm/use-cases/chat/rollback", headers=headers)
    assert rb_resp.status_code == 200
    assert rb_resp.json()["data"]["id"] == version_id
    assert rb_resp.json()["data"]["status"] == "published"

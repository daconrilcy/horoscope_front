from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.models.llm_prompt import LlmUseCaseConfigModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(LlmPersonaModel))
        db.execute(delete(LlmUseCaseConfigModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_admin_and_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="admin@test.com", password="admin-pass-123", role="admin"
        )
        db.commit()
        return auth.tokens.access_token


def test_admin_persona_crud_lifecycle() -> None:
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create
    create_resp = client.post(
        "/v1/admin/llm/personas",
        headers=headers,
        json={
            "name": "Luna",
            "description": "Bienveillante",
            "tone": "warm",
            "verbosity": "medium",
            "style_markers": ["tutoiement"],
            "boundaries": ["pas de fatalisme"],
            "formatting": {"sections": True, "bullets": False, "emojis": False},
        },
    )
    assert create_resp.status_code == 200
    persona_id = create_resp.json()["data"]["id"]
    assert create_resp.json()["data"]["name"] == "Luna"

    # 2. List
    list_resp = client.get("/v1/admin/llm/personas", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1

    # 3. Update
    update_resp = client.patch(
        f"/v1/admin/llm/personas/{persona_id}",
        headers=headers,
        json={"tone": "mystical", "name": "Luna Mystica"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["tone"] == "mystical"
    assert update_resp.json()["data"]["name"] == "Luna Mystica"

    # 4. Associate to use case
    # Create use case first
    with SessionLocal() as db:
        uc = LlmUseCaseConfigModel(
            key="chat", display_name="Chat", description="Chat with astrologer"
        )
        db.add(uc)
        db.commit()

    assoc_resp = client.patch(
        "/v1/admin/llm/use-cases/chat/persona", headers=headers, json={"persona_id": persona_id}
    )
    assert assoc_resp.status_code == 200
    assert assoc_resp.json()["data"][0]["allowed_persona_ids"] == [persona_id]

    # 5. Disable (Delete)
    del_resp = client.delete(f"/v1/admin/llm/personas/{persona_id}", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["enabled"] is False


def test_admin_persona_rbac() -> None:
    _cleanup_tables()
    # Register regular user
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="user@test.com", password="user-pass-123", role="user"
        )
        db.commit()
        user_token = auth.tokens.access_token

    response = client.get(
        "/v1/admin/llm/personas", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models import UserModel
from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
from app.infra.db.models.llm.llm_prompt import LlmUseCaseConfigModel
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
        )
        db.commit()
        return auth.tokens.access_token


def test_get_use_case_contract():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        s = LlmOutputSchemaModel(
            name="AstroResponse_v1", json_schema={"type": "object", "title": "Astro"}
        )
        db.add(s)
        db.commit()

    resp = client.get(
        "/v1/admin/llm/use-cases/natal_interpretation_short/contract",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["key"] == "natal_interpretation_short"
    assert data["output_schema_id"] is not None
    assert data["output_schema"]["type"] == "object"
    assert "title" in data["output_schema"]["properties"]
    assert data["persona_strategy"] == "optional"
    assert "chart_json" in data["required_prompt_placeholders"]
    assert data["use_case_audit"] is None


def test_get_use_case_contract_hides_removed_legacy_use_case():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.get("/v1/admin/llm/use-cases/chat/contract", headers=headers)
    assert resp.status_code == 404

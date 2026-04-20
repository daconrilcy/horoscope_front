from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models import LlmOutputSchemaModel, LlmUseCaseConfigModel, UserModel
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
        db.flush()

        uc = LlmUseCaseConfigModel(
            key="natal",
            display_name="Natal",
            description="Test",
            output_schema_id=str(s.id),
            persona_strategy="required",
            safety_profile="astrology",
            required_prompt_placeholders=["chart_json"],
        )
        db.add(uc)
        db.commit()

    resp = client.get("/v1/admin/llm/use-cases/natal/contract", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["key"] == "natal"
    assert data["output_schema_id"] is not None
    assert data["output_schema"]["title"] == "Astro"
    assert data["persona_strategy"] == "required"
    assert "chart_json" in data["required_prompt_placeholders"]
    assert data["use_case_audit"] == {
        "maintenance_surface": "legacy_maintenance",
        "status": "legacy_registry_only",
        "canonical_feature": None,
        "canonical_subfeature": None,
        "canonical_plan": None,
    }


def test_get_use_case_contract_exposes_legacy_alias_metadata():
    _cleanup_tables()
    admin_token = _register_admin_and_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    with SessionLocal() as db:
        uc = LlmUseCaseConfigModel(
            key="chat",
            display_name="Chat",
            description="Legacy chat alias",
            fallback_use_case_key="horoscope_daily_free",
        )
        db.add(uc)
        db.commit()

    resp = client.get("/v1/admin/llm/use-cases/chat/contract", headers=headers)
    assert resp.status_code == 200

    data = resp.json()["data"]
    assert data["use_case_audit"] == {
        "maintenance_surface": "legacy_maintenance",
        "status": "legacy_alias",
        "canonical_feature": "chat",
        "canonical_subfeature": "astrologer",
        "canonical_plan": "free",
    }
    assert data["fallback_use_case_audit"] == {
        "maintenance_surface": "legacy_maintenance",
        "status": "legacy_alias",
        "canonical_feature": "horoscope_daily",
        "canonical_subfeature": "narration",
        "canonical_plan": "free",
    }

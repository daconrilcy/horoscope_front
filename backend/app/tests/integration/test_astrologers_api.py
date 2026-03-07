import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.session import SessionLocal, engine
from app.main import app

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(LlmPersonaModel))
        db.commit()


def test_list_astrologers_handles_null_description() -> None:
    _cleanup_tables()
    persona_id = uuid.uuid4()
    with SessionLocal() as db:
        db.add(
            LlmPersonaModel(
                id=persona_id,
                name="Astrologue Sans Bio",
                description=None,
                tone="direct",
                verbosity="medium",
                style_markers=[],
                boundaries=[],
                allowed_topics=[],
                disallowed_topics=[],
                formatting={},
                enabled=True,
            )
        )
        db.commit()

    response = client.get("/v1/astrologers")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert len(payload) == 1
    assert payload[0]["id"] == str(persona_id)
    assert payload[0]["bio_short"] == ""


def test_get_astrologer_handles_null_description() -> None:
    _cleanup_tables()
    persona_id = uuid.uuid4()
    with SessionLocal() as db:
        db.add(
            LlmPersonaModel(
                id=persona_id,
                name="Astrologue Sans Bio",
                description=None,
                tone="direct",
                verbosity="medium",
                style_markers=[],
                boundaries=[],
                allowed_topics=[],
                disallowed_topics=[],
                formatting={},
                enabled=True,
            )
        )
        db.commit()

    response = client.get(f"/v1/astrologers/{persona_id}")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == str(persona_id)
    assert payload["bio_short"] == ""
    assert payload["bio_full"] == ""

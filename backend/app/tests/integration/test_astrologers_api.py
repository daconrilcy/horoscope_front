import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models import AstrologerProfileModel, LlmPersonaModel
from app.infra.db.session import SessionLocal, engine
from app.main import app

client = TestClient(app)


def _reset_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(AstrologerProfileModel))
        db.execute(delete(LlmPersonaModel))
        db.commit()


def test_list_astrologers_returns_only_public_enabled_profiles() -> None:
    _reset_tables()
    visible_id = uuid.uuid4()
    hidden_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                LlmPersonaModel(id=visible_id, name="Visible", enabled=True),
                LlmPersonaModel(id=hidden_id, name="Disabled", enabled=False),
            ]
        )
        db.add_all(
            [
            AstrologerProfileModel(
                persona_id=visible_id,
                first_name="Visible",
                last_name="Guide",
                display_name="Visible Guide",
                gender="other",
                age=41,
                public_style_label="Standard",
                bio_short="Bio courte",
                bio_long="Bio longue",
                admin_category="standard",
                specialties=[],
                professional_background=["Parcours visible"],
                key_skills=["Pédagogie"],
                behavioral_style=["Calme"],
                is_public=True,
                sort_order=1,
            ),
            AstrologerProfileModel(
                persona_id=hidden_id,
                first_name="Hidden",
                last_name="Guide",
                display_name="Hidden Guide",
                gender="other",
                age=40,
                public_style_label="Standard",
                bio_short="Ne doit pas sortir",
                bio_long="Ne doit pas sortir",
                admin_category="standard",
                specialties=[],
                professional_background=[],
                key_skills=[],
                behavioral_style=[],
                is_public=True,
                sort_order=2,
            ),
            ]
        )
        db.commit()

    response = client.get("/v1/astrologers")
    assert response.status_code == 200
    payload = response.json()["data"]

    assert [item["id"] for item in payload] == [str(visible_id)]
    assert payload[0]["name"] == "Visible Guide"


def test_get_astrologer_returns_404_for_disabled_persona_even_if_profile_is_public() -> None:
    _reset_tables()
    persona_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(LlmPersonaModel(id=persona_id, name="Disabled", enabled=False))
        db.add(
            AstrologerProfileModel(
                persona_id=persona_id,
                first_name="Disabled",
                last_name="Guide",
                display_name="Disabled Guide",
                gender="other",
                age=40,
                public_style_label="Standard",
                bio_short="Bio courte",
                bio_long="Bio longue",
                admin_category="standard",
                specialties=[],
                professional_background=[],
                key_skills=[],
                behavioral_style=[],
                is_public=True,
            )
        )
        db.commit()

    response = client.get(f"/v1/astrologers/{persona_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "astrologer_not_found"


def test_get_astrologer_returns_structured_profile_fields() -> None:
    _reset_tables()
    persona_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(LlmPersonaModel(id=persona_id, name="Sélène", enabled=True))
        db.add(
            AstrologerProfileModel(
                persona_id=persona_id,
                first_name="Sélène",
                last_name="Ardent",
                display_name="Sélène Mystique",
                gender="female",
                age=44,
                public_style_label="Mystique",
                bio_short="Bio courte",
                bio_long="Bio longue",
                admin_category="mystical",
                specialties=["Cycles Lunaires"],
                professional_background=["Études en symbolisme et traditions anciennes"],
                key_skills=["Lecture symbolique du thème", "Archétypes"],
                behavioral_style=["Imagé", "Poétique mais lisible"],
                is_public=True,
            )
        )
        db.commit()

    response = client.get(f"/v1/astrologers/{persona_id}")
    assert response.status_code == 200

    payload = response.json()["data"]
    assert payload["age"] == 44
    assert payload["professional_background"] == ["Études en symbolisme et traditions anciennes"]
    assert payload["key_skills"] == ["Lecture symbolique du thème", "Archétypes"]
    assert payload["behavioral_style"] == ["Imagé", "Poétique mais lisible"]

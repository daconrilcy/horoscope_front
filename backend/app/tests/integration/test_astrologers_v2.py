import uuid

from fastapi.testclient import TestClient

from app.infra.db.base import Base
from app.infra.db.models import (
    AstrologerProfileModel,
    AstrologerPromptProfileModel,
    LlmPersonaModel,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from scripts.seed_astrologers_6_profiles import ASTROLOGERS, seed_astrologers

client = TestClient(app)


def _reset_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_list_astrologers_returns_v2_fields() -> None:
    _reset_tables()
    # Use a unique name to avoid conflicts if tables aren't cleared
    unique_name = f"Orion Analyste {uuid.uuid4()}"
    persona_id = uuid.uuid4()
    with SessionLocal() as db:
        persona = LlmPersonaModel(
            id=persona_id,
            name=unique_name,
            description="Legacy Bio",
            enabled=True,
        )
        db.add(persona)

        profile = AstrologerProfileModel(
            persona_id=persona_id,
            first_name="Orion",
            last_name="Analyste",
            display_name="Orion l'Analyste",
            gender="male",
            age=39,
            photo_url="/assets/orion.jpg",
            public_style_label="Analytique",
            bio_short="Short bio",
            bio_long="Long bio content",
            admin_category="rational",
            specialties=["Transits", "Carrière"],
            professional_background=["Ingénieur data / systèmes"],
            key_skills=["Lecture des aspects et configurations"],
            behavioral_style=["Méthodique"],
            is_public=True,
            sort_order=1,
        )
        db.add(profile)
        db.commit()

    response = client.get("/v1/astrologers")
    assert response.status_code == 200
    payload = response.json()["data"]

    # Find our specific persona in the list
    astrologers = [p for p in payload if p["id"] == str(persona_id)]
    assert len(astrologers) == 1

    astrologue = astrologers[0]
    assert astrologue["name"] == "Orion l'Analyste"
    assert astrologue["first_name"] == "Orion"
    assert astrologue["last_name"] == "Analyste"
    assert astrologue["avatar_url"] == "/assets/orion.jpg"
    assert "Transits" in astrologue["specialties"]
    assert astrologue["style"] == "Analytique"
    assert astrologue["bio_short"] == "Short bio"
    # Ensure admin_category is NOT exposed
    assert "admin_category" not in astrologue


def test_get_astrologer_returns_v2_profile() -> None:
    _reset_tables()
    unique_name = f"Selene Mystique {uuid.uuid4()}"
    persona_id = uuid.uuid4()
    with SessionLocal() as db:
        persona = LlmPersonaModel(
            id=persona_id,
            name=unique_name,
            enabled=True,
        )
        db.add(persona)

        profile = AstrologerProfileModel(
            persona_id=persona_id,
            first_name="Sélène",
            last_name="Mystique",
            display_name="Sélène Mystique",
            gender="female",
            age=44,
            photo_url="/assets/selene.jpg",
            public_style_label="Mystique",
            bio_short="Short",
            bio_long="Enriched long bio",
            admin_category="mystical",
            specialties=["Spiritualité"],
            professional_background=["Études en symbolisme et traditions anciennes"],
            key_skills=["Lecture symbolique du thème"],
            behavioral_style=["Imagé"],
            is_public=True,
        )
        db.add(profile)
        db.commit()

    response = client.get(f"/v1/astrologers/{persona_id}")
    assert response.status_code == 200
    payload = response.json()["data"]

    assert payload["id"] == str(persona_id)
    assert payload["name"] == "Sélène Mystique"
    assert payload["bio_full"] == "Enriched long bio"
    assert payload["gender"] == "female"
    assert payload["age"] == 44
    assert payload["professional_background"] == ["Études en symbolisme et traditions anciennes"]
    assert payload["key_skills"] == ["Lecture symbolique du thème"]
    assert payload["behavioral_style"] == ["Imagé"]
    assert "admin_category" not in payload


def test_seed_astrologers_creates_active_prompt_profiles() -> None:
    _reset_tables()
    with SessionLocal() as db:
        seed_astrologers(db)
        canonical_ids = {uuid.UUID(item["id"]) for item in ASTROLOGERS}
        prompt_profiles = (
            db.query(AstrologerPromptProfileModel)
            .filter(
                AstrologerPromptProfileModel.persona_id.in_(canonical_ids),
                AstrologerPromptProfileModel.is_active.is_(True),
            )
            .all()
        )

    assert len(prompt_profiles) == len(canonical_ids)
    assert all(profile.prompt_content.strip() for profile in prompt_profiles)


def test_seed_astrologers_populates_structured_profile_fields() -> None:
    _reset_tables()
    selene_id = next(
        uuid.UUID(item["id"]) for item in ASTROLOGERS if item["display_name"] == "Sélène Ardent"
    )

    with SessionLocal() as db:
        seed_astrologers(db)
        selene_profile = (
            db.query(AstrologerProfileModel)
            .filter(AstrologerProfileModel.persona_id == selene_id)
            .one()
        )

    assert selene_profile.age == 44
    assert any(
        item.startswith("Études en symbolisme") for item in selene_profile.professional_background
    )
    assert "Lecture symbolique" in selene_profile.key_skills
    assert "Imagé" in selene_profile.behavioral_style


def test_seed_astrologers_hides_stale_non_canonical_profiles_without_photo() -> None:
    _reset_tables()
    stale_persona_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            LlmPersonaModel(
                id=stale_persona_id,
                name="Ancien Profil",
                description="Profil historique",
                enabled=True,
            )
        )
        db.add(
            AstrologerProfileModel(
                persona_id=stale_persona_id,
                first_name="Ancien",
                last_name="Profil",
                display_name="Ancien Profil",
                gender="other",
                provider_type="ia",
                age=None,
                photo_url=None,
                public_style_label="Standard",
                bio_short="Legacy",
                bio_long="Legacy",
                admin_category="legacy",
                specialties=[],
                professional_background=[],
                key_skills=[],
                behavioral_style=[],
                is_public=True,
            )
        )
        db.commit()

        seed_astrologers(db)

        stale_profile = (
            db.query(AstrologerProfileModel)
            .filter(AstrologerProfileModel.persona_id == stale_persona_id)
            .one()
        )

    assert stale_profile.is_public is False

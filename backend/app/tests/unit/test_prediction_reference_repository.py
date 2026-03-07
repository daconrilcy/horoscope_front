from __future__ import annotations

from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import (
    HouseProfileModel,
    PlanetProfileModel,
    PredictionCategoryModel,
    SignRulershipModel,
)
from app.infra.db.models.reference import (
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.repositories.prediction_reference_repository import (
    PredictionReferenceRepository,
)
from app.infra.db.repositories.prediction_schemas import (
    CategoryData,
    PlanetProfileData,
    PredictionContext,
)


def test_get_categories(db_session: Session):
    repo = PredictionReferenceRepository(db_session)

    # Seed
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    categories = [
        PredictionCategoryModel(
            reference_version_id=version.id,
            code=f"cat_{i}",
            name=f"Category {i}",
            display_name=f"Cat {i}",
            sort_order=i,
            is_enabled=True,
        )
        for i in range(12)
    ]
    # Add one disabled category
    categories.append(
        PredictionCategoryModel(
            reference_version_id=version.id,
            code="disabled",
            name="Disabled",
            display_name="Disabled",
            sort_order=100,
            is_enabled=False,
        )
    )
    db_session.add_all(categories)
    db_session.commit()

    result = repo.get_categories(version.id)

    assert len(result) == 12
    assert [c.code for c in result] == [f"cat_{i}" for i in range(12)]
    assert isinstance(result[0], CategoryData)


PLANET_CODES = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
]


def test_get_planet_profiles(db_session: Session):
    repo = PredictionReferenceRepository(db_session)

    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    for i, code in enumerate(PLANET_CODES):
        planet = PlanetModel(reference_version_id=version.id, code=code, name=code.capitalize())
        db_session.add(planet)
        db_session.flush()
        profile = PlanetProfileModel(
            planet_id=planet.id,
            class_code="luminary" if code in ("sun", "moon") else "personal",
            speed_rank=i + 1,
            speed_class="fast",
            weight_intraday=1.0,
            weight_day_climate=1.0,
            keywords_json='["vitality", "ego", "purpose"]' if code == "sun" else None,
        )
        db_session.add(profile)
    db_session.commit()

    result = repo.get_planet_profiles(version.id)

    assert len(result) == 10
    assert "sun" in result
    sun_profile = result["sun"]
    assert isinstance(sun_profile, PlanetProfileData)
    assert sun_profile.code == "sun"
    assert sun_profile.keywords == ["vitality", "ego", "purpose"]
    assert isinstance(result["moon"].keywords, list)


SIGN_RULERSHIPS = [
    ("aries", "mars"),
    ("taurus", "venus"),
    ("gemini", "mercury"),
    ("cancer", "moon"),
    ("leo", "sun"),
    ("virgo", "mercury"),
    ("libra", "venus"),
    ("scorpio", "mars"),
    ("sagittarius", "jupiter"),
    ("capricorn", "saturn"),
    ("aquarius", "saturn"),
    ("pisces", "jupiter"),
]


def test_get_sign_rulerships(db_session: Session):
    repo = PredictionReferenceRepository(db_session)

    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    # Seed unique planet codes needed
    planet_codes = list(dict.fromkeys(p for _, p in SIGN_RULERSHIPS))
    planets = {
        code: PlanetModel(reference_version_id=version.id, code=code, name=code.capitalize())
        for code in planet_codes
    }
    db_session.add_all(planets.values())

    signs = {
        code: SignModel(reference_version_id=version.id, code=code, name=code.capitalize())
        for code, _ in SIGN_RULERSHIPS
    }
    db_session.add_all(signs.values())
    db_session.flush()

    rulerships = [
        SignRulershipModel(
            reference_version_id=version.id,
            sign_id=signs[sign_code].id,
            planet_id=planets[planet_code].id,
            rulership_type="domicile",
            is_primary=True,
        )
        for sign_code, planet_code in SIGN_RULERSHIPS
    ]
    db_session.add_all(rulerships)
    db_session.commit()

    result = repo.get_sign_rulerships(version.id)

    assert len(result) == 12
    assert result["aries"] == "mars"
    assert result["leo"] == "sun"


def test_load_prediction_context(db_session: Session):
    repo = PredictionReferenceRepository(db_session)

    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    # Seed one category
    db_session.add(
        PredictionCategoryModel(
            reference_version_id=version.id,
            code="love",
            name="Love",
            display_name="Love",
            sort_order=1,
            is_enabled=True,
        )
    )

    # Seed one planet with profile
    planet = PlanetModel(reference_version_id=version.id, code="sun", name="Sun")
    db_session.add(planet)
    db_session.flush()
    db_session.add(
        PlanetProfileModel(
            planet_id=planet.id,
            class_code="luminary",
            speed_rank=1,
            speed_class="fast",
            weight_intraday=1.5,
            weight_day_climate=1.2,
        )
    )

    # Seed one house with profile
    house = HouseModel(reference_version_id=version.id, number=1, name="House 1")
    db_session.add(house)
    db_session.flush()
    db_session.add(
        HouseProfileModel(
            house_id=house.id,
            house_kind="angular",
            visibility_weight=1.0,
            base_priority=1,
        )
    )

    db_session.commit()

    context = repo.load_prediction_context(version.id)

    assert isinstance(context, PredictionContext)
    assert len(context.categories) >= 1
    assert len(context.planet_profiles) >= 1
    assert len(context.house_profiles) >= 1
    assert "sun" in context.planet_profiles
    assert 1 in context.house_profiles

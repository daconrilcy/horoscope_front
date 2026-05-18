from __future__ import annotations

import pytest
from sqlalchemy import CheckConstraint, String, Text, UniqueConstraint, inspect, select
from sqlalchemy.orm import Session

from app.infra.db.base import Base
from app.infra.db.models.interpretation_reference import (
    AstralAspectInterpretationProfileModel,
    AstralHouseAxisDefinitionModel,
    AstralHouseAxisMemberModel,
    AstralPointInterpretationProfileModel,
    HouseInterpretationProfileModel,
)
from app.infra.db.models.prediction_reference import (
    AspectProfileModel,
    AstralAspectDefinitionModel,
    AstralAspectOrbRuleModel,
    AstralDefaultValenceModel,
    AstralInterpretiveValenceModel,
    AstralPlanetSignDignityModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralAstrologicalRoleModel,
    AstralCalculationTypeModel,
    AstralConstellationModel,
    AstralDignityTypeModel,
    AstralFixedStarDefinitionModel,
    AstralFixedStarKeywordModel,
    AstralFixedStarModel,
    AstralHemisphereModel,
    AstralHouseSystemModel,
    AstralObjectTypeModel,
    AstralPlanetDefinitionModel,
    AstralPointAliasModel,
    AstralPointCalculationVariantModel,
    AstralPointFamilyModel,
    AstralPointInterpretationKeywordModel,
    AstralPointModel,
    AstralReferenceEpochModel,
    AstralReferenceSourceModel,
    AstralSignModel,
    AstralSpeedModel,
    AstralSystemModel,
    AstralTypicalPolarityModel,
    AstralZodiacalReferenceSystemCategoryModel,
    AstralZodiacalReferenceSystemModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.prediction_reference_repository import (
    PredictionReferenceRepository,
)
from app.infra.db.repositories.prediction_schemas import (
    CategoryData,
    FixedStarData,
    HousePredictionProfile,
    PlanetProfileData,
    PredictionContext,
)
from app.infra.db.repositories.reference_repository import ReferenceRepository


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


def test_structural_astrology_models_are_not_versioned():
    """Les tables structurelles restent des référentiels stables non versionnés."""
    structural_models = (
        PlanetModel,
        AstralSignModel,
        HouseModel,
        AspectModel,
        AstroPointModel,
        AstralSystemModel,
        AstralHouseSystemModel,
        AstralConstellationModel,
        AstralHemisphereModel,
        AstralZodiacalReferenceSystemCategoryModel,
        AstralZodiacalReferenceSystemModel,
        AstralReferenceEpochModel,
        AstralReferenceSourceModel,
        AstralFixedStarModel,
        AstralFixedStarKeywordModel,
        AstralFixedStarDefinitionModel,
        AstralPlanetSignDignityModel,
        AstralHouseAxisDefinitionModel,
        AstralAspectFamilyModel,
        AstralPointFamilyModel,
        AstralPointModel,
        AstralPointCalculationVariantModel,
        AstralPointAliasModel,
        AstralPointInterpretationKeywordModel,
        AstralPointInterpretationProfileModel,
    )

    for model in structural_models:
        columns = {column.key for column in inspect(model).columns}
        assert "reference_version_id" not in columns


def test_reference_repository_seeds_astral_point_catalog(db_session: Session) -> None:
    """Le seed global alimente les points calculés et leurs variantes sans ambiguïté."""
    ReferenceRepository(db_session).seed_version_defaults()
    db_session.flush()

    assert db_session.query(AstralPointFamilyModel).count() == 3
    assert db_session.query(AstralPointModel).count() == 5
    assert db_session.query(AstralPointCalculationVariantModel).count() == 10
    assert db_session.query(AstralPointAliasModel).count() == 17
    assert db_session.query(AstralPointInterpretationKeywordModel).count() == 5
    assert db_session.query(AstralPointInterpretationProfileModel).count() == 5

    true_variants = db_session.scalars(
        select(AstralPointCalculationVariantModel).where(
            AstralPointCalculationVariantModel.variant_code == "true"
        )
    ).all()

    assert {variant.astral_point_code for variant in true_variants} == {
        "black_moon_lilith",
        "lunar_apogee",
        "lunar_perigee",
        "north_node",
        "south_node",
    }


def test_astral_system_model_supports_nullable_self_inheritance():
    """Les systèmes astrologiques portent une self-FK nullable d'héritage."""
    columns = {column.key for column in inspect(AstralSystemModel).columns}
    assert columns == {"id", "name", "inherits_from_system_id"}
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in AstralSystemModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {"astral_systems"}


def test_planet_model_uses_canonical_astral_table_name():
    """Le modèle des planètes pointe vers le nom SQL canonique astral."""
    assert PlanetModel.__tablename__ == "astral_planets"
    columns = {column.key for column in inspect(PlanetModel).columns}
    assert columns == {"id", "code", "name", "swe_id"}


def test_reference_and_aspect_models_use_canonical_astral_table_names():
    """Les modèles de versions et d'aspects pointent vers les noms SQL canoniques."""
    assert ReferenceVersionModel.__tablename__ == "astral_reference_versions"
    assert AspectModel.__tablename__ == "astral_aspects"
    assert AstralAspectFamilyModel.__tablename__ == "astral_aspect_families"


def test_constellation_model_uses_canonical_astral_table_name():
    """Le modèle des constellations pointe vers le nom SQL canonique astral."""
    assert AstralConstellationModel.__tablename__ == "astral_constellations"
    columns = {column.key for column in inspect(AstralConstellationModel).columns}
    assert columns == {
        "id",
        "key",
        "display_name",
        "latin_name",
        "abbreviation",
        "zodiacal",
        "hemisphere_id",
        "notes",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralConstellationModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints
    assert ("abbreviation",) in constraints
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in AstralConstellationModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {"astral_hemispheres"}


def test_hemisphere_model_uses_canonical_astral_table_name():
    """Le modèle des hémisphères pointe vers le nom SQL canonique astral."""
    assert AstralHemisphereModel.__tablename__ == "astral_hemispheres"
    columns = {column.key for column in inspect(AstralHemisphereModel).columns}
    assert columns == {"id", "key", "display_name", "description", "usage_note"}
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralHemisphereModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints


def test_zodiacal_reference_system_category_model_uses_canonical_table_name():
    """Le modèle des catégories zodiacales pointe vers le nom SQL canonique."""
    assert (
        AstralZodiacalReferenceSystemCategoryModel.__tablename__
        == "astral_zodiacal_reference_system_categories"
    )
    columns = {column.key for column in inspect(AstralZodiacalReferenceSystemCategoryModel).columns}
    assert columns == {"id", "key", "display_name", "description", "usage_note"}
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralZodiacalReferenceSystemCategoryModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints


def test_zodiacal_reference_system_model_uses_canonical_table_name():
    """Le modèle des systèmes zodiacaux pointe vers le nom SQL canonique."""
    assert AstralZodiacalReferenceSystemModel.__tablename__ == ("astral_zodiacal_reference_systems")
    columns = {column.key for column in inspect(AstralZodiacalReferenceSystemModel).columns}
    assert columns == {
        "id",
        "key",
        "display_name",
        "category_id",
        "description",
        "requires_ayanamsha",
        "usage_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralZodiacalReferenceSystemModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in AstralZodiacalReferenceSystemModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {"astral_zodiacal_reference_system_categories"}


def test_reference_epoch_model_uses_canonical_table_name():
    """Le modèle des époques pointe vers le nom SQL canonique astral."""
    assert AstralReferenceEpochModel.__tablename__ == "astral_reference_epochs"
    columns = {column.key for column in inspect(AstralReferenceEpochModel).columns}
    assert columns == {
        "id",
        "key",
        "display_name",
        "description",
        "epoch_type",
        "julian_year",
        "iso_datetime",
        "is_standard",
        "usage_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralReferenceEpochModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints


def test_reference_source_model_uses_canonical_table_name():
    """Le modèle des sources pointe vers le nom SQL canonique astral."""
    assert AstralReferenceSourceModel.__tablename__ == "astral_reference_sources"
    columns = {column.key for column in inspect(AstralReferenceSourceModel).columns}
    assert columns == {
        "id",
        "key",
        "display_name",
        "category",
        "publisher",
        "website",
        "is_canonical",
        "usage_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralReferenceSourceModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in constraints


def test_fixed_star_models_use_canonical_table_names():
    """Les modèles d'étoiles fixes pointent vers les tables SQL canoniques."""
    assert AstralFixedStarModel.__tablename__ == "astral_fixed_stars"
    assert AstralFixedStarKeywordModel.__tablename__ == "astral_fixed_star_keywords"
    assert AstralFixedStarDefinitionModel.__tablename__ == "astral_fixed_star_definitions"
    assert {column.key for column in inspect(AstralFixedStarModel).columns} == {
        "id",
        "key",
        "display_name",
    }
    assert {column.key for column in inspect(AstralFixedStarKeywordModel).columns} == {
        "id",
        "keywords_json",
    }
    assert {column.key for column in inspect(AstralFixedStarDefinitionModel).columns} == {
        "id",
        "fixed_star_id",
        "constellation_id",
        "zodiacal_reference_system_id",
        "reference_epoch_id",
        "ecliptic_longitude_deg",
        "zodiac_sign_id",
        "zodiac_degree",
        "declination_deg",
        "right_ascension_deg",
        "visual_magnitude",
        "astral_fixed_star_keywords_id",
        "is_active",
        "source_id",
        "notes",
    }
    fixed_star_constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralFixedStarModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    definition_constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralFixedStarDefinitionModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("key",) in fixed_star_constraints
    assert ("fixed_star_id",) in definition_constraints
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in AstralFixedStarDefinitionModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {
        "astral_fixed_stars",
        "astral_constellations",
        "astral_zodiacal_reference_systems",
        "astral_reference_epochs",
        "astral_signs",
        "astral_fixed_star_keywords",
        "astral_reference_sources",
    }


def test_prediction_aspect_and_planet_weight_tables_are_astral_namespaced():
    """Les tables prédictives liées aux aspects et planètes sont préfixées astral."""
    assert PlanetCategoryWeightModel.__tablename__ == "astral_planet_category_weights"
    assert AspectProfileModel.__tablename__ == "astral_aspect_profiles"
    assert (
        AstralAspectInterpretationProfileModel.__tablename__
        == "astral_aspect_interpretation_profiles"
    )
    assert AstralAspectDefinitionModel.__tablename__ == "astral_aspect_definitions"
    assert AstralAspectOrbRuleModel.__tablename__ == "astral_aspect_orb_rules"
    assert AstralDefaultValenceModel.__tablename__ == "astral_default_valence"
    assert AstralInterpretiveValenceModel.__tablename__ == "astral_interpretive_valence"
    assert inspect(PlanetCategoryWeightModel).persist_selectable.name == (
        "astral_planet_category_weights"
    )


def test_enabled_aspect_definitions_require_default_orb_deg():
    """Un aspect activé doit toujours porter son orbe standard de fallback."""
    constraints = {
        constraint.name
        for constraint in AstralAspectDefinitionModel.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_astral_aspect_definitions_enabled_default_orb" in constraints


def test_aspect_orb_rule_model_stores_only_targeted_overrides():
    """Verrouille la structure des exceptions d'orbes versionnées."""
    columns = {column.key for column in inspect(AstralAspectOrbRuleModel).columns}
    assert columns == {
        "id",
        "reference_version_id",
        "astral_system_id",
        "aspect_id",
        "calculation_context",
        "source_body_type",
        "source_planet_id",
        "source_point_code",
        "target_body_type",
        "target_planet_id",
        "target_point_code",
        "orb_deg",
        "priority",
        "is_enabled",
        "micro_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralAspectOrbRuleModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert (
        "reference_version_id",
        "astral_system_id",
        "aspect_id",
        "calculation_context",
        "source_body_type",
        "source_planet_id",
        "source_point_code",
        "target_body_type",
        "target_planet_id",
        "target_point_code",
    ) in constraints


def test_house_models_use_canonical_astral_table_names():
    """Les modèles maison pointent vers les noms SQL canoniques astraux."""
    assert HouseModel.__tablename__ == "astral_houses"
    assert AstralHouseSystemModel.__tablename__ == "astral_house_systems"
    assert HouseProfileModel.__tablename__ == "astral_prediction_daily_house_profiles"
    assert HouseCategoryWeightModel.__tablename__ == "astral_house_category_weights"
    assert HouseInterpretationProfileModel.__tablename__ == "astral_house_interpretation_profiles"


def test_house_axis_definition_is_structural_not_versioned():
    """Les definitions d'axes de maisons sont structurelles et non versionnees."""
    columns = {column.key for column in inspect(AstralHouseAxisDefinitionModel).columns}
    assert columns == {
        "id",
        "astral_system_id",
        "key",
        "title",
        "summary",
        "language_id",
        "micro_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralHouseAxisDefinitionModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("astral_system_id", "key", "language_id") in constraints


def test_house_interpretation_profile_is_dedicated_editorial_reference_model():
    """Verrouille le modèle éditorial versionné distinct du runtime et du scoring."""
    columns = {column.key for column in inspect(HouseInterpretationProfileModel).columns}
    assert columns == {
        "id",
        "reference_version_id",
        "house_id",
        "language_id",
        "astral_system_id",
        "title",
        "summary",
        "core_keywords_json",
        "shadow_keywords_json",
        "psychological_keywords_json",
        "material_keywords_json",
        "relationship_keywords_json",
        "career_keywords_json",
        "health_keywords_json",
        "spiritual_keywords_json",
        "body_parts_json",
        "archetypes_json",
        "dos_json",
        "donts_json",
        "prompt_hints_json",
        "micro_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in HouseInterpretationProfileModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("reference_version_id", "house_id", "language_id", "astral_system_id") in constraints
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in HouseInterpretationProfileModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {
        "astral_reference_versions",
        "astral_houses",
        "astral_systems",
        "languages",
    }


def test_aspect_interpretation_profile_is_dedicated_editorial_reference_model():
    """Verrouille le modèle éditorial versionné distinct des profils de scoring."""
    columns = {column.key for column in inspect(AstralAspectInterpretationProfileModel).columns}
    assert columns == {
        "id",
        "reference_version_id",
        "aspect_id",
        "astral_system_id",
        "language_id",
        "title",
        "summary",
        "core_keywords_json",
        "shadow_keywords_json",
        "psychological_keywords_json",
        "relationship_keywords_json",
        "career_keywords_json",
        "spiritual_keywords_json",
        "energetic_dynamics_json",
        "growth_patterns_json",
        "conflict_patterns_json",
        "archetypes_json",
        "dos_json",
        "donts_json",
        "prompt_hints_json",
        "micro_note",
    }
    constraints = {
        tuple(constraint.columns.keys())
        for constraint in AstralAspectInterpretationProfileModel.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert (
        "reference_version_id",
        "aspect_id",
        "astral_system_id",
        "language_id",
    ) in constraints
    foreign_key_targets = {
        foreign_key.column.table.name
        for column in AstralAspectInterpretationProfileModel.__table__.columns
        for foreign_key in column.foreign_keys
    }
    assert foreign_key_targets == {
        "astral_reference_versions",
        "astral_aspects",
        "astral_systems",
        "languages",
    }


def test_house_interpretation_profile_update_is_blocked_when_version_is_locked(
    db_session: Session,
):
    """Vérifie le verrouillage des profils éditoriaux après publication de version."""
    version = ReferenceVersionModel(version="locked-editorial", is_locked=True)
    house = HouseModel(number=10, name="Career")
    system = AstralSystemModel(name="modern")
    language = LanguageModel(code="en", name="english")
    db_session.add_all([version, house, system, language])
    db_session.flush()
    profile = HouseInterpretationProfileModel(
        reference_version_id=version.id,
        house_id=house.id,
        language_id=language.id,
        astral_system_id=system.id,
        title="Career and Public Role",
        summary="Original editorial summary.",
    )
    db_session.add(profile)
    db_session.commit()

    profile.title = "Changed title"

    with pytest.raises(ValueError, match="reference version is immutable"):
        db_session.commit()
    db_session.rollback()


def test_aspect_interpretation_profile_update_is_blocked_when_version_is_locked(
    db_session: Session,
):
    """Vérifie le verrouillage des profils éditoriaux d'aspects publiés."""
    version = ReferenceVersionModel(version="locked-aspect-editorial", is_locked=True)
    family = AstralAspectFamilyModel(name="major")
    db_session.add(family)
    db_session.flush()
    aspect = AspectModel(code="conjunction", name="Conjunction", angle=0.0, family=family.id)
    system = AstralSystemModel(name="modern")
    language = LanguageModel(code="en", name="english")
    db_session.add_all([version, aspect, system, language])
    db_session.flush()
    profile = AstralAspectInterpretationProfileModel(
        reference_version_id=version.id,
        aspect_id=aspect.id,
        astral_system_id=system.id,
        language_id=language.id,
        title="Fusion",
        summary="Original editorial summary.",
    )
    db_session.add(profile)
    db_session.commit()

    profile.title = "Changed title"

    with pytest.raises(ValueError, match="reference version is immutable"):
        db_session.commit()
    db_session.rollback()


def test_runtime_models_do_not_store_house_system_codes_as_string_columns():
    """Verrouille la référence canonique des systèmes de maisons en SQL relationnel."""
    forbidden_columns = []

    for mapper in Base.registry.mappers:
        table = getattr(mapper.class_, "__table__", None)
        if table is None:
            continue

        for column in table.columns:
            if column.name in {"house_system", "house_system_effective"} and isinstance(
                column.type, (String, Text)
            ):
                forbidden_columns.append(f"{table.name}.{column.name}")

    assert forbidden_columns == []


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

    object_type = AstralObjectTypeModel(code="celestial_body", label="Body", description="Body")
    calculation_type = AstralCalculationTypeModel(
        code="ephemeris",
        label="Ephemeris",
        description="Ephemeris",
    )
    roles = {
        "luminary": AstralAstrologicalRoleModel(
            code="luminary",
            label="Luminary",
            description="Luminary",
        ),
        "personal_planet": AstralAstrologicalRoleModel(
            code="personal_planet",
            label="Personal",
            description="Personal",
        ),
    }
    polarities = {
        "positive": AstralTypicalPolarityModel(name="positive"),
        "neutral": AstralTypicalPolarityModel(name="neutral"),
    }
    db_session.add_all([object_type, calculation_type, *roles.values(), *polarities.values()])
    db_session.flush()

    for i, code in enumerate(PLANET_CODES):
        planet = PlanetModel(code=code, name=code.capitalize())
        db_session.add(planet)
        db_session.flush()
        speed = AstralSpeedModel(name=f"fast_{i}", speed_rank=i + 1)
        db_session.add(speed)
        db_session.flush()
        role_code = "luminary" if code in ("sun", "moon") else "personal_planet"
        polarity_code = "positive" if code == "sun" else "neutral"
        db_session.add(
            AstralPlanetDefinitionModel(
                planet_id=planet.id,
                object_type_id=object_type.id,
                astrological_role_id=roles[role_code].id,
                calculation_type_id=calculation_type.id,
                speed_rank=i + 1,
                speed_class_id=speed.id,
                typical_polarity_id=polarities[polarity_code].id,
                is_physical_body=True,
                is_luminary=code in ("sun", "moon"),
                is_planet=code not in ("sun", "moon"),
                is_visible_to_naked_eye=True,
            )
        )
        profile = PlanetProfileModel(
            reference_version_id=version.id,
            planet_id=planet.id,
            weight_intraday=1.0,
            weight_day_climate=1.0,
            daily_visibility_score=1.0,
            daily_emotional_impact_score=0.5,
            daily_conscious_activation_score=0.8,
            micro_note="Daily note" if code == "sun" else None,
        )
        db_session.add(profile)
    db_session.commit()

    result = repo.get_planet_profiles(version.id)

    assert len(result) == 10
    assert "sun" in result
    sun_profile = result["sun"]
    assert isinstance(sun_profile, PlanetProfileData)
    assert sun_profile.code == "sun"
    assert sun_profile.class_code == "luminary"
    assert sun_profile.typical_polarity == "positive"
    assert sun_profile.daily_conscious_activation_score == 0.8
    assert sun_profile.micro_note == "Daily note"
    assert result["mercury"].class_code == "personal"


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
    """Vérifie que les maîtrises métier sont lues depuis les dignités canoniques."""
    repo = PredictionReferenceRepository(db_session)

    db_session.add(ReferenceVersionModel(version="1.0.0"))
    db_session.flush()

    # Seed unique planet codes needed
    planet_codes = list(dict.fromkeys([*(p for _, p in SIGN_RULERSHIPS), "pluto"]))
    planets = {code: PlanetModel(code=code, name=code.capitalize()) for code in planet_codes}
    db_session.add_all(planets.values())

    signs = {
        code: AstralSignModel(code=code, name=code.capitalize()) for code, _ in SIGN_RULERSHIPS
    }
    db_session.add_all(signs.values())
    dignity_type = AstralDignityTypeModel(code="domicile", name="Domicile")
    traditional_system = AstralSystemModel(name="traditional")
    modern_system = AstralSystemModel(name="modern")
    db_session.add_all([dignity_type, traditional_system, modern_system])
    db_session.flush()

    dignities = [
        AstralPlanetSignDignityModel(
            astral_sign_id=signs[sign_code].id,
            astral_planet_id=planets[planet_code].id,
            astral_dignity_type_id=dignity_type.id,
            astral_system_id=traditional_system.id,
            weight=1.0,
            is_primary=True,
        )
        for sign_code, planet_code in SIGN_RULERSHIPS
    ]
    dignities.append(
        AstralPlanetSignDignityModel(
            astral_sign_id=signs["scorpio"].id,
            astral_planet_id=planets["pluto"].id,
            astral_dignity_type_id=dignity_type.id,
            astral_system_id=modern_system.id,
            weight=1.0,
            is_primary=True,
        )
    )
    db_session.add_all(dignities)
    db_session.commit()

    result = repo.get_sign_rulerships()

    assert len(result) == 12
    assert result["aries"] == "mars"
    assert result["leo"] == "sun"
    assert result["scorpio"] == "mars"


def test_get_aspect_system_inheritance_reads_reference_parent_links(db_session: Session) -> None:
    """Vérifie que l'héritage des systèmes astrologiques vient du référentiel SQL."""
    repo = PredictionReferenceRepository(db_session)
    traditional = AstralSystemModel(name="traditional")
    modern = AstralSystemModel(name="modern")
    experimental = AstralSystemModel(name="experimental", inherits_from=traditional)
    db_session.add_all([traditional, modern, experimental])
    db_session.commit()

    inheritance = repo.get_aspect_system_inheritance()

    assert inheritance == {
        "traditional": None,
        "modern": None,
        "experimental": "traditional",
    }


def test_get_reference_data_exposes_house_axes_from_canonical_tables(db_session: Session) -> None:
    """Les axes de maisons du payload de reference proviennent des tables relationnelles."""
    repo = ReferenceRepository(db_session)

    version = ReferenceVersionModel(version="axis-reference")
    system = AstralSystemModel(name="modern")
    language = LanguageModel(code="en", name="English")
    houses = {number: HouseModel(number=number, name=f"House {number}") for number in range(1, 13)}
    db_session.add_all([version, system, language, *houses.values()])
    db_session.flush()

    axis = AstralHouseAxisDefinitionModel(
        astral_system_id=system.id,
        key="self_relationship",
        title="Self and Relationship",
        summary="Axis summary",
        language_id=language.id,
    )
    db_session.add(axis)
    db_session.flush()
    db_session.add_all(
        [
            AstralHouseAxisMemberModel(
                axis_id=axis.id,
                house_id=houses[1].id,
                opposite_house_id=houses[7].id,
            ),
            AstralHouseAxisMemberModel(
                axis_id=axis.id,
                house_id=houses[7].id,
                opposite_house_id=houses[1].id,
            ),
        ]
    )
    db_session.commit()

    payload = repo.get_reference_data("axis-reference")

    assert payload["house_axes"] == [
        {"house_number": 1, "opposite_house": 7, "theme": "self_relationship"},
        {"house_number": 7, "opposite_house": 1, "theme": "self_relationship"},
    ]


def test_get_planet_sign_dignities_filters_by_system(db_session: Session):
    """Vérifie le chargement générique des dignités pour un système donné."""
    repo = PredictionReferenceRepository(db_session)

    aries = AstralSignModel(code="aries", name="Aries")
    mars = PlanetModel(code="mars", name="Mars")
    pluto = PlanetModel(code="pluto", name="Pluto")
    domicile = AstralDignityTypeModel(code="domicile", name="Domicile")
    traditional = AstralSystemModel(name="traditional")
    modern = AstralSystemModel(name="modern")
    db_session.add_all([aries, mars, pluto, domicile, traditional, modern])
    db_session.flush()
    db_session.add_all(
        [
            AstralPlanetSignDignityModel(
                astral_sign_id=aries.id,
                astral_planet_id=mars.id,
                astral_dignity_type_id=domicile.id,
                astral_system_id=traditional.id,
                weight=1.0,
                is_primary=True,
            ),
            AstralPlanetSignDignityModel(
                astral_sign_id=aries.id,
                astral_planet_id=pluto.id,
                astral_dignity_type_id=domicile.id,
                astral_system_id=modern.id,
                weight=1.0,
                is_primary=True,
            ),
        ]
    )
    db_session.commit()

    dignities = repo.get_planet_sign_dignities(system="traditional")

    assert len(dignities) == 1
    assert dignities[0].sign_code == "aries"
    assert dignities[0].planet_code == "mars"
    assert dignities[0].dignity_type == "domicile"
    assert dignities[0].system == "traditional"


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
    object_type = AstralObjectTypeModel(code="celestial_body", label="Body", description="Body")
    calculation_type = AstralCalculationTypeModel(
        code="ephemeris",
        label="Ephemeris",
        description="Ephemeris",
    )
    role = AstralAstrologicalRoleModel(
        code="luminary",
        label="Luminary",
        description="Luminary",
    )
    speed = AstralSpeedModel(name="fast", speed_rank=1)
    polarity = AstralTypicalPolarityModel(name="positive")
    db_session.add_all([object_type, calculation_type, role, speed, polarity])
    db_session.flush()

    planet = PlanetModel(code="sun", name="Sun")
    db_session.add(planet)
    db_session.flush()
    db_session.add(
        AstralPlanetDefinitionModel(
            planet_id=planet.id,
            object_type_id=object_type.id,
            astrological_role_id=role.id,
            calculation_type_id=calculation_type.id,
            speed_rank=1,
            speed_class_id=speed.id,
            typical_polarity_id=polarity.id,
            is_physical_body=True,
            is_luminary=True,
            is_planet=False,
            is_visible_to_naked_eye=True,
        )
    )
    db_session.add(
        PlanetProfileModel(
            reference_version_id=version.id,
            planet_id=planet.id,
            weight_intraday=1.5,
            weight_day_climate=1.2,
            daily_visibility_score=1.0,
            daily_emotional_impact_score=0.5,
            daily_conscious_activation_score=1.0,
        )
    )

    # Seed one house with profile
    house = HouseModel(number=1, name="House 1")
    db_session.add(house)
    db_session.flush()
    db_session.add(
        HouseProfileModel(
            reference_version_id=version.id,
            house_id=house.id,
            house_kind="angular",
            visibility_weight=1.0,
            base_priority=1,
            keywords_json='["self"]',
            micro_note="Note produit maison 1",
        )
    )

    db_session.commit()

    context = repo.load_prediction_context(version.id)

    assert isinstance(context, PredictionContext)
    assert len(context.categories) >= 1
    assert len(context.planet_profiles) >= 1
    assert len(context.house_astrology_profiles) >= 1
    assert len(context.house_prediction_profiles) >= 1
    assert "sun" in context.planet_profiles
    assert 1 in context.house_astrology_profiles
    assert 1 in context.house_prediction_profiles
    astrology_profile = context.house_astrology_profiles[1]
    prediction_profile = context.house_prediction_profiles[1]
    assert astrology_profile.house_number == 1
    assert astrology_profile.house_kind == "angular"
    assert astrology_profile.natural_theme is None
    assert isinstance(prediction_profile, HousePredictionProfile)
    assert prediction_profile.house_number == 1
    assert prediction_profile.keywords == ("self",)
    assert prediction_profile.micro_note == "Note produit maison 1"


def test_get_fixed_stars_returns_active_db_reference_rows(db_session: Session) -> None:
    """Les étoiles fixes runtime proviennent des définitions DB actives."""
    repo = PredictionReferenceRepository(db_session)
    sign = AstralSignModel(code="leo", name="Leo")
    source = AstralReferenceSourceModel(
        key="fixed-star-source",
        display_name="Fixed Star Source",
        category="internal",
        is_canonical=True,
    )
    constellation = AstralConstellationModel(
        key="leo",
        display_name="Leo",
        latin_name="Leo",
        abbreviation="Leo",
        zodiacal=True,
    )
    epoch = AstralReferenceEpochModel(
        key="j2000",
        display_name="J2000",
        description="Julian epoch 2000",
        epoch_type="julian_epoch",
        julian_year=2000.0,
        is_standard=True,
    )
    category = AstralZodiacalReferenceSystemCategoryModel(
        key="tropical",
        display_name="Tropical",
        description="Tropical",
    )
    zodiacal_system = AstralZodiacalReferenceSystemModel(
        key="tropical",
        display_name="Tropical",
        category=category,
        description="Tropical",
        requires_ayanamsha=False,
    )
    keywords = AstralFixedStarKeywordModel(keywords_json='["royalty"]')
    regulus = AstralFixedStarModel(key="regulus", display_name="Regulus")
    algol = AstralFixedStarModel(key="algol", display_name="Algol")
    db_session.add_all(
        [
            sign,
            source,
            constellation,
            epoch,
            category,
            zodiacal_system,
            keywords,
            regulus,
            algol,
        ]
    )
    db_session.flush()
    db_session.add_all(
        [
            AstralFixedStarDefinitionModel(
                fixed_star_id=regulus.id,
                constellation_id=constellation.id,
                zodiacal_reference_system_id=zodiacal_system.id,
                reference_epoch_id=epoch.id,
                ecliptic_longitude_deg=150.0,
                zodiac_sign_id=sign.id,
                zodiac_degree=0.0,
                astral_fixed_star_keywords_id=keywords.id,
                source_id=source.id,
                is_active=True,
            ),
            AstralFixedStarDefinitionModel(
                fixed_star_id=algol.id,
                constellation_id=constellation.id,
                zodiacal_reference_system_id=zodiacal_system.id,
                reference_epoch_id=epoch.id,
                ecliptic_longitude_deg=56.0,
                zodiac_sign_id=sign.id,
                zodiac_degree=26.0,
                astral_fixed_star_keywords_id=keywords.id,
                source_id=source.id,
                is_active=False,
            ),
        ]
    )
    db_session.commit()

    fixed_stars = repo.get_fixed_stars()

    assert fixed_stars == (
        FixedStarData(key="regulus", display_name="Regulus", ecliptic_longitude_deg=150.0),
    )


def test_category_weight_queries_filter_joined_categories_by_reference_version(db_session: Session):
    repo = PredictionReferenceRepository(db_session)

    version_a = ReferenceVersionModel(version="1.0.0")
    version_b = ReferenceVersionModel(version="2.0.0")
    db_session.add_all([version_a, version_b])
    db_session.flush()

    planet = PlanetModel(code="sun", name="Sun")
    house = HouseModel(number=1, name="House 1")
    db_session.add_all([planet, house])
    db_session.flush()

    category_a = PredictionCategoryModel(
        reference_version_id=version_a.id,
        code="love",
        name="Love",
        display_name="Love",
        sort_order=1,
        is_enabled=True,
    )
    category_b = PredictionCategoryModel(
        reference_version_id=version_b.id,
        code="foreign",
        name="Foreign",
        display_name="Foreign",
        sort_order=1,
        is_enabled=True,
    )
    point = AstroPointModel(
        code="asc",
        name="Asc",
        point_type="angle",
    )
    db_session.add_all([category_a, category_b, point])
    db_session.flush()

    db_session.add_all(
        [
            PlanetCategoryWeightModel(
                reference_version_id=version_a.id,
                planet_id=planet.id,
                category_id=category_a.id,
                weight=0.8,
                influence_role="primary",
            ),
            PlanetCategoryWeightModel(
                reference_version_id=version_b.id,
                planet_id=planet.id,
                category_id=category_b.id,
                weight=0.2,
                influence_role="secondary",
            ),
            HouseCategoryWeightModel(
                reference_version_id=version_a.id,
                house_id=house.id,
                category_id=category_a.id,
                weight=0.7,
                routing_role="primary",
            ),
            HouseCategoryWeightModel(
                reference_version_id=version_b.id,
                house_id=house.id,
                category_id=category_b.id,
                weight=0.1,
                routing_role="secondary",
            ),
            PointCategoryWeightModel(
                reference_version_id=version_a.id,
                point_id=point.id,
                category_id=category_a.id,
                weight=0.6,
            ),
            PointCategoryWeightModel(
                reference_version_id=version_b.id,
                point_id=point.id,
                category_id=category_b.id,
                weight=0.2,
            ),
        ]
    )
    db_session.commit()

    planet_weights = repo.get_planet_category_weights(version_a.id)
    house_weights = repo.get_house_category_weights(version_a.id)
    point_weights = repo.get_point_category_weights(version_a.id)

    assert [weight.category_code for weight in planet_weights] == ["love"]
    assert [weight.category_code for weight in house_weights] == ["love"]
    assert [weight.category_code for weight in point_weights] == ["love"]

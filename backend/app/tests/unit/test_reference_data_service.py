import json
from typing import Any, cast

import pytest
from sqlalchemy import delete, func, select

from app.infra.db.base import Base
from app.infra.db.models.interpretation_reference import (
    AstralAspectInterpretationProfileModel,
    AstralPlanetInterpretationProfileModel,
    HouseInterpretationProfileModel,
)
from app.infra.db.models.prediction_reference import (
    AstralAspectOrbRuleModel,
    PredictionCategoryModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAnglePointModel,
    AstralAspectFamilyModel,
    AstralAstrologicalRoleModel,
    AstralCalculationTypeModel,
    AstralDignityTypeModel,
    AstralHouseModalityModel,
    AstralObjectTypeModel,
    AstralSignModel,
    AstralSystemModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.models.translation_reference import (
    AstralAspectInterpretationProfileTranslationModel,
    AstralAspectTranslationModel,
    AstralHouseInterpretationProfileTranslationModel,
    AstralHouseTranslationModel,
    AstralPlanetInterpretationProfileTranslationModel,
    AstralPlanetTranslationModel,
    AstralSignTranslationModel,
)
from app.infra.db.repositories.astrology_reference_sources import (
    astrology_research_path,
    load_astral_sign_rows,
)
from app.services.reference_data.translation_seed_service import sync_astral_translation_seed_data
from app.services.reference_data_service import ReferenceDataService, ReferenceDataServiceError
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_reference_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            AspectModel,
            HouseModel,
            AstralSignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def test_astral_sign_seed_source_matches_model_contract() -> None:
    """Le JSON dédié expose uniquement les champs persistés par AstralSignModel."""
    source_path = astrology_research_path("astral_signs.json")
    payload = json.loads(source_path.read_text(encoding="utf-8"))

    assert payload["name"] == AstralSignModel.__tablename__
    assert payload["structure"] == {"id": "integer", "code": "string", "name": "string"}
    assert [set(row) for row in payload["data"]] == [{"id", "code", "name"}] * 12


def test_seed_reference_version_is_idempotent() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        version_1 = ReferenceDataService.seed_reference_version(db, version="1.0.0")
    with open_app_test_db_session() as db:
        version_2 = ReferenceDataService.seed_reference_version(db, version="1.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")

    assert version_1 == "1.0.0"
    assert version_2 == "1.0.0"
    assert payload["version"] == "1.0.0"
    assert len(payload["planets"]) == 10
    assert len(payload["signs"]) == 12
    assert len(payload["aspects"]) == 20
    assert len(payload["aspect_orb_rules"]) == 79
    systems = cast(list[dict[str, Any]], payload["astral_systems"])
    assert {item["code"]: item["inherits_from_system_code"] for item in systems} == {
        "hellenistic": "traditional",
        "medieval": "traditional",
        "modern": None,
        "traditional": None,
    }
    planets = cast(list[dict[str, Any]], payload["planets"])
    signs = cast(list[dict[str, Any]], payload["signs"])
    aspects = cast(list[dict[str, Any]], payload["aspects"])
    expected_sign_rows = load_astral_sign_rows()
    assert any(item["code"] == "sun" and item["name"] == "Sun" for item in planets)
    assert any(
        item["code"] == "pluto" and item["name"] == "Pluto" and item["swe_id"] == 9
        for item in planets
    )
    assert {item["code"] for item in signs} == {
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    }
    assert [item["code"] for item in signs] == [str(row["code"]) for row in expected_sign_rows]
    assert {item["code"] for item in aspects} >= {
        "conjunction",
        "sextile",
        "square",
        "trine",
        "opposition",
        "quincunx",
        "septile",
    }
    expected_default_orbs = {
        "conjunction": 8.0,
        "sextile": 4.0,
        "square": 6.0,
        "trine": 6.0,
        "opposition": 8.0,
    }
    assert {
        item["code"]: item.get("default_orb_deg")
        for item in aspects
        if item["code"] in expected_default_orbs
    } == expected_default_orbs
    with open_app_test_db_session() as db:
        version = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        assert version is not None
        assert (
            db.scalar(
                select(func.count())
                .select_from(HouseInterpretationProfileModel)
                .where(HouseInterpretationProfileModel.reference_version_id == version.id)
            )
            == 12
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AstralAspectOrbRuleModel)
                .where(AstralAspectOrbRuleModel.reference_version_id == version.id)
            )
            == 79
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AstralAspectInterpretationProfileModel)
                .where(AstralAspectInterpretationProfileModel.reference_version_id == version.id)
            )
            == 20
        )
        assert db.scalar(select(func.count()).select_from(AstralAnglePointModel)) == 4
        assert db.scalar(select(func.count()).select_from(AstralAstrologicalRoleModel)) == 6
        assert db.scalar(select(func.count()).select_from(AstralCalculationTypeModel)) == 2
        assert db.scalar(select(func.count()).select_from(AstralHouseModalityModel)) == 3
        assert db.scalar(select(func.count()).select_from(AstralObjectTypeModel)) == 3
        ascendant = db.scalar(
            select(AstralAnglePointModel).where(AstralAnglePointModel.code == "asc")
        )
        assert ascendant is not None
        assert ascendant.short_label == "ASC"
        assert ascendant.associated_house == 1
        house_10_profile = db.scalar(
            select(HouseInterpretationProfileModel)
            .join(HouseModel, HouseInterpretationProfileModel.house_id == HouseModel.id)
            .where(
                HouseInterpretationProfileModel.reference_version_id == version.id,
                HouseInterpretationProfileModel.language == "en",
                HouseModel.number == 10,
            )
            .join(
                AstralSystemModel,
                HouseInterpretationProfileModel.astral_system_id == AstralSystemModel.id,
            )
            .where(AstralSystemModel.name == "modern")
        )
        assert house_10_profile is not None
        assert house_10_profile.title == "Career and Public Role"
        assert "career" in json.loads(house_10_profile.core_keywords_json or "[]")


def test_seed_reference_version_populates_translation_tables() -> None:
    """Le seed de référence alimente les traductions stables et éditoriales."""
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")

    with open_app_test_db_session() as db:
        assert db.scalar(select(func.count()).select_from(AstralSignTranslationModel)) == 48
        assert db.scalar(select(func.count()).select_from(AstralHouseTranslationModel)) == 48
        assert db.scalar(select(func.count()).select_from(AstralPlanetTranslationModel)) == 40
        assert db.scalar(select(func.count()).select_from(AstralAspectTranslationModel)) == 80
        assert (
            db.scalar(
                select(func.count()).select_from(AstralHouseInterpretationProfileTranslationModel)
            )
            == 48
        )
        assert (
            db.scalar(
                select(func.count()).select_from(AstralAspectInterpretationProfileTranslationModel)
            )
            == 80
        )
        assert (
            db.scalar(
                select(func.count()).select_from(AstralPlanetInterpretationProfileTranslationModel)
            )
            == 0
        )

        aries_fr = db.scalar(
            select(AstralSignTranslationModel.translated_name)
            .join(AstralSignTranslationModel.sign)
            .where(
                AstralSignModel.code == "aries",
                AstralSignTranslationModel.language.has(code="fr"),
            )
        )
        assert aries_fr == "Bélier"


def test_translation_seed_populates_planet_interpretation_translations_when_sources_exist() -> None:
    """Les traductions éditoriales planétaires se rattachent aux profils source existants."""
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        version = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        sun = db.scalar(select(PlanetModel).where(PlanetModel.code == "sun"))
        modern = db.scalar(select(AstralSystemModel).where(AstralSystemModel.name == "modern"))
        english = db.scalar(select(LanguageModel).where(LanguageModel.code == "en"))
        assert version is not None
        assert sun is not None
        assert modern is not None
        assert english is not None
        db.add(
            AstralPlanetInterpretationProfileModel(
                reference_version_id=version.id,
                planet_id=sun.id,
                astral_system_id=modern.id,
                language_id=english.id,
                title="Identity and Vitality",
            )
        )
        db.flush()
        sync_astral_translation_seed_data(db, version.id)
        db.commit()

    with open_app_test_db_session() as db:
        rows = db.scalars(select(AstralPlanetInterpretationProfileTranslationModel)).all()
        assert len(rows) == 4
        assert {row.language.code for row in rows} == {"fr", "es", "de", "it"}
        assert (
            next(row for row in rows if row.language.code == "fr").title == "Identité et vitalité"
        )


def test_seed_reference_version_repairs_partial_existing_version() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        partial = ReferenceVersionModel(version="2.0.0", description="partial", is_locked=True)
        db.add(partial)
        db.flush()
        family = AstralAspectFamilyModel(name="major")
        db.add(family)
        db.flush()
        db.add(
            AspectModel(
                code="conjunction",
                name="Conjunction",
                angle=0,
                family=family.id,
            )
        )
        db.commit()

    with open_app_test_db_session() as db:
        version = ReferenceDataService.seed_reference_version(db, version="2.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="2.0.0")

    assert version == "2.0.0"
    assert payload["version"] == "2.0.0"
    assert len(payload["planets"]) == 10
    assert len(payload["signs"]) == 12
    assert len(payload["houses"]) == 12
    house_axes = cast(list[dict[str, Any]], payload["house_axes"])
    assert len(house_axes) == 12
    assert {item["house_number"]: item["opposite_house"] for item in house_axes} == {
        1: 7,
        2: 8,
        3: 9,
        4: 10,
        5: 11,
        6: 12,
        7: 1,
        8: 2,
        9: 3,
        10: 4,
        11: 5,
        12: 6,
    }
    assert len(payload["aspects"]) == 20
    assert len(payload["aspect_orb_rules"]) == 79
    assert "characteristics" not in payload


def test_seed_reference_version_repairs_superficially_complete_catalog() -> None:
    """Un catalogue superficiellement complet est resynchronisé depuis les JSON."""
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        partial = ReferenceVersionModel(version="3.0.0", description="partial", is_locked=True)
        db.add(partial)
        family = AstralAspectFamilyModel(name="major")
        db.add_all(
            [
                PlanetModel(code="sun", name="Wrong Sun"),
                AstralSignModel(code="aries", name="Wrong Aries"),
                AstralDignityTypeModel(code="domicile", name="Wrong Domicile"),
                AstralSystemModel(name="modern"),
                HouseModel(number=1, name="Wrong Self"),
                family,
            ]
        )
        db.flush()
        db.add(
            AspectModel(code="conjunction", name="Wrong Conjunction", angle=99, family=family.id)
        )
        db.commit()

    with open_app_test_db_session() as db:
        version = ReferenceDataService.seed_reference_version(db, version="3.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="3.0.0")

    assert version == "3.0.0"
    assert len(payload["planets"]) == 10
    assert len(payload["signs"]) == 12
    assert len(payload["houses"]) == 12
    assert len(payload["aspects"]) == 20
    planets = cast(list[dict[str, Any]], payload["planets"])
    houses = cast(list[dict[str, Any]], payload["houses"])
    aspects = cast(list[dict[str, Any]], payload["aspects"])
    seeded_sun = next(item for item in planets if item["code"] == "sun")
    assert seeded_sun["name"] == "Sun"
    assert seeded_sun["swe_id"] == 0
    assert next(item for item in houses if item["number"] == 1)["name"] == "Self"
    assert next(item for item in aspects if item["code"] == "conjunction")["angle"] == 0.0


def test_reference_data_contract_does_not_expose_characteristics() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")

    aspects = cast(list[dict[str, Any]], payload["aspects"])
    square = next(item for item in aspects if item["code"] == "square")
    assert "characteristics" not in payload
    assert "sign_rulerships" not in payload
    assert "orb_luminaries" not in square
    assert "orb_pair_overrides" not in square
    assert square["default_orb_deg"] == 6.0


def test_clone_reference_version_preserves_previous_version() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        source_version = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        if source_version is not None:
            db.add(
                PlanetModel(
                    code="test_planet",
                    name="Test Planet",
                )
            )
            db.commit()
        clone = ReferenceDataService.clone_reference_version(
            db,
            source_version="1.0.0",
            new_version="1.1.0",
        )
        source_payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")
        cloned_payload = ReferenceDataService.get_active_reference_data(db, version=clone)

    assert clone == "1.1.0"
    assert source_payload["version"] == "1.0.0"
    assert cloned_payload["version"] == "1.1.0"
    assert len(source_payload["planets"]) == len(cloned_payload["planets"])
    cloned_planets = cast(list[dict[str, Any]], cloned_payload["planets"])
    assert any(item["code"] == "test_planet" for item in cloned_planets)


def test_locked_reference_version_rejects_parametric_mutation() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        version = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        assert version is not None
        category = PredictionCategoryModel(
            reference_version_id=version.id,
            code="energy",
            name="Energy",
            display_name="Energy",
        )
        db.add(category)
        db.commit()

        category.name = "Mutated Energy"
        try:
            db.commit()
            assert False, "expected commit failure on locked reference version"
        except ValueError as error:
            db.rollback()
            assert str(error) == "reference version is immutable"


def test_validate_orb_overrides_accepts_values_between_zero_and_fifteen() -> None:
    validated = ReferenceDataService.validate_orb_overrides(
        {
            "conjunction": 7.5,
            "sun-moon": 9,
        }
    )
    assert validated == {"conjunction": 7.5, "sun-moon": 9.0}


@pytest.mark.parametrize(
    ("input_value", "expected_reason"),
    [
        (0, "must_be_gt_0"),
        (-1, "must_be_gt_0"),
        (15.1, "must_be_lte_15"),
    ],
)
def test_validate_orb_overrides_rejects_out_of_range_values(
    input_value: float,
    expected_reason: str,
) -> None:
    with pytest.raises(ReferenceDataServiceError) as error:
        ReferenceDataService.validate_orb_overrides({"conjunction": input_value})
    assert error.value.code == "invalid_orb_override"
    assert error.value.details.get("reason") == expected_reason

import json
from typing import Any, cast

import pytest
from sqlalchemy import delete, func, select

from app.infra.db.base import Base
from app.infra.db.models.interpretation_reference import HouseInterpretationProfileModel
from app.infra.db.models.prediction_reference import (
    AstralAspectOrbRuleModel,
    PredictionCategoryModel,
)
from app.infra.db.models.reference import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralSignModel,
    AstralSystemModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
)
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
    assert len(payload["aspect_orb_rules"]) == 159
    planets = cast(list[dict[str, Any]], payload["planets"])
    signs = cast(list[dict[str, Any]], payload["signs"])
    aspects = cast(list[dict[str, Any]], payload["aspects"])
    assert any(item["code"] == "sun" and item["name"] == "Sun" for item in planets)
    assert any(item["code"] == "pluto" and item["name"] == "Pluto" for item in planets)
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
            == 159
        )
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
    assert len(payload["aspects"]) == 20
    assert len(payload["aspect_orb_rules"]) == 159
    assert "characteristics" not in payload


def test_reference_data_contract_does_not_expose_characteristics() -> None:
    _cleanup_reference_tables()
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")

    aspects = cast(list[dict[str, Any]], payload["aspects"])
    square = next(item for item in aspects if item["code"] == "square")
    assert "characteristics" not in payload
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

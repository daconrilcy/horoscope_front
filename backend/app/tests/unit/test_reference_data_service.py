from typing import Any, cast

import pytest
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.session import SessionLocal, engine
from app.services.reference_data_service import ReferenceDataService, ReferenceDataServiceError


def _cleanup_reference_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def test_seed_reference_version_is_idempotent() -> None:
    _cleanup_reference_tables()
    with SessionLocal() as db:
        version_1 = ReferenceDataService.seed_reference_version(db, version="1.0.0")
    with SessionLocal() as db:
        version_2 = ReferenceDataService.seed_reference_version(db, version="1.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")

    assert version_1 == "1.0.0"
    assert version_2 == "1.0.0"
    assert payload["version"] == "1.0.0"
    assert len(payload["planets"]) == 10
    assert len(payload["signs"]) == 2
    assert len(payload["aspects"]) == 5
    planets = cast(list[dict[str, Any]], payload["planets"])
    aspects = cast(list[dict[str, Any]], payload["aspects"])
    assert any(item["code"] == "sun" and item["name"] == "Sun" for item in planets)
    assert any(item["code"] == "pluto" and item["name"] == "Pluto" for item in planets)
    assert {item["code"] for item in aspects} == {
        "conjunction",
        "sextile",
        "square",
        "trine",
        "opposition",
    }
    expected_default_orbs = {
        "conjunction": 8.0,
        "sextile": 4.0,
        "square": 6.0,
        "trine": 6.0,
        "opposition": 8.0,
    }
    assert {item["code"]: item.get("default_orb_deg") for item in aspects} == expected_default_orbs


def test_clone_reference_version_preserves_previous_version() -> None:
    _cleanup_reference_tables()
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        source_version = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        if source_version is not None:
            db.add(
                PlanetModel(
                    reference_version_id=source_version.id,
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


def test_locked_reference_version_rejects_in_place_mutation() -> None:
    _cleanup_reference_tables()
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        planet = db.scalar(select(PlanetModel).where(PlanetModel.code == "sun"))
        assert planet is not None
        planet.name = "Mutated Sun"
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

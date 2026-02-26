from typing import Any, cast

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
from app.services.reference_data_service import ReferenceDataService


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

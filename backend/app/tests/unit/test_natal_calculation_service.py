from sqlalchemy import delete

from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.session import SessionLocal, engine
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService


def _cleanup_reference_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChartResultModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def test_calculate_natal_is_deterministic() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        first = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        second = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")

    assert first == second
    assert first.reference_version == "1.0.0"
    assert len(first.planet_positions) >= 3
    assert len(first.houses) == 12


def test_calculate_natal_fails_with_unknown_reference_version() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        try:
            NatalCalculationService.calculate(db, payload, reference_version="9.9.9")
        except NatalCalculationError as error:
            assert error.code == "reference_version_not_found"
        else:
            raise AssertionError("Expected NatalCalculationError")


def test_calculate_natal_fails_with_incomplete_reference_data() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        db.execute(delete(HouseModel))
        db.commit()
        try:
            NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        except NatalCalculationError as error:
            assert error.code == "invalid_reference_data"
            assert error.details["field"] == "houses"
        else:
            raise AssertionError("Expected NatalCalculationError")

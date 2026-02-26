import pytest
from sqlalchemy import delete

from app.domain.astrology.calculators.houses import assign_house_number
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

SIGNS = [
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
]


def _cleanup_reference_tables() -> None:
    ReferenceDataService._clear_cache_for_tests()
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


def test_calculate_natal_none_reference_version_resolves_to_active_version_in_error() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        with pytest.raises(NatalCalculationError) as error:
            NatalCalculationService.calculate(db, payload, reference_version=None)

    assert error.value.code == "reference_version_not_found"
    assert error.value.details["version"] == "1.0.0"


def test_calculate_natal_keeps_sign_and_house_consistent_with_geometry() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1973-03-14",
        birth_time="11:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")

    houses_by_number = {house.number: house.cusp_longitude for house in result.houses}
    ordered_houses = [houses_by_number[number] for number in sorted(houses_by_number)]

    def _contains(longitude: float, start: float, end: float) -> bool:
        if start <= end:
            return start <= longitude < end
        return longitude >= start or longitude < end

    for planet in result.planet_positions:
        sign_index = int((planet.longitude % 360.0) // 30.0) % 12
        assert planet.sign_code == SIGNS[sign_index]

        house_idx = planet.house_number - 1
        start = ordered_houses[house_idx]
        end = ordered_houses[(house_idx + 1) % 12]
        assert _contains(planet.longitude % 360.0, start, end)


def test_calculate_natal_hard_fails_on_sign_longitude_inconsistency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1973-04-24",
        birth_time="11:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    def _bad_positions(*args: object, **kwargs: object) -> list[dict[str, object]]:
        return [
            {
                "planet_code": "sun",
                "longitude": 34.08,
                "sign_code": "aries",
                "house_number": 1,
            }
        ]

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation.calculate_planet_positions",
        _bad_positions,
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        with pytest.raises(NatalCalculationError) as error:
            NatalCalculationService.calculate(db, payload, reference_version="1.0.0")

    assert error.value.code == "inconsistent_natal_result"


def test_assign_house_number_exact_cusp_belongs_to_next_house() -> None:
    houses = [
        {"number": 1, "cusp_longitude": 0.0},
        {"number": 2, "cusp_longitude": 30.0},
        {"number": 3, "cusp_longitude": 60.0},
        {"number": 4, "cusp_longitude": 90.0},
        {"number": 5, "cusp_longitude": 120.0},
        {"number": 6, "cusp_longitude": 150.0},
        {"number": 7, "cusp_longitude": 180.0},
        {"number": 8, "cusp_longitude": 210.0},
        {"number": 9, "cusp_longitude": 240.0},
        {"number": 10, "cusp_longitude": 270.0},
        {"number": 11, "cusp_longitude": 300.0},
        {"number": 12, "cusp_longitude": 330.0},
    ]
    # Convention semi-open: [start, end), so longitude == cusp VII belongs to house VII.
    assert assign_house_number(180.0, houses) == 7
    # End cusp of house VII is cusp VIII; longitude == 210.0 belongs to house VIII.
    assert assign_house_number(210.0, houses) == 8


def test_assign_house_number_wrap_interval_contains_359_and_0() -> None:
    houses = [
        {"number": 1, "cusp_longitude": 138.46},
        {"number": 2, "cusp_longitude": 168.46},
        {"number": 3, "cusp_longitude": 198.46},
        {"number": 4, "cusp_longitude": 228.46},
        {"number": 5, "cusp_longitude": 258.46},
        {"number": 6, "cusp_longitude": 288.46},
        {"number": 7, "cusp_longitude": 318.46},
        {"number": 8, "cusp_longitude": 348.46},
        {"number": 9, "cusp_longitude": 18.46},
        {"number": 10, "cusp_longitude": 48.46},
        {"number": 11, "cusp_longitude": 78.46},
        {"number": 12, "cusp_longitude": 108.46},
    ]
    # Wrap interval [348.46, 18.46) includes both 359° and 0°.
    assert assign_house_number(359.0, houses) == 8
    assert assign_house_number(0.0, houses) == 8
    # End cusp belongs to next house due to semi-open interval.
    assert assign_house_number(18.46, houses) == 9


def test_calculate_natal_fails_when_houses_have_duplicate_cusps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1973-04-24",
        birth_time="11:00",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    def _bad_houses(*args: object, **kwargs: object) -> list[dict[str, object]]:
        return [{"number": n, "cusp_longitude": 0.0} for n in range(1, 13)]

    monkeypatch.setattr(
        "app.domain.astrology.natal_calculation.calculate_houses",
        _bad_houses,
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        with pytest.raises(NatalCalculationError) as error:
            NatalCalculationService.calculate(db, payload, reference_version="1.0.0")

    assert error.value.code == "invalid_reference_data"
    assert error.value.details["field"] == "houses"
    assert error.value.details["reason"] == "duplicate_cusp_longitude"


def test_calculate_natal_calls_timeout_check_around_reference_loading() -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    checkpoints: list[str] = []

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")

        def _timeout_check() -> None:
            checkpoints.append("tick")

        NatalCalculationService.calculate(
            db,
            payload,
            reference_version="1.0.0",
            timeout_check=_timeout_check,
        )

    assert len(checkpoints) >= 2


def test_calculate_natal_uses_reference_cache_for_same_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_reference_tables()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    calls = {"count": 0}
    from app.infra.db.repositories.reference_repository import ReferenceRepository

    original = ReferenceRepository.get_reference_data

    def _spy_get_reference_data(self: object, version: str) -> dict[str, object]:
        calls["count"] += 1
        return original(self, version)

    monkeypatch.setattr(
        "app.services.reference_data_service.ReferenceRepository.get_reference_data",
        _spy_get_reference_data,
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        NatalCalculationService.calculate(db, payload, reference_version="1.0.0")

    assert calls["count"] == 1


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

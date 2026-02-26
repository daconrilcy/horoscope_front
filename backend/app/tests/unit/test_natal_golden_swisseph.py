from __future__ import annotations

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from app.domain.astrology.natal_preparation import BirthInput
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
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService

PLANET_TOLERANCE_DEG = 0.01
ANGLE_TOLERANCE_DEG = 0.05


def _is_swisseph_available() -> bool:
    try:
        import swisseph  # noqa: F401
        return True
    except ImportError:
        return False


requires_swisseph = pytest.mark.skipif(
    not _is_swisseph_available(),
    reason="pyswisseph non disponible",
)


def _cleanup_reference_tables() -> None:
    ReferenceDataService._clear_cache_for_tests()
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


def _assert_close(actual: float, expected: float, tol: float, label: str) -> None:
    assert abs(actual - expected) <= tol, (
        f"{label}: attendu={expected:.6f}, obtenu={actual:.6f}, "
        f"delta={abs(actual - expected):.6f} > {tol}"
    )


@pytest.mark.golden
@requires_swisseph
def test_natal_swisseph_golden_paris_1973_includes_planets_and_angles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _cleanup_reference_tables()
    monkeypatch.setattr("app.services.natal_calculation_service.settings.swisseph_enabled", True)
    monkeypatch.setattr(
        "app.core.ephemeris.get_bootstrap_result",
        lambda: SimpleNamespace(success=True, error=None, path_version="moshier-local"),
    )

    birth_input = BirthInput(
        birth_date="1973-04-24",
        birth_time="11:00",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8588897,
        birth_lon=2.320041,
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            reference_version="1.0.0",
            accurate=True,
        )

    assert result.engine == "swisseph"
    assert result.house_system == "placidus"

    planets = {p.planet_code: p for p in result.planet_positions}
    assert {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"}.issubset(planets)

    _assert_close(planets["sun"].longitude, 34.0817569, PLANET_TOLERANCE_DEG, "sun.longitude")
    _assert_close(planets["moon"].longitude, 289.3256361, PLANET_TOLERANCE_DEG, "moon.longitude")
    _assert_close(
        planets["mercury"].longitude,
        10.3694115,
        PLANET_TOLERANCE_DEG,
        "mercury.longitude",
    )

    assert planets["sun"].is_retrograde is False
    assert planets["mercury"].speed_longitude is not None
    assert planets["mercury"].is_retrograde is not None

    houses = {h.number: h.cusp_longitude for h in result.houses}
    _assert_close(houses[1], 117.9631694, ANGLE_TOLERANCE_DEG, "ascendant_house_1")
    _assert_close(houses[10], 5.0250079, ANGLE_TOLERANCE_DEG, "mc_house_10")

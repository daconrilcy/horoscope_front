"""Tests d'integration pour le mode accurate du pipeline natal.

Couvre les AC 2, 3, 4 (erreurs 422) et la non-regression du mode simplified.
"""
from __future__ import annotations

import pytest
from sqlalchemy import delete

from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.user_natal_chart_service import (
    UserNatalChartService,
    UserNatalChartServiceError,
)
from app.domain.astrology.natal_calculation import NatalCalculationError


@pytest.fixture
def mock_swisseph(monkeypatch: pytest.MonkeyPatch) -> None:
    """Active SwissEph et mock le bootstrap pour les tests d'intégration."""
    from app.services import natal_calculation_service
    from app.core import ephemeris
    
    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", True)
    
    class MockBootstrap:
        success = True
        path_version = "test_path_v1"
        error = None
        
    monkeypatch.setattr(ephemeris, "get_bootstrap_result", lambda: MockBootstrap())
    
    # Mock des providers pour éviter d'appeler pyswisseph réel
    def _mock_positions(jdut: float, planet_codes: list[str], **kwargs: object) -> list[dict[str, object]]:
        return [{"planet_code": code, "longitude": 0.0, "sign_code": "aries"} for code in planet_codes]
        
    def _mock_houses(jdut: float, lat: float, lon: float, house_numbers: list[int], **kwargs: object) -> tuple[list[dict[str, object]], str]:
        return [{"number": n, "cusp_longitude": float((n - 1) * 30)} for n in house_numbers], "placidus"

    monkeypatch.setattr("app.domain.astrology.natal_calculation._build_swisseph_positions", _mock_positions)
    monkeypatch.setattr("app.domain.astrology.natal_calculation._build_swisseph_houses", _mock_houses)


def _cleanup() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChartResultModel,
            GeoPlaceResolvedModel,
            UserBirthProfileModel,
            UserModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_user_with_profile(
    birth_time: str | None = "10:30",
    birth_timezone: str = "Europe/Paris",
    email: str = "user_accurate@example.com",
) -> int:
    """Cree un utilisateur avec profil natal sans birth_place_resolved_id."""
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time=birth_time,
        birth_place="Paris",
        birth_timezone=birth_timezone,
    )
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        UserBirthProfileService.upsert_for_user(db, user_id=auth.user.id, payload=payload)
        db.commit()
        return auth.user.id


def _create_user_with_resolved_place(
    birth_time: str | None = "10:30",
    birth_timezone: str = "Europe/Paris",
    email: str = "user_resolved@example.com",
) -> int:
    """Cree un utilisateur avec profil natal ET birth_place_resolved_id."""
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123")
        resolved = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=99999,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        db.add(resolved)
        db.flush()
        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time=birth_time,
            birth_place="Paris",
            birth_timezone=birth_timezone,
            place_resolved_id=resolved.id,
            birth_lat=48.8566,
            birth_lon=2.3522,
        )
        UserBirthProfileService.upsert_for_user(db, user_id=auth.user.id, payload=payload)
        db.commit()
        return auth.user.id


def test_accurate_mode_missing_birth_time_returns_error(mock_swisseph: None) -> None:
    """AC2: accurate=True avec place_resolved mais sans birth_time -> missing_birth_time."""
    _cleanup()
    user_id = _create_user_with_resolved_place(birth_time=None)

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        with pytest.raises(UserNatalChartServiceError) as exc_info:
            UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=True)

    assert exc_info.value.code == "missing_birth_time"


def test_accurate_mode_missing_birth_place_resolved_returns_error(mock_swisseph: None) -> None:
    """AC3: accurate=True sans birth_place_resolved_id -> missing_birth_place_resolved."""
    _cleanup()
    user_id = _create_user_with_profile(birth_time="10:30")

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        with pytest.raises(UserNatalChartServiceError) as exc_info:
            UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=True)

    assert exc_info.value.code == "missing_birth_place_resolved"


def test_non_accurate_mode_still_works() -> None:
    """Non-regression: accurate=False genere un theme natal sans SwissEph."""
    _cleanup()
    user_id = _create_user_with_profile(birth_time="10:30", email="user_simplified@example.com")

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=False)

    assert result.chart_id is not None
    assert len(result.result.planet_positions) >= 1
    assert len(result.result.houses) == 12


def test_accurate_mode_swisseph_disabled_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """accurate=True mais SWISSEPH_ENABLED=False -> NatalCalculationError."""
    _cleanup()

    from app.services import natal_calculation_service

    monkeypatch.setattr(natal_calculation_service.settings, "swisseph_enabled", False)

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        birth_input = BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        from app.services.natal_calculation_service import NatalCalculationService

        with pytest.raises(NatalCalculationError) as exc_info:
            NatalCalculationService.calculate(
                db=db,
                birth_input=birth_input,
                accurate=True,
            )

    assert exc_info.value.code == "natal_engine_unavailable"


# ---------------------------------------------------------------------------
# Story 20-5: Tests metadata complète
# ---------------------------------------------------------------------------

def test_metadata_always_present_in_generated_chart() -> None:
    """AC4: metadata contient toujours reference_version, ruleset_version, timezone_used."""
    _cleanup()
    user_id = _create_user_with_profile(
        birth_time="10:30",
        birth_timezone="Europe/Paris",
        email="user_meta@example.com",
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        data = UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=False)

    meta = data.metadata
    # AC4 : tous les champs obligatoires présents
    assert meta.reference_version is not None and meta.reference_version != ""
    assert meta.ruleset_version is not None and meta.ruleset_version != ""
    assert meta.timezone_used is not None  # non-null, dérivé de prepared_input.birth_timezone
    assert meta.timezone_used == "Europe/Paris"
    # ephemeris_path_version est un champ présent dans le modèle (None pour simplified)
    assert hasattr(meta, "ephemeris_path_version")


def test_metadata_defaults_simplified_engine() -> None:
    """generate_for_user(accurate=False) → engine=simplified, zodiac=tropical, frame=geocentric."""
    _cleanup()
    user_id = _create_user_with_profile(
        birth_time="10:30",
        email="user_defaults@example.com",
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        data = UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=False)

    meta = data.metadata
    assert meta.engine == "simplified"
    assert meta.zodiac == "tropical"
    assert meta.frame == "geocentric"
    assert meta.ayanamsa is None
    assert meta.ephemeris_path_version is None


def test_get_latest_for_user_reconstructs_metadata_from_result() -> None:
    """get_latest_for_user() reconstruite la metadata depuis le résultat stocké en DB."""
    _cleanup()
    user_id = _create_user_with_profile(
        birth_time="10:30",
        email="user_read_meta@example.com",
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        # Générer d'abord
        UserNatalChartService.generate_for_user(db=db, user_id=user_id, accurate=False)
        db.commit()

    with SessionLocal() as db:
        # Récupérer et vérifier metadata reconstruite
        read_data = UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)

    meta = read_data.metadata
    assert meta.reference_version is not None and meta.reference_version != ""
    assert meta.ruleset_version is not None and meta.ruleset_version != ""
    assert meta.timezone_used == "Europe/Paris"
    assert meta.engine == "simplified"
    assert meta.zodiac == "tropical"
    assert meta.frame == "geocentric"
    assert meta.ayanamsa is None


def test_metadata_sidereal_mode_reconstructed(mock_swisseph: None) -> None:
    """AC2: generate_for_user(zodiac=sidereal) → metadata zodiac=sidereal, ayanamsa propagé."""
    _cleanup()
    user_id = _create_user_with_resolved_place(
        birth_time="10:30",
        email="user_sidereal@example.com",
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        data = UserNatalChartService.generate_for_user(
            db=db,
            user_id=user_id,
            accurate=True,
            zodiac="sidereal",
            ayanamsa="fagan_bradley",
        )
        db.commit()

    with SessionLocal() as db:
        read_data = UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)

    meta = read_data.metadata
    assert meta.engine == "swisseph"
    assert meta.zodiac == "sidereal"
    assert meta.ayanamsa == "fagan_bradley"


def test_metadata_topocentric_mode_reconstructed(mock_swisseph: None) -> None:
    """AC3: generate_for_user(frame=topocentric) → metadata frame=topocentric."""
    _cleanup()
    user_id = _create_user_with_resolved_place(
        birth_time="10:30",
        email="user_topocentric@example.com",
    )

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        data = UserNatalChartService.generate_for_user(
            db=db,
            user_id=user_id,
            accurate=True,
            frame="topocentric",
            altitude_m=150.0,
        )
        db.commit()

    with SessionLocal() as db:
        read_data = UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)

    meta = read_data.metadata
    assert meta.engine == "swisseph"
    assert meta.frame == "topocentric"

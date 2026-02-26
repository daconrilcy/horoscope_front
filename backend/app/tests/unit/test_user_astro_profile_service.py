"""
Tests unitaires du service de profil astrologique.

Vérifie la règle null-time (AC3, AC4), le calcul du signe solaire (AC1),
et le calcul de l'ascendant (AC2).
"""

from __future__ import annotations

import pytest
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401  # ensure all SQLAlchemy models are registered
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
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_astro_profile_service import (
    UserAstroProfileService,
    UserAstroProfileServiceError,
)
from app.services.user_birth_profile_service import UserBirthProfileService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
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


def _create_user_with_profile(birth_time: str | None) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email="user@test.com", password="pass1234!")
        db.commit()
        user_id = auth.user.id

    with SessionLocal() as db:
        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time=birth_time,
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()

    return user_id


# ---------------------------------------------------------------------------
# AC3 — birth_time null → ascendant null + missing_birth_time=True
# ---------------------------------------------------------------------------


def test_astro_profile_null_birth_time_returns_null_ascendant_and_missing_flag() -> None:
    """AC3: birth_time absent => ascendant=null, missing_birth_time=true."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time=None)

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.ascendant_sign_code is None
    assert result.missing_birth_time is True


# ---------------------------------------------------------------------------
# AC4 — birth_time "00:00" => ascendant calculé + missing_birth_time=False
# ---------------------------------------------------------------------------


def test_astro_profile_explicit_midnight_returns_calculated_ascendant() -> None:
    """AC4: birth_time '00:00' => ascendant non null, missing_birth_time=false."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="00:00")

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.ascendant_sign_code is not None
    assert result.missing_birth_time is False


# ---------------------------------------------------------------------------
# AC2 — birth_time "14:30" => ascendant non null + missing_birth_time=False
# ---------------------------------------------------------------------------


def test_astro_profile_with_valid_birth_time_returns_ascendant() -> None:
    """AC2: birth_time valide => ascendant non null, missing_birth_time=false."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="14:30")

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.ascendant_sign_code is not None
    assert result.missing_birth_time is False


# ---------------------------------------------------------------------------
# AC1 — sun_sign_code calculé depuis birth_date
# ---------------------------------------------------------------------------


def test_astro_profile_sun_sign_present_regardless_of_birth_time() -> None:
    """AC1: sun_sign_code calculé même si birth_time absent."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time=None)

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.sun_sign_code is not None


def test_astro_profile_works_without_reference_seed_data() -> None:
    """Astro profile reste calculable même sans seed reference_data local."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="14:30")

    with SessionLocal() as db:
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.sun_sign_code in {
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
    assert result.ascendant_sign_code in {
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
    assert result.missing_birth_time is False


def test_astro_profile_sun_sign_consistent_for_fixed_reference_dates() -> None:
    """AC1: signe solaire dérivé du moteur natal (Sun planet) pour date connue."""
    _cleanup_tables()
    with SessionLocal() as db:
        auth = AuthService.register(db, email="sun-date@test.com", password="pass1234!")
        db.commit()
        user_id = auth.user.id

    with SessionLocal() as db:
        payload = BirthInput(
            birth_date="1973-04-24",
            birth_time="11:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()

    with SessionLocal() as db:
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.sun_sign_code == "taurus"


def test_astro_profile_sun_sign_boundaries() -> None:
    """Le signe solaire est toujours un code zodiacal valide."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="14:30")

    with SessionLocal() as db:
        result = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result.sun_sign_code in {
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


def test_compute_ascendant_deterministic_for_same_inputs() -> None:
    """L'ascendant dérivé du moteur natal est déterministe."""
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="14:30")

    with SessionLocal() as db:
        result1 = UserAstroProfileService.get_for_user(db, user_id=user_id)
        result2 = UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert result1.ascendant_sign_code == result2.ascendant_sign_code


def test_astro_profile_ascendant_matches_house_1_cusp_sign() -> None:
    _cleanup_tables()
    user_id = _create_user_with_profile(birth_time="14:30")

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        profile = UserBirthProfileService.get_for_user(db, user_id)
        natal = NatalCalculationService.calculate(
            db,
            birth_input=BirthInput(
                birth_date=profile.birth_date,
                birth_time=profile.birth_time,
                birth_place=profile.birth_place,
                birth_timezone=profile.birth_timezone,
            ),
        )
        expected_sign = None
        for house in natal.houses:
            if house.number == 1:
                sign_index = int((house.cusp_longitude % 360.0) // 30.0)
                expected_sign = (
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
                )[sign_index]
                break
        result = UserAstroProfileService.get_for_user(db, user_id)

    assert result.ascendant_sign_code == expected_sign


# ---------------------------------------------------------------------------
# AC3 vs AC4 distinction: null vs "00:00"
# ---------------------------------------------------------------------------


def test_null_and_zero_birth_time_produce_different_missing_flag() -> None:
    """AC3 vs AC4: null et '00:00' produisent des comportements différents."""
    _cleanup_tables()

    user_null = _create_user_with_profile(birth_time=None)

    # Second user with "00:00"
    with SessionLocal() as db:
        auth = AuthService.register(db, email="user2@test.com", password="pass1234!")
        db.commit()
        user_zero_id = auth.user.id

    with SessionLocal() as db:
        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time="00:00",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        UserBirthProfileService.upsert_for_user(db, user_id=user_zero_id, payload=payload)
        db.commit()

    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result_null = UserAstroProfileService.get_for_user(db, user_id=user_null)
        result_zero = UserAstroProfileService.get_for_user(db, user_id=user_zero_id)

    assert result_null.missing_birth_time is True
    assert result_null.ascendant_sign_code is None
    assert result_zero.missing_birth_time is False
    assert result_zero.ascendant_sign_code is not None


# ---------------------------------------------------------------------------
# Erreur — profil introuvable
# ---------------------------------------------------------------------------


def test_astro_profile_raises_when_birth_profile_missing() -> None:
    """Lève UserAstroProfileServiceError si le profil natal est absent."""
    _cleanup_tables()

    with SessionLocal() as db:
        auth = AuthService.register(db, email="noprofile@test.com", password="pass1234!")
        db.commit()
        user_id = auth.user.id

    with SessionLocal() as db:
        with pytest.raises(UserAstroProfileServiceError) as exc_info:
            UserAstroProfileService.get_for_user(db, user_id=user_id)

    assert exc_info.value.code == "birth_profile_not_found"

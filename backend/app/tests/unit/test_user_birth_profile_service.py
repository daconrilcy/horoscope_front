import pytest
from pydantic import ValidationError
from sqlalchemy import delete

from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.base import Base
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user() -> int:
    with SessionLocal() as db:
        auth = AuthService.register(db, email="user@example.com", password="strong-pass-123")
        db.commit()
        return auth.user.id


def test_upsert_and_get_user_birth_profile() -> None:
    _cleanup_tables()
    user_id = _create_user()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )

    with SessionLocal() as db:
        upserted = UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()
        fetched = UserBirthProfileService.get_for_user(db, user_id=user_id)

    assert upserted.birth_place == "Paris"
    assert fetched.birth_date == "1990-06-15"
    assert fetched.birth_timezone == "Europe/Paris"


def test_get_birth_profile_not_found() -> None:
    _cleanup_tables()
    user_id = _create_user()
    with SessionLocal() as db:
        with pytest.raises(UserBirthProfileServiceError) as error:
            UserBirthProfileService.get_for_user(db, user_id=user_id)
    assert error.value.code == "birth_profile_not_found"


def test_upsert_rejects_invalid_timezone() -> None:
    _cleanup_tables()
    user_id = _create_user()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Mars/Olympus",
    )

    with SessionLocal() as db:
        with pytest.raises(BirthPreparationError) as error:
            UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
    assert error.value.code == "invalid_timezone"


def test_upsert_rejects_invalid_birth_input_shape() -> None:
    with pytest.raises(ValidationError):
        BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place=" ",
            birth_timezone="Europe/Paris",
        )


def test_upsert_birth_profile_with_place_resolved_id() -> None:
    _cleanup_tables()
    user_id = _create_user()

    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=12345,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        db.add(place)
        db.flush()
        place_id = place.id

        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
            place_resolved_id=place_id,
        )

        upserted = UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()
        fetched = UserBirthProfileService.get_for_user(db, user_id=user_id)

    assert upserted.birth_place_resolved_id == place_id
    assert fetched.birth_place_resolved_id == place_id


def test_resolve_coordinates_prioritizes_place_resolved_over_legacy_coords() -> None:
    _cleanup_tables()
    user_id = _create_user()

    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=54321,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        db.add(place)
        db.flush()

        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
            # Legacy coords intentionally conflicting with resolved place.
            birth_lat=40.7128,
            birth_lon=-74.0060,
            place_resolved_id=place.id,
        )
        UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()

        profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
        resolved = UserBirthProfileService.resolve_coordinates(db, profile)

    assert resolved.birth_place_resolved_id == place.id
    assert resolved.resolved_from_place is True
    assert resolved.birth_lat == pytest.approx(48.8566)
    assert resolved.birth_lon == pytest.approx(2.3522)


def test_resolve_coordinates_falls_back_to_legacy_without_place_resolved_id() -> None:
    _cleanup_tables()
    user_id = _create_user()

    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=40.7128,
        birth_lon=-74.0060,
    )

    with SessionLocal() as db:
        UserBirthProfileService.upsert_for_user(db, user_id=user_id, payload=payload)
        db.commit()
        profile = UserBirthProfileService.get_for_user(db, user_id=user_id)
        resolved = UserBirthProfileService.resolve_coordinates(db, profile)

    assert resolved.birth_place_resolved_id is None
    assert resolved.resolved_from_place is False
    assert resolved.birth_lat == pytest.approx(40.7128)
    assert resolved.birth_lon == pytest.approx(-74.0060)

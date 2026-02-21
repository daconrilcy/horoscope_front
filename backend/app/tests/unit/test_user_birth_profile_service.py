import pytest
from pydantic import ValidationError
from sqlalchemy import delete

from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.base import Base
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

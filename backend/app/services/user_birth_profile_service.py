from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.astrology.natal_preparation import BirthInput, prepare_birth_data
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.infra.db.repositories.user_repository import UserRepository


class UserBirthProfileServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class UserBirthProfileData(BaseModel):
    birth_date: str
    birth_time: str
    birth_place: str
    birth_timezone: str


class UserBirthProfileService:
    @staticmethod
    def get_for_user(db: Session, user_id: int) -> UserBirthProfileData:
        model = UserBirthProfileRepository(db).get_by_user_id(user_id)
        if model is None:
            raise UserBirthProfileServiceError(
                code="birth_profile_not_found",
                message="birth profile not found",
                details={"user_id": str(user_id)},
            )
        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_timezone=model.birth_timezone,
        )

    @staticmethod
    def upsert_for_user(db: Session, user_id: int, payload: BirthInput) -> UserBirthProfileData:
        if UserRepository(db).get_by_id(user_id) is None:
            raise UserBirthProfileServiceError(
                code="user_not_found",
                message="user not found",
                details={"user_id": str(user_id)},
            )

        # Reuse existing preparation for deterministic birth-data validation.
        prepare_birth_data(payload)
        model = UserBirthProfileRepository(db).upsert(
            user_id=user_id,
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
            birth_timezone=payload.birth_timezone,
        )
        return UserBirthProfileData(
            birth_date=model.birth_date.isoformat(),
            birth_time=model.birth_time,
            birth_place=model.birth_place,
            birth_timezone=model.birth_timezone,
        )

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.user_birth_profile import UserBirthProfileModel


class UserBirthProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: int) -> UserBirthProfileModel | None:
        return self.db.scalar(
            select(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user_id)
        )

    def upsert(
        self,
        user_id: int,
        birth_date: date,
        birth_time: str | None,
        birth_place: str,
        birth_timezone: str,
        birth_city: str | None = None,
        birth_country: str | None = None,
        birth_lat: float | None = None,
        birth_lon: float | None = None,
        birth_place_resolved_id: int | None = None,
        geolocation_consent: bool = False,
        current_city: str | None = None,
        current_country: str | None = None,
        current_lat: float | None = None,
        current_lon: float | None = None,
        current_location_display: str | None = None,
        current_timezone: str | None = None,
    ) -> UserBirthProfileModel:
        model = self.get_by_user_id(user_id)
        if model is None:
            model = UserBirthProfileModel(
                user_id=user_id,
                birth_date=birth_date,
                birth_time=birth_time,
                birth_place=birth_place,
                birth_timezone=birth_timezone,
                birth_city=birth_city,
                birth_country=birth_country,
                birth_lat=birth_lat,
                birth_lon=birth_lon,
                birth_place_resolved_id=birth_place_resolved_id,
                geolocation_consent=geolocation_consent,
                current_city=current_city,
                current_country=current_country,
                current_lat=current_lat,
                current_lon=current_lon,
                current_location_display=current_location_display,
                current_timezone=current_timezone,
            )
            self.db.add(model)
            return model

        model.birth_date = birth_date
        model.birth_time = birth_time
        model.birth_place = birth_place
        model.birth_timezone = birth_timezone
        model.birth_city = birth_city
        model.birth_country = birth_country
        model.birth_lat = birth_lat
        model.birth_lon = birth_lon
        model.birth_place_resolved_id = birth_place_resolved_id
        model.geolocation_consent = geolocation_consent
        model.current_city = current_city
        model.current_country = current_country
        model.current_lat = current_lat
        model.current_lon = current_lon
        model.current_location_display = current_location_display
        model.current_timezone = current_timezone
        self.db.flush()
        return model

    def count_users_with_same_profile(
        self,
        birth_date: date,
        birth_time: str | None,
        birth_place: str,
        birth_timezone: str,
    ) -> int:
        return int(
            self.db.scalar(
                select(func.count(UserBirthProfileModel.id)).where(
                    UserBirthProfileModel.birth_date == birth_date,
                    UserBirthProfileModel.birth_time == birth_time,
                    UserBirthProfileModel.birth_place == birth_place,
                    UserBirthProfileModel.birth_timezone == birth_timezone,
                )
            )
            or 0
        )

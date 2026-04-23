from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.datetime_provider import utc_now
from app.infra.db.base import Base


class UserBirthProfileModel(Base):
    __tablename__ = "user_birth_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[str | None] = mapped_column(String(8), nullable=True)
    birth_place: Mapped[str] = mapped_column(String(255))
    birth_timezone: Mapped[str] = mapped_column(String(64))
    birth_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_place_resolved_id: Mapped[int | None] = mapped_column(
        ForeignKey("geo_place_resolved.id"),
        nullable=True,
        index=True,
    )
    geolocation_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_location_display: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

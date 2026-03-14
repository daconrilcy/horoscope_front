from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid4())


class ConsultationThirdPartyProfileModel(Base):
    __tablename__ = "consultation_third_party_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=generate_uuid
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    nickname: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[str | None] = mapped_column(String(8), nullable=True)
    birth_time_known: Mapped[bool] = mapped_column(Boolean, default=True)
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

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class ConsultationThirdPartyUsageModel(Base):
    __tablename__ = "consultation_third_party_usages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    third_party_profile_id: Mapped[int] = mapped_column(
        ForeignKey("consultation_third_party_profiles.id"), index=True
    )
    consultation_id: Mapped[str] = mapped_column(
        String(100), index=True
    )  # External ID from consultation generate
    consultation_type: Mapped[str] = mapped_column(String(50))
    context_summary: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

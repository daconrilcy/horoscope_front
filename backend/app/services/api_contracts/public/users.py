"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.user_profile.birth_profile_service import (
    UserBirthProfileData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class UserBirthProfileApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: UserBirthProfileData
    meta: ResponseMeta


class UserBirthProfileWithAstroData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    birth_date: str | None
    birth_year: int | None = None
    birth_month: int | None = None
    birth_day: int | None = None
    birth_date_precision: str = "full"
    birth_time: str | None
    birth_place: str
    birth_place_text: str
    birth_timezone: str
    birth_city: str | None = None
    birth_country: str | None = None
    birth_lat: float | None = None
    birth_lon: float | None = None
    birth_place_resolved_id: int | None = None
    birth_place_resolved: dict[str, Any] | None = None
    geolocation_consent: bool = False
    current_city: str | None = None
    current_country: str | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    current_location_display: str | None = None
    current_timezone: str | None = None
    astro_profile: dict[str, Any] | None = None


class UserBirthProfileWithAstroApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: UserBirthProfileWithAstroData
    meta: ResponseMeta


class UserSettingsData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    default_language_code: str | None = None
    detected_locale: str | None = None
    detected_country_code: str | None = None
    detected_timezone: str | None = None


class UserSettingsApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: UserSettingsData
    meta: ResponseMeta


class UserSettingsPatchRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    default_language_code: str | None = Field(default=None, max_length=16)
    detected_locale: str | None = Field(default=None, max_length=64)
    detected_country_code: str | None = Field(default=None, max_length=2)
    detected_timezone: str | None = Field(default=None, max_length=64)

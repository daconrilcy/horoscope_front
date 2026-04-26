"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035


import logging
from threading import Lock
from time import monotonic
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationData,
)
from app.services.user_profile.astro_profile_service import (
    UserAstroProfileData,
)
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileData,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartConsistencyData,
    UserNatalChartGenerationData,
    UserNatalChartReadData,
)

router = APIRouter(prefix="/v1/users", tags=["users"])
logger = logging.getLogger(__name__)
_INCONSISTENT_LOG_WINDOW_SECONDS = 60.0
_INCONSISTENT_LOG_ALWAYS_PER_WINDOW = 10
_INCONSISTENT_LOG_SAMPLING_RATIO = 0.01
_inconsistent_log_sampling_lock = Lock()
_inconsistent_log_sampling_state = {"window_start": monotonic(), "count": 0}


class ResponseMeta(BaseModel):
    request_id: str


class UserBirthProfileApiResponse(BaseModel):
    data: UserBirthProfileData
    meta: ResponseMeta


class UserBirthProfileWithAstroData(BaseModel):
    birth_date: str
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
    astro_profile: UserAstroProfileData | None = None


class UserBirthProfileWithAstroApiResponse(BaseModel):
    data: UserBirthProfileWithAstroData
    meta: ResponseMeta


class NatalChartGenerateRequest(BaseModel):
    reference_version: str | None = None
    accurate: bool = False
    zodiac: str | None = None
    ayanamsa: str | None = None
    frame: str | None = None
    house_system: str | None = None
    altitude_m: float | None = None


class UserNatalChartApiResponse(BaseModel):
    data: UserNatalChartGenerationData
    meta: ResponseMeta


class UserNatalChartReadApiResponse(BaseModel):
    data: UserNatalChartReadData
    meta: ResponseMeta


class UserNatalChartLatestData(UserNatalChartReadData):
    interpretation: NatalInterpretationData | None = None
    astro_profile: UserAstroProfileData | None = None


class UserNatalChartLatestApiResponse(BaseModel):
    data: UserNatalChartLatestData
    meta: ResponseMeta


class UserNatalChartConsistencyApiResponse(BaseModel):
    data: UserNatalChartConsistencyData
    meta: ResponseMeta


class NatalInterpretationApiResponse(BaseModel):
    data: NatalInterpretationData
    meta: ResponseMeta


class UserSettingsData(BaseModel):
    astrologer_profile: str
    default_astrologer_id: str | None = None


class UserSettingsApiResponse(BaseModel):
    data: UserSettingsData
    meta: ResponseMeta


class UserSettingsPatchRequest(BaseModel):
    astrologer_profile: str | None = None
    default_astrologer_id: str | None = None

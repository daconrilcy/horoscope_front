"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import asyncio
import logging
import random
from threading import Lock
from time import monotonic
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.llm_generation.natal.interpretation_service import (
    NatalInterpretationData,
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.user_profile.astro_profile_service import (
    UserAstroProfileData,
    UserAstroProfileService,
    UserAstroProfileServiceError,
)
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileData,
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartConsistencyData,
    UserNatalChartGenerationData,
    UserNatalChartReadData,
    UserNatalChartService,
    UserNatalChartServiceError,
)

VALID_ASTROLOGER_PROFILES = {"standard", "vedique", "humaniste", "karmique", "psychologique"}
router = APIRouter(prefix="/v1/users", tags=["users"])
logger = logging.getLogger(__name__)
_INCONSISTENT_LOG_WINDOW_SECONDS = 60.0
_INCONSISTENT_LOG_ALWAYS_PER_WINDOW = 10
_INCONSISTENT_LOG_SAMPLING_RATIO = 0.01
_inconsistent_log_sampling_lock = Lock()
_inconsistent_log_sampling_state = {"window_start": monotonic(), "count": 0}


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


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

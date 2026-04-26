"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
from datetime import datetime
from typing import Any, Literal
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_ops_user
from app.api.v1.routers.public.predictions import (
    _extract_llm_narrative_payload,
    _raise_daily_prediction_service_error,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.user_repository import UserRepository
from app.infra.db.session import get_db_session
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.public_projection import PublicPredictionAssembler
from app.services.entitlement.horoscope_daily_entitlement_gate import (
    HoroscopeDailyAccessDeniedError,
    HoroscopeDailyEntitlementGate,
)
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatGuidanceService,
    ChatGuidanceServiceError,
)
from app.services.llm_generation.guidance.guidance_service import (
    GuidanceService,
    GuidanceServiceError,
)
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.qa_seed_service import (
    LLM_QA_TEST_USER_EMAIL,
    LlmQaSeedResult,
    LlmQaSeedService,
)
from app.services.prediction import DailyPredictionService
from app.services.prediction.types import ComputeMode, DailyPredictionServiceError
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartService,
    UserNatalChartServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/internal/llm/qa", tags=["internal-llm-qa"])


class ResponseMeta(BaseModel):
    request_id: str
    target_user_email: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class SeedUserResponse(BaseModel):
    user_id: int
    email: str
    birth_place_resolved_id: int
    birth_timezone: str
    chart_id: str
    chart_reused: bool


class GuidanceQaRequest(BaseModel):
    period: Literal["daily", "weekly"] = "daily"
    target_email: str | None = None
    conversation_id: int | None = None


class ChatQaRequest(BaseModel):
    message: str = Field(min_length=1)
    target_email: str | None = None
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class NatalQaRequest(BaseModel):
    target_email: str | None = None
    use_case_level: Literal["short", "complete"] = "complete"
    locale: str = "fr"
    question: str | None = None
    persona_id: str | None = None
    force_refresh: bool = False
    module: str | None = None


class DailyQaRequest(BaseModel):
    target_email: str | None = None
    date: str | None = None

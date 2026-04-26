"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import get_optional_authenticated_user as get_current_user_optional
from app.core.request_id import resolve_request_id
from app.infra.db.models import (
    AstrologerProfileModel,
    AstrologerReviewModel,
    ChatConversationModel,
    UserNatalInterpretationModel,
)
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.session import get_db_session

router = APIRouter(prefix="/v1/astrologers", tags=["astrologers"])


class ResponseMeta(BaseModel):
    request_id: str


class SpecialtyDetail(BaseModel):
    title: str
    description: str


class AstrologerMetrics(BaseModel):
    total_experience_years: int = 0
    experience_years: int = 0
    consultations_count: int = 0
    average_rating: float = 0.0


class AstrologerReview(BaseModel):
    id: str
    user_name: str
    rating: int
    comment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: str


class AstrologerActionState(BaseModel):
    has_chat: bool = False
    has_natal_interpretation: bool = False
    last_chat_id: Optional[str] = None
    last_natal_interpretation_id: Optional[str] = None


class Astrologer(BaseModel):
    id: str
    name: str
    first_name: str
    last_name: str
    provider_type: str = "ia"
    avatar_url: Optional[str] = None
    specialties: List[str]
    style: str
    bio_short: str


class AstrologerProfile(Astrologer):
    bio_full: str
    gender: str
    age: Optional[int] = None
    location: Optional[str] = None
    quote: Optional[str] = None
    mission_statement: Optional[str] = None
    ideal_for: Optional[str] = None
    metrics: AstrologerMetrics
    specialties_details: List[SpecialtyDetail] = Field(default_factory=list)
    professional_background: List[str] = Field(default_factory=list)
    key_skills: List[str] = Field(default_factory=list)
    behavioral_style: List[str] = Field(default_factory=list)
    reviews: List[AstrologerReview] = Field(default_factory=list)
    review_summary: dict = Field(default_factory=dict)
    user_rating: Optional[int] = None
    user_review: Optional[AstrologerReview] = None
    action_state: AstrologerActionState = Field(default_factory=AstrologerActionState)


class AstrologerListResponse(BaseModel):
    data: List[Astrologer]
    meta: ResponseMeta


class AstrologerApiResponse(BaseModel):
    data: AstrologerProfile
    meta: ResponseMeta


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

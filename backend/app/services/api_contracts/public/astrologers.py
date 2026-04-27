"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class SpecialtyDetail(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    title: str
    description: str


class AstrologerMetrics(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    total_experience_years: int = 0
    experience_years: int = 0
    consultations_count: int = 0
    average_rating: float = 0.0


class AstrologerReview(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: str
    user_name: str
    rating: int
    comment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: str


class AstrologerActionState(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    has_chat: bool = False
    has_natal_interpretation: bool = False
    last_chat_id: Optional[str] = None
    last_natal_interpretation_id: Optional[str] = None


class Astrologer(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: List[Astrologer]
    meta: ResponseMeta


class AstrologerApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AstrologerProfile
    meta: ResponseMeta


class ReviewUpdate(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

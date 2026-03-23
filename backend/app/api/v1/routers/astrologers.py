from __future__ import annotations

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
    LlmPersonaModel,
    UserNatalInterpretationModel,
)
from app.infra.db.session import get_db_session

router = APIRouter(prefix="/v1/astrologers", tags=["astrologers"])


class ResponseMeta(BaseModel):
    request_id: str


class SpecialtyDetail(BaseModel):
    title: str
    description: str


class AstrologerMetrics(BaseModel):
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
    
    # Social proof
    reviews: List[AstrologerReview] = Field(default_factory=list)
    review_summary: dict = Field(default_factory=dict)
    user_rating: Optional[int] = None # Current user's rating
    
    # Contextual actions
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


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


@router.get("", response_model=AstrologerListResponse)
def list_astrologers(
    request: Request,
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    stmt = (
        select(AstrologerProfileModel)
        .join(LlmPersonaModel, LlmPersonaModel.id == AstrologerProfileModel.persona_id)
        .where(AstrologerProfileModel.is_public.is_(True), LlmPersonaModel.enabled.is_(True))
        .order_by(AstrologerProfileModel.sort_order, AstrologerProfileModel.display_name)
    )
    profiles = db.execute(stmt).scalars().all()

    result_data = []
    for p in profiles:
        result_data.append(
            Astrologer(
                id=str(p.persona_id),
                name=p.display_name,
                first_name=p.first_name,
                last_name=p.last_name,
                provider_type=p.provider_type,
                avatar_url=p.photo_url,
                specialties=p.specialties,
                style=p.public_style_label,
                bio_short=p.bio_short,
            )
        )

    return {"data": result_data, "meta": {"request_id": request_id}}


@router.get("/{id}", response_model=AstrologerApiResponse)
def get_astrologer(
    id: str,
    request: Request,
    db: Session = Depends(get_db_session),
    current_user: Any = Depends(get_current_user_optional),
) -> Any:
    request_id = resolve_request_id(request)

    try:
        persona_uuid = uuid.UUID(id)
    except (ValueError, TypeError):
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="astrologer_not_found",
            message=f"astrologer {id} not found",
            details={},
        )

    stmt = (
        select(AstrologerProfileModel)
        .join(LlmPersonaModel, LlmPersonaModel.id == AstrologerProfileModel.persona_id)
        .where(
            AstrologerProfileModel.persona_id == persona_uuid,
            AstrologerProfileModel.is_public.is_(True),
            LlmPersonaModel.enabled.is_(True),
        )
    )
    profile = db.execute(stmt).scalar_one_or_none()
    if not profile:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="astrologer_not_found",
            message=f"astrologer {id} not found",
            details={},
        )

    # Fetch reviews
    reviews_stmt = (
        select(AstrologerReviewModel)
        .where(AstrologerReviewModel.persona_id == persona_uuid)
        .order_by(AstrologerReviewModel.created_at.desc())
        .limit(5)
    )
    reviews_models = db.execute(reviews_stmt).scalars().all()
    
    reviews = [
        AstrologerReview(
            id=str(r.id),
            user_name="Consultant", # We don't have user names yet, anonymize
            rating=r.rating,
            comment=r.comment,
            tags=r.tags,
            created_at=r.created_at.isoformat()
        ) for r in reviews_models
    ]

    # Review summary
    stats_stmt = (
        select(func.avg(AstrologerReviewModel.rating), func.count(AstrologerReviewModel.id))
        .where(AstrologerReviewModel.persona_id == persona_uuid)
    )
    avg_rating, review_count = db.execute(stats_stmt).one()
    
    review_summary = {
        "average_rating": float(avg_rating or 0),
        "review_count": review_count,
    }

    # User state
    user_rating = None
    action_state = AstrologerActionState()
    
    if current_user:
        # User rating
        user_rev_stmt = select(AstrologerReviewModel.rating).where(
            AstrologerReviewModel.persona_id == persona_uuid,
            AstrologerReviewModel.user_id == current_user.id
        )
        user_rating = db.execute(user_rev_stmt).scalar_one_or_none()
        
        # Chat state
        chat_stmt = (
            select(ChatConversationModel.id)
            .where(
                ChatConversationModel.persona_id == persona_uuid,
                ChatConversationModel.user_id == current_user.id
            )
            .order_by(ChatConversationModel.updated_at.desc())
            .limit(1)
        )
        action_state.last_chat_id = db.execute(chat_stmt).scalar_one_or_none()
        action_state.has_chat = action_state.last_chat_id is not None
        
        # Natal state
        natal_stmt = (
            select(UserNatalInterpretationModel.id)
            .where(
                UserNatalInterpretationModel.persona_id == persona_uuid,
                UserNatalInterpretationModel.user_id == current_user.id
            )
            .order_by(UserNatalInterpretationModel.created_at.desc())
            .limit(1)
        )
        action_state.last_natal_interpretation_id = db.execute(natal_stmt).scalar_one_or_none()
        action_state.has_natal_interpretation = (
            action_state.last_natal_interpretation_id is not None
        )

    return {
        "data": AstrologerProfile(
            id=str(profile.persona_id),
            name=profile.display_name,
            first_name=profile.first_name,
            last_name=profile.last_name,
            provider_type=profile.provider_type,
            avatar_url=profile.photo_url,
            specialties=profile.specialties,
            style=profile.public_style_label,
            bio_short=profile.bio_short,
            bio_full=profile.bio_long,
            gender=profile.gender,
            age=profile.age,
            location=profile.location,
            quote=profile.quote,
            mission_statement=profile.mission_statement,
            ideal_for=profile.ideal_for,
            metrics=(
                AstrologerMetrics(**profile.metrics) 
                if profile.metrics else AstrologerMetrics()
            ),
            specialties_details=[
                SpecialtyDetail(**sd) 
                for sd in profile.specialties_details
            ],
            professional_background=profile.professional_background,
            key_skills=profile.key_skills,
            behavioral_style=profile.behavioral_style,
            reviews=reviews,
            review_summary=review_summary,
            user_rating=user_rating,
            action_state=action_state
        ),
        "meta": {"request_id": request_id},
    }


@router.post("/{id}/reviews", response_model=dict)
def update_astrologer_review(
    id: str,
    review_data: ReviewUpdate,
    request: Request,
    db: Session = Depends(get_db_session),
    current_user: Any = Depends(get_current_user_optional),
) -> Any:
    request_id = resolve_request_id(request)
    
    if not current_user:
        return _error_response(
            status_code=401,
            request_id=request_id,
            code="unauthorized",
            message="authentication required to leave a review",
            details={},
        )

    try:
        persona_uuid = uuid.UUID(id)
    except (ValueError, TypeError):
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="astrologer_not_found",
            message=f"astrologer {id} not found",
            details={},
        )

    # Check persona exists
    persona = db.get(LlmPersonaModel, persona_uuid)
    if not persona:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="astrologer_not_found",
            message=f"astrologer {id} not found",
            details={},
        )

    # Upsert review
    stmt = select(AstrologerReviewModel).where(
        AstrologerReviewModel.persona_id == persona_uuid,
        AstrologerReviewModel.user_id == current_user.id
    )
    review = db.execute(stmt).scalar_one_or_none()
    
    if review:
        review.rating = review_data.rating
        review.comment = review_data.comment
        review.tags = review_data.tags
    else:
        review = AstrologerReviewModel(
            user_id=current_user.id,
            persona_id=persona_uuid,
            rating=review_data.rating,
            comment=review_data.comment,
            tags=review_data.tags
        )
        db.add(review)
    
    db.commit()
    
    return {"status": "ok", "meta": {"request_id": request_id}}

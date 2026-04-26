from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_optional_authenticated_user as get_current_user_optional
from app.api.v1.router_logic.public.astrologers import (
    _build_user_alias,
    _error_response,
)
from app.api.v1.schemas.routers.public.astrologers import (
    Astrologer,
    AstrologerActionState,
    AstrologerApiResponse,
    AstrologerListResponse,
    AstrologerMetrics,
    AstrologerProfile,
    AstrologerReview,
    ReviewUpdate,
    SpecialtyDetail,
)
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
        .where(
            AstrologerReviewModel.persona_id == persona_uuid,
            AstrologerReviewModel.comment.is_not(None),
            AstrologerReviewModel.comment != "",
        )
        .order_by(AstrologerReviewModel.created_at.desc())
        .limit(5)
    )
    reviews_models = db.execute(reviews_stmt).scalars().all()

    reviews = [
        AstrologerReview(
            id=str(r.id),
            user_name=r.user_alias or "membre",
            rating=r.rating,
            comment=r.comment,
            tags=r.tags,
            created_at=r.created_at.isoformat(),
        )
        for r in reviews_models
    ]

    # Review summary
    stats_stmt = select(
        func.avg(AstrologerReviewModel.rating), func.count(AstrologerReviewModel.id)
    ).where(AstrologerReviewModel.persona_id == persona_uuid)
    avg_rating, review_count = db.execute(stats_stmt).one()

    review_summary = {
        "average_rating": float(avg_rating or 0),
        "review_count": review_count,
    }

    # User state
    user_rating = None
    user_review = None
    action_state = AstrologerActionState()

    if current_user:
        # User rating
        user_rev_stmt = select(AstrologerReviewModel).where(
            AstrologerReviewModel.persona_id == persona_uuid,
            AstrologerReviewModel.user_id == current_user.id,
        )
        current_user_review = db.execute(user_rev_stmt).scalar_one_or_none()
        if current_user_review is not None:
            user_rating = current_user_review.rating
            user_review = AstrologerReview(
                id=str(current_user_review.id),
                user_name=current_user_review.user_alias or _build_user_alias(current_user.email),
                rating=current_user_review.rating,
                comment=current_user_review.comment,
                tags=current_user_review.tags,
                created_at=current_user_review.created_at.isoformat(),
            )

        # Chat state
        chat_stmt = (
            select(ChatConversationModel.id)
            .where(
                ChatConversationModel.persona_id == persona_uuid,
                ChatConversationModel.user_id == current_user.id,
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
                UserNatalInterpretationModel.user_id == current_user.id,
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
                AstrologerMetrics(**profile.metrics) if profile.metrics else AstrologerMetrics()
            ),
            specialties_details=[SpecialtyDetail(**sd) for sd in profile.specialties_details],
            professional_background=profile.professional_background,
            key_skills=profile.key_skills,
            behavioral_style=profile.behavioral_style,
            reviews=reviews,
            review_summary=review_summary,
            user_rating=user_rating,
            user_review=user_review,
            action_state=action_state,
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

    normalized_comment = (review_data.comment or "").strip() or None

    # Upsert review
    stmt = select(AstrologerReviewModel).where(
        AstrologerReviewModel.persona_id == persona_uuid,
        AstrologerReviewModel.user_id == current_user.id,
    )
    review = db.execute(stmt).scalar_one_or_none()

    if review:
        review.rating = review_data.rating
        review.comment = normalized_comment
        review.tags = review_data.tags
        review.user_alias = review.user_alias or _build_user_alias(current_user.email)
    else:
        review = AstrologerReviewModel(
            user_id=current_user.id,
            user_alias=_build_user_alias(current_user.email),
            persona_id=persona_uuid,
            rating=review_data.rating,
            comment=normalized_comment,
            tags=review_data.tags,
        )
        db.add(review)

    db.commit()

    return {"status": "ok", "meta": {"request_id": request_id}}

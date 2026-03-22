from __future__ import annotations

import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.request_id import resolve_request_id
from app.infra.db.models import AstrologerProfileModel, LlmPersonaModel
from app.infra.db.session import get_db_session

router = APIRouter(prefix="/v1/astrologers", tags=["astrologers"])


class ResponseMeta(BaseModel):
    request_id: str


class Astrologer(BaseModel):
    id: str
    name: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    specialties: List[str]
    style: str
    bio_short: str


class AstrologerProfile(Astrologer):
    bio_full: str
    gender: str


class AstrologerListResponse(BaseModel):
    data: List[Astrologer]
    meta: ResponseMeta


class AstrologerApiResponse(BaseModel):
    data: AstrologerProfile
    meta: ResponseMeta


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

    return {
        "data": AstrologerProfile(
            id=str(profile.persona_id),
            name=profile.display_name,
            first_name=profile.first_name,
            last_name=profile.last_name,
            avatar_url=profile.photo_url,
            specialties=profile.specialties,
            style=profile.public_style_label,
            bio_short=profile.bio_short,
            bio_full=profile.bio_long,
            gender=profile.gender,
        ),
        "meta": {"request_id": request_id},
    }

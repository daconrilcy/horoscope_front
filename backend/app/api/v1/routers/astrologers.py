from __future__ import annotations

import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.request_id import resolve_request_id
from app.infra.db.models.llm_persona import LlmPersonaModel
from app.infra.db.session import get_db_session

router = APIRouter(prefix="/v1/astrologers", tags=["astrologers"])


class ResponseMeta(BaseModel):
    request_id: str


class Astrologer(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str] = None
    specialties: List[str]
    style: str
    bio_short: str


class AstrologerProfile(Astrologer):
    bio_full: str
    languages: List[str]
    experience_years: int


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
        select(LlmPersonaModel)
        .where(LlmPersonaModel.enabled == True)
        .order_by(LlmPersonaModel.name)
    )
    personas = db.execute(stmt).scalars().all()

    result_data = []
    for p in personas:
        result_data.append(
            Astrologer(
                id=str(p.id),
                name=p.name,
                avatar_url=None,  # Personas don't have avatar_url in DB yet
                specialties=p.allowed_topics or [],
                style=p.tone,
                bio_short=p.description,
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

    persona = db.get(LlmPersonaModel, persona_uuid)
    if not persona or not persona.enabled:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="astrologer_not_found",
            message=f"astrologer {id} not found",
            details={},
        )

    return {
        "data": AstrologerProfile(
            id=str(persona.id),
            name=persona.name,
            avatar_url=None,
            specialties=persona.allowed_topics or [],
            style=persona.tone,
            bio_short=persona.description,
            bio_full=persona.description,  # Same as bio_short for now
            languages=["Français"],
            experience_years=10,
        ),
        "meta": {"request_id": request_id},
    }

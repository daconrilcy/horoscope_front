from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import build_error_response
from app.api.v1.schemas.routers.public.help import (
    CreateTicketRequest,
    HelpCategoriesApiResponse,
    HelpCategoryData,
    TicketApiResponse,
    TicketResponseData,
    TicketsListApiResponse,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
from app.infra.db.session import get_db_session
from app.services.ops.incident_service import (
    IncidentService,
    SupportIncidentCreatePayload,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/help", tags=["help"])


@router.get("/categories", response_model=HelpCategoriesApiResponse)
async def get_help_categories(
    request: Request,
    lang: str = Query("fr"),
    db: Session = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        check_rate_limit(key=f"help_categories:{user.id}", limit=60, window_seconds=60)
    except RateLimitError as e:
        return build_error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            request_id=request_id,
            code="rate_limit_exceeded",
            message="Rate limit exceeded",
            details=e.details,
        )

    stmt = (
        select(SupportTicketCategoryModel)
        .where(SupportTicketCategoryModel.is_active)
        .order_by(SupportTicketCategoryModel.display_order)
    )
    categories = db.scalars(stmt).all()

    def get_label(cat: SupportTicketCategoryModel) -> str:
        if lang == "en":
            return cat.label_en
        if lang == "es":
            return cat.label_es
        return cat.label_fr

    def get_description(cat: SupportTicketCategoryModel) -> str | None:
        if lang == "en":
            return cat.description_en
        if lang == "es":
            return cat.description_es
        return cat.description_fr

    result = [
        HelpCategoryData(
            code=cat.code,
            label=get_label(cat),
            description=get_description(cat),
        )
        for cat in categories
    ]

    return {
        "data": {"categories": result},
        "meta": {"request_id": request_id},
    }


@router.post("/tickets", response_model=TicketApiResponse, status_code=status.HTTP_201_CREATED)
async def create_help_ticket(
    request: Request,
    payload: CreateTicketRequest = Body(...),
    db: Session = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        check_rate_limit(key=f"help_create_ticket:{user.id}", limit=5, window_seconds=3600)
    except RateLimitError as e:
        return build_error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            request_id=request_id,
            code="rate_limit_exceeded",
            message="Rate limit exceeded (max 5 tickets per hour)",
            details=e.details,
        )

    # Validate category
    cat_stmt = select(SupportTicketCategoryModel).where(
        SupportTicketCategoryModel.code == payload.category_code,
        SupportTicketCategoryModel.is_active,
    )
    category = db.scalar(cat_stmt)
    if not category:
        return build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            request_id=request_id,
            code="ticket_invalid_category",
            message="invalid or inactive category",
            details={"category_code": payload.category_code},
        )

    if not payload.subject.strip():
        return build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            request_id=request_id,
            code="ticket_invalid_subject",
            message="subject is required",
            details={},
        )

    if not payload.description.strip():
        return build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            request_id=request_id,
            code="ticket_invalid_description",
            message="description is required",
            details={},
        )

    incident_payload = SupportIncidentCreatePayload(
        user_id=user.id,
        category=payload.category_code,
        title=payload.subject,
        description=payload.description,
        priority="low",
    )

    try:
        incident = IncidentService.create_incident(
            db,
            payload=incident_payload,
            actor_user_id=user.id,
            request_id=request_id,
            initial_status="pending",
        )
        db.commit()

        return {
            "data": TicketResponseData(
                ticket_id=incident.incident_id,
                category_code=incident.category,
                subject=incident.title,
                description=incident.description,
                support_response=incident.support_response,
                status=incident.status,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
                resolved_at=incident.resolved_at,
            ),
            "meta": {"request_id": request_id},
        }
    except Exception as e:
        logger.exception("failed to create help ticket request_id=%s", request_id)
        return build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
            code="internal_error",
            message="failed to create ticket",
            details={"error": str(e)},
        )


@router.get("/tickets", response_model=TicketsListApiResponse)
async def list_help_tickets(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        check_rate_limit(key=f"help_list_tickets:{user.id}", limit=30, window_seconds=60)
    except RateLimitError as e:
        return build_error_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            request_id=request_id,
            code="rate_limit_exceeded",
            message="Rate limit exceeded",
            details=e.details,
        )

    stmt = (
        select(SupportIncidentModel)
        .where(SupportIncidentModel.user_id == user.id)
        .order_by(desc(SupportIncidentModel.created_at))
        .limit(limit)
        .offset(offset)
    )
    tickets = db.scalars(stmt).all()

    total_stmt = select(func.count(SupportIncidentModel.id)).where(
        SupportIncidentModel.user_id == user.id
    )
    total = db.scalar(total_stmt) or 0

    result = [
        TicketResponseData(
            ticket_id=t.id,
            category_code=t.category,
            subject=t.title,
            description=t.description,
            support_response=t.support_response,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at,
            resolved_at=t.resolved_at,
        )
        for t in tickets
    ]

    return {
        "data": {
            "tickets": result,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        "meta": {"request_id": request_id},
    }

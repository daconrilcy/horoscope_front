"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Body, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
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


class ResponseMeta(BaseModel):
    request_id: str


class HelpCategoryData(BaseModel):
    code: str
    label: str
    description: str | None


class HelpCategoriesResponseData(BaseModel):
    categories: list[HelpCategoryData]


class HelpCategoriesApiResponse(BaseModel):
    data: HelpCategoriesResponseData
    meta: ResponseMeta


class CreateTicketRequest(BaseModel):
    category_code: str
    subject: str = Field(..., max_length=160)
    description: str


class TicketResponseData(BaseModel):
    ticket_id: int
    category_code: str
    subject: str
    description: str
    support_response: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class TicketApiResponse(BaseModel):
    data: TicketResponseData
    meta: ResponseMeta


class TicketsListData(BaseModel):
    tickets: list[TicketResponseData]
    total: int
    limit: int
    offset: int


class TicketsListApiResponse(BaseModel):
    data: TicketsListData
    meta: ResponseMeta

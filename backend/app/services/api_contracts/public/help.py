"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class HelpCategoryData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    code: str
    label: str
    description: str | None


class HelpCategoriesResponseData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    categories: list[HelpCategoryData]


class HelpCategoriesApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: HelpCategoriesResponseData
    meta: ResponseMeta


class CreateTicketRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    category_code: str
    subject: str = Field(..., max_length=160)
    description: str


class TicketResponseData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: TicketResponseData
    meta: ResponseMeta


class TicketsListData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    tickets: list[TicketResponseData]
    total: int
    limit: int
    offset: int


class TicketsListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: TicketsListData
    meta: ResponseMeta

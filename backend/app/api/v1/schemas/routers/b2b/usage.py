"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.b2b.canonical_usage_service import (
    B2BCanonicalUsageSummary,
)

router = APIRouter(prefix="/v1/b2b/usage", tags=["b2b-usage"])


class ResponseMeta(BaseModel):
    request_id: str


class B2BUsageSummaryApiResponse(BaseModel):
    data: B2BCanonicalUsageSummary
    meta: ResponseMeta

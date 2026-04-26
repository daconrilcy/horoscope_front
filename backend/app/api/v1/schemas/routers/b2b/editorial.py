"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.b2b.editorial_service import (
    B2BEditorialConfigData,
)

router = APIRouter(prefix="/v1/b2b/editorial", tags=["b2b-editorial"])


class ResponseMeta(BaseModel):
    request_id: str


class B2BEditorialConfigApiResponse(BaseModel):
    data: B2BEditorialConfigData
    meta: ResponseMeta

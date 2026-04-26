"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.domain.llm.configuration.admin_models import (
    DraftPublishResponse,
    PromptAssemblyConfig,
    PromptAssemblyPreview,
)

router = APIRouter(prefix="/v1/admin/llm/assembly", tags=["admin-llm-assembly"])


class ResponseMeta(BaseModel):
    request_id: str
    warnings: List[str] = Field(default_factory=list)


class AssemblyConfigListResponse(BaseModel):
    data: List[PromptAssemblyConfig]
    meta: ResponseMeta


class AssemblyConfigResponse(BaseModel):
    data: PromptAssemblyConfig
    meta: ResponseMeta


class AssemblyPreviewResponse(BaseModel):
    data: PromptAssemblyPreview
    meta: ResponseMeta


class AssemblyPublishApiResponse(BaseModel):
    data: DraftPublishResponse
    meta: ResponseMeta

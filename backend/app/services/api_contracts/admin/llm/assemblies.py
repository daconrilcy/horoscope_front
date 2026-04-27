"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.domain.llm.configuration.admin_models import (
    DraftPublishResponse,
    PromptAssemblyConfig,
    PromptAssemblyPreview,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str
    warnings: List[str] = Field(default_factory=list)


class AssemblyConfigListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: List[PromptAssemblyConfig]
    meta: ResponseMeta


class AssemblyConfigResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PromptAssemblyConfig
    meta: ResponseMeta


class AssemblyPreviewResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: PromptAssemblyPreview
    meta: ResponseMeta


class AssemblyPublishApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: DraftPublishResponse
    meta: ResponseMeta

"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.domain.llm.configuration.admin_models import (
    DraftPublishResponse,
    PromptAssemblyConfig,
    PromptAssemblyPreview,
)
from app.domain.llm.configuration.assembly_admin_service import AssemblyAdminService
from app.domain.llm.configuration.coherence import CoherenceError
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

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

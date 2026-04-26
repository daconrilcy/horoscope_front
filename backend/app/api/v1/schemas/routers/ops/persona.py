"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

from typing import Any, Callable
from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import (
    AuthenticatedUser,
    require_ops_user,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.llm_generation.guidance.persona_config_service import (
    PersonaConfigData,
    PersonaConfigService,
    PersonaConfigServiceError,
    PersonaConfigUpdatePayload,
    PersonaProfileCreatePayload,
    PersonaProfileListData,
    PersonaRollbackData,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError

router = APIRouter(prefix="/v1/ops/persona", tags=["ops-persona"])


class ResponseMeta(BaseModel):
    request_id: str


class PersonaConfigApiResponse(BaseModel):
    data: PersonaConfigData
    meta: ResponseMeta


class PersonaRollbackApiResponse(BaseModel):
    data: PersonaRollbackData
    meta: ResponseMeta


class PersonaProfileListApiResponse(BaseModel):
    data: PersonaProfileListData
    meta: ResponseMeta

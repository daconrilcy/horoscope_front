"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.constants import BLOCKED_CATEGORIES, LOCALE_PATTERN

import re
import uuid
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.v1.schemas.routers.admin.llm.error_codes import AdminLlmErrorCode
from app.core.request_id import resolve_request_id
from app.core.sensitive_data import DataCategory, classify_field
from app.domain.llm.governance.feature_taxonomy import (
    is_supported_feature,
    normalize_feature,
    normalize_plan_scope,
    normalize_subfeature,
)
from app.infra.db.models.llm.llm_sample_payload import LlmSamplePayloadModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/admin/llm/sample-payloads", tags=["admin-llm"])


class ResponseMeta(BaseModel):
    request_id: str


class AdminLlmSamplePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    feature: str
    subfeature: str
    plan: str
    locale: str
    payload_json: dict[str, Any]
    description: str | None = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminLlmSamplePayloadSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    feature: str
    subfeature: str
    plan: str
    locale: str
    description: str | None = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminLlmSamplePayloadListData(BaseModel):
    items: list[AdminLlmSamplePayloadSummary]
    recommended_default_id: uuid.UUID | None = None


class AdminLlmSamplePayloadResponse(BaseModel):
    data: AdminLlmSamplePayload
    meta: ResponseMeta


class AdminLlmSamplePayloadListResponse(BaseModel):
    data: AdminLlmSamplePayloadListData
    meta: ResponseMeta


class AdminLlmSamplePayloadDeleteData(BaseModel):
    id: uuid.UUID


class AdminLlmSamplePayloadDeleteResponse(BaseModel):
    data: AdminLlmSamplePayloadDeleteData
    meta: ResponseMeta


class AdminLlmSamplePayloadCreatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    feature: str = Field(min_length=1, max_length=64)
    subfeature: str | None = Field(default=None, max_length=64)
    plan: str | None = Field(default=None, max_length=64)
    locale: str = Field(min_length=5, max_length=16)
    payload_json: dict[str, Any]
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool = False
    is_active: bool = True


class AdminLlmSamplePayloadUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    subfeature: str | None = Field(default=None, max_length=64)
    plan: str | None = Field(default=None, max_length=64)
    locale: str | None = Field(default=None, min_length=5, max_length=16)
    payload_json: dict[str, Any] | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool | None = None
    is_active: bool | None = None

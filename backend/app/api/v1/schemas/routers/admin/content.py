"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from app.api.v1.constants import (
    CALIBRATION_RULE_DESCRIPTIONS,
    DEFAULT_CONFIG_TEXTS,
    DEFAULT_EDITORIAL_TEMPLATES,
)

# ruff: noqa: F401, F811, I001, UP035
import json
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.core.datetime_provider import datetime_provider
from app.core.request_id import resolve_request_id
from app.infra.db.models.config_text import ConfigTextModel
from app.infra.db.models.editorial_template import EditorialTemplateVersionModel
from app.infra.db.models.feature_flag import FeatureFlagModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel, RulesetParameterModel
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService
from app.services.ops.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagService,
    FeatureFlagServiceError,
    FeatureFlagUpdatePayload,
)

router = APIRouter(prefix="/v1/admin/content", tags=["admin-content"])


class ResponseMeta(BaseModel):
    request_id: str


class ConfigTextData(BaseModel):
    key: str
    value: str
    category: str
    updated_at: datetime
    updated_by_user_id: int | None


class ConfigTextListResponse(BaseModel):
    data: list[ConfigTextData]
    meta: ResponseMeta


class ConfigTextResponse(BaseModel):
    data: ConfigTextData
    meta: ResponseMeta


class ConfigTextUpdatePayload(BaseModel):
    value: str


class AdminFeatureFlagData(BaseModel):
    key: str
    description: str
    enabled: bool
    target_roles: list[str]
    target_user_ids: list[int]
    updated_by_user_id: int | None
    updated_at: datetime
    scope: str


class AdminFeatureFlagListResponse(BaseModel):
    data: list[AdminFeatureFlagData]
    meta: ResponseMeta


class AdminFeatureFlagResponse(BaseModel):
    data: AdminFeatureFlagData
    meta: ResponseMeta


class EditorialTemplateSummary(BaseModel):
    template_code: str
    title: str
    active_version_id: uuid.UUID | None
    active_version_number: int | None
    published_at: datetime | None


class EditorialTemplateVersionData(BaseModel):
    id: uuid.UUID
    template_code: str
    version_number: int
    title: str
    content: str
    expected_tags: list[str]
    example_render: str | None
    status: str
    created_at: datetime
    published_at: datetime | None
    created_by_user_id: int | None


class EditorialTemplateListResponse(BaseModel):
    data: list[EditorialTemplateSummary]
    meta: ResponseMeta


class EditorialTemplateDetail(BaseModel):
    template_code: str
    active_version_id: uuid.UUID | None
    versions: list[EditorialTemplateVersionData]


class EditorialTemplateDetailResponse(BaseModel):
    data: EditorialTemplateDetail
    meta: ResponseMeta


class EditorialTemplateVersionCreatePayload(BaseModel):
    title: str
    content: str
    expected_tags: list[str] = Field(default_factory=list)
    example_render: str | None = None


class EditorialTemplateRollbackPayload(BaseModel):
    version_id: uuid.UUID


class CalibrationRuleData(BaseModel):
    rule_code: str
    value: str
    data_type: str
    description: str
    ruleset_version: str


class CalibrationRuleListResponse(BaseModel):
    data: list[CalibrationRuleData]
    meta: ResponseMeta


class CalibrationRuleResponse(BaseModel):
    data: CalibrationRuleData
    meta: ResponseMeta


class CalibrationRuleUpdatePayload(BaseModel):
    value: Any

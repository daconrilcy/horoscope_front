"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations


# ruff: noqa: F401, F811, I001, UP035
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

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

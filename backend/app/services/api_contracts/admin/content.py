"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class ConfigTextData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    value: str
    category: str
    updated_at: datetime
    updated_by_user_id: int | None


class ConfigTextListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[ConfigTextData]
    meta: ResponseMeta


class ConfigTextResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ConfigTextData
    meta: ResponseMeta


class ConfigTextUpdatePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    value: str


class AdminFeatureFlagData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    key: str
    description: str
    enabled: bool
    target_roles: list[str]
    target_user_ids: list[int]
    updated_by_user_id: int | None
    updated_at: datetime
    scope: str


class AdminFeatureFlagListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[AdminFeatureFlagData]
    meta: ResponseMeta


class AdminFeatureFlagResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminFeatureFlagData
    meta: ResponseMeta


class EditorialTemplateSummary(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    template_code: str
    title: str
    active_version_id: uuid.UUID | None
    active_version_number: int | None
    published_at: datetime | None


class EditorialTemplateVersionData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: list[EditorialTemplateSummary]
    meta: ResponseMeta


class EditorialTemplateDetail(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    template_code: str
    active_version_id: uuid.UUID | None
    versions: list[EditorialTemplateVersionData]


class EditorialTemplateDetailResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: EditorialTemplateDetail
    meta: ResponseMeta


class EditorialTemplateVersionCreatePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    title: str
    content: str
    expected_tags: list[str] = Field(default_factory=list)
    example_render: str | None = None


class EditorialTemplateRollbackPayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    version_id: uuid.UUID


class CalibrationRuleData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    rule_code: str
    value: str
    data_type: str
    description: str
    ruleset_version: str


class CalibrationRuleListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: list[CalibrationRuleData]
    meta: ResponseMeta


class CalibrationRuleResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: CalibrationRuleData
    meta: ResponseMeta


class CalibrationRuleUpdatePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    value: Any

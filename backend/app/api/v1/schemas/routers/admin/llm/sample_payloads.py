"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

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

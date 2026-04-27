"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class AdminLlmSamplePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    items: list[AdminLlmSamplePayloadSummary]
    recommended_default_id: uuid.UUID | None = None


class AdminLlmSamplePayloadResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminLlmSamplePayload
    meta: ResponseMeta


class AdminLlmSamplePayloadListResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminLlmSamplePayloadListData
    meta: ResponseMeta


class AdminLlmSamplePayloadDeleteData(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    id: uuid.UUID


class AdminLlmSamplePayloadDeleteResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: AdminLlmSamplePayloadDeleteData
    meta: ResponseMeta


class AdminLlmSamplePayloadCreatePayload(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    name: str | None = Field(default=None, min_length=1, max_length=128)
    subfeature: str | None = Field(default=None, max_length=64)
    plan: str | None = Field(default=None, max_length=64)
    locale: str | None = Field(default=None, min_length=5, max_length=16)
    payload_json: dict[str, Any] | None = None
    description: str | None = Field(default=None, max_length=2000)
    is_default: bool | None = None
    is_active: bool | None = None

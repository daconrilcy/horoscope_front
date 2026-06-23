"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


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

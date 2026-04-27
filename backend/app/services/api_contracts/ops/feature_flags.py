"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.ops.feature_flag_service import (
    FeatureFlagData,
    FeatureFlagListData,
)


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class FeatureFlagListApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: FeatureFlagListData
    meta: ResponseMeta


class FeatureFlagApiResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: FeatureFlagData
    meta: ResponseMeta

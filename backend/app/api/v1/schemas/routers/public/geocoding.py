"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

import logging
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.geocoding_service import (
    GeocodingSearchResult,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/geocoding", tags=["geocoding"])


class GeocodingResolveRequest(BaseModel):
    provider: Literal["nominatim"]
    provider_place_id: int = Field(gt=0)
    snapshot: GeocodingSearchResult | None = None


class ReverseGeocodingRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)

"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.services.geocoding_service import (
    GeocodingSearchResult,
)


class GeocodingResolveRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    provider: Literal["nominatim"]
    provider_place_id: int = Field(gt=0)
    snapshot: GeocodingSearchResult | None = None


class ReverseGeocodingRequest(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)

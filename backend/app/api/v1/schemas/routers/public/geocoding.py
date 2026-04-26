"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
import math
import re
from typing import Any, Literal
from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import (
    AuthenticatedUser,
    get_optional_authenticated_user,
    require_authenticated_user,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.repositories.geo_place_resolved_repository import (
    GeoPlaceResolvedCreateData,
    GeoPlaceResolvedRepository,
)
from app.infra.db.session import get_db_session
from app.services.geocoding_service import (
    GeocodingSearchResult,
    GeocodingService,
    GeocodingServiceError,
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

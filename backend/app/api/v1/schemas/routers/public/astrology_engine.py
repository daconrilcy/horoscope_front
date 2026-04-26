"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035
from app.api.v1.schemas.common import ErrorEnvelope, ErrorPayload

import logging
from typing import Any
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core import ephemeris
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.domain.astrology.natal_calculation import NatalCalculationError
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.session import get_db_session
from app.services.chart.result_service import (
    ChartResultAuditRecord,
    ChartResultService,
    ChartResultServiceError,
)
from app.services.natal.calculation_service import NatalCalculationService
from app.services.natal.preparation_service import NatalPreparationService

router = APIRouter(prefix="/v1/astrology-engine", tags=["astrology-engine"])
logger = logging.getLogger(__name__)
_NATAL_TECHNICAL_ERROR_CODES = frozenset(
    {
        "ephemeris_calc_failed",
        "houses_calc_failed",
    }
)


class NatalPrepareRequest(BirthInput):
    tt_enabled: bool = False


class NatalCalculateRequest(BirthInput):
    reference_version: str | None = None
    accurate: bool = False
    zodiac: str | None = None
    ayanamsa: str | None = None
    frame: str | None = None
    house_system: str | None = None
    altitude_m: float | None = None
    tt_enabled: bool = False


class NatalCompareRequest(BirthInput):
    reference_version: str | None = None


class ResponseMeta(BaseModel):
    request_id: str
    engine: str | None = None
    ephemeris_path_version: str | None = None
    ephemeris_path_hash: str | None = None
    # Terrestrial Time fields (story 22.2) — present when tt_enabled=True.
    time_scale: str = "UT"
    delta_t_sec: float | None = None
    jd_tt: float | None = None
    # Story 26.1 — Timezone traceability fields.
    # timezone_used: IANA identifier of the timezone effectively applied.
    # timezone_source: provenance — "user_provided" or "derived".
    timezone_used: str | None = None
    timezone_source: str | None = None


class BirthPrepareResponse(BaseModel):
    data: dict[str, Any]
    meta: ResponseMeta


class NatalCalculateResponse(BaseModel):
    data: dict[str, object]
    meta: ResponseMeta


class NatalCompareResponse(BaseModel):
    data: dict[str, object]
    meta: ResponseMeta


class ChartResultAuditResponse(BaseModel):
    data: ChartResultAuditRecord
    meta: ResponseMeta

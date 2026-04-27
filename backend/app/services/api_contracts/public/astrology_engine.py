"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.domain.astrology.natal_preparation import BirthInput
from app.services.chart.result_service import (
    ChartResultAuditRecord,
)

_NATAL_TECHNICAL_ERROR_CODES = frozenset(
    {
        "ephemeris_calc_failed",
        "houses_calc_failed",
    }
)


class NatalPrepareRequest(BirthInput):
    """Contrat Pydantic exposé par l'API."""

    tt_enabled: bool = False


class NatalCalculateRequest(BirthInput):
    """Contrat Pydantic exposé par l'API."""

    reference_version: str | None = None
    accurate: bool = False
    zodiac: str | None = None
    ayanamsa: str | None = None
    frame: str | None = None
    house_system: str | None = None
    altitude_m: float | None = None
    tt_enabled: bool = False


class NatalCompareRequest(BirthInput):
    """Contrat Pydantic exposé par l'API."""

    reference_version: str | None = None


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

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
    """Contrat Pydantic exposé par l'API."""

    data: dict[str, Any]
    meta: ResponseMeta


class NatalCalculateResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: dict[str, object]
    meta: ResponseMeta


class NatalCompareResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: dict[str, object]
    meta: ResponseMeta


class ChartResultAuditResponse(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    data: ChartResultAuditRecord
    meta: ResponseMeta

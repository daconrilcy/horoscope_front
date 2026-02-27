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
from app.services.chart_result_service import (
    ChartResultAuditRecord,
    ChartResultService,
    ChartResultServiceError,
)
from app.services.natal_calculation_service import NatalCalculationService
from app.services.natal_preparation_service import NatalPreparationService


class ResponseMeta(BaseModel):
    request_id: str
    engine: str | None = None
    ephemeris_path_version: str | None = None
    ephemeris_path_hash: str | None = None
    # Terrestrial Time fields (story 22.2) — present when tt_enabled=True.
    time_scale: str = "UT"
    delta_t_sec: float | None = None
    jd_tt: float | None = None


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class BirthPrepareResponse(BaseModel):
    data: dict[str, Any]
    meta: ResponseMeta


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


class NatalCalculateResponse(BaseModel):
    data: dict[str, object]
    meta: ResponseMeta


class NatalCompareRequest(BirthInput):
    reference_version: str | None = None


class NatalCompareResponse(BaseModel):
    data: dict[str, object]
    meta: ResponseMeta


class ChartResultAuditResponse(BaseModel):
    data: ChartResultAuditRecord
    meta: ResponseMeta


router = APIRouter(prefix="/v1/astrology-engine", tags=["astrology-engine"])
logger = logging.getLogger(__name__)
_NATAL_TECHNICAL_ERROR_CODES = frozenset(
    {
        "ephemeris_calc_failed",
        "houses_calc_failed",
    }
)


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _status_code_for_natal_error(error_code: str) -> int:
    if error_code == "reference_version_not_found":
        return 404
    if error_code in _NATAL_TECHNICAL_ERROR_CODES:
        return 503
    return 422


def _build_engine_diff(
    *,
    simplified_result: dict[str, Any],
    swisseph_result: dict[str, Any],
) -> dict[str, Any]:
    simplified_planets = {
        str(item["planet_code"]): float(item["longitude"])
        for item in simplified_result.get("planet_positions", [])
        if isinstance(item, dict)
        and isinstance(item.get("planet_code"), str)
        and item.get("longitude") is not None
    }
    swisseph_planets = {
        str(item["planet_code"]): float(item["longitude"])
        for item in swisseph_result.get("planet_positions", [])
        if isinstance(item, dict)
        and isinstance(item.get("planet_code"), str)
        and item.get("longitude") is not None
    }

    simplified_houses = {
        int(item["number"]): float(item["cusp_longitude"])
        for item in simplified_result.get("houses", [])
        if isinstance(item, dict)
        and item.get("number") is not None
        and item.get("cusp_longitude") is not None
    }
    swisseph_houses = {
        int(item["number"]): float(item["cusp_longitude"])
        for item in swisseph_result.get("houses", [])
        if isinstance(item, dict)
        and item.get("number") is not None
        and item.get("cusp_longitude") is not None
    }

    planet_diffs: list[dict[str, Any]] = []
    for planet_code in sorted(set(simplified_planets).intersection(swisseph_planets)):
        simplified_longitude = simplified_planets[planet_code]
        swisseph_longitude = swisseph_planets[planet_code]
        planet_diffs.append(
            {
                "planet_code": planet_code,
                "simplified_longitude": simplified_longitude,
                "swisseph_longitude": swisseph_longitude,
                "delta_degrees": round(simplified_longitude - swisseph_longitude, 6),
            }
        )

    house_diffs: list[dict[str, Any]] = []
    for house_number in sorted(set(simplified_houses).intersection(swisseph_houses)):
        simplified_cusp = simplified_houses[house_number]
        swisseph_cusp = swisseph_houses[house_number]
        house_diffs.append(
            {
                "house_number": house_number,
                "simplified_cusp_longitude": simplified_cusp,
                "swisseph_cusp_longitude": swisseph_cusp,
                "delta_degrees": round(simplified_cusp - swisseph_cusp, 6),
            }
        )

    max_planet_delta = max(
        (abs(float(item["delta_degrees"])) for item in planet_diffs), default=0.0
    )
    max_house_delta = max((abs(float(item["delta_degrees"])) for item in house_diffs), default=0.0)

    return {
        "planet_positions": planet_diffs,
        "houses": house_diffs,
        "summary": {
            "planet_positions_count": len(planet_diffs),
            "houses_count": len(house_diffs),
            "max_planet_delta_degrees": round(max_planet_delta, 6),
            "max_house_delta_degrees": round(max_house_delta, 6),
        },
    }


@router.post(
    "/natal/prepare",
    response_model=BirthPrepareResponse,
    responses={422: {"model": ErrorEnvelope}},
)
def prepare_natal(request: Request, payload: dict[str, Any]) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed_payload = NatalPrepareRequest.model_validate(payload)
        birth_input = BirthInput(
            birth_date=parsed_payload.birth_date,
            birth_time=parsed_payload.birth_time,
            birth_place=parsed_payload.birth_place,
            birth_timezone=parsed_payload.birth_timezone,
            place_resolved_id=parsed_payload.place_resolved_id,
            birth_city=parsed_payload.birth_city,
            birth_country=parsed_payload.birth_country,
            birth_lat=parsed_payload.birth_lat,
            birth_lon=parsed_payload.birth_lon,
        )
        tt_enabled = parsed_payload.tt_enabled or settings.swisseph_pro_mode
        prepared = NatalPreparationService.prepare(birth_input, tt_enabled=tt_enabled)

        eph_version = None
        eph_hash = None
        engine_name = "simplified"
        if settings.swisseph_enabled:
            result = ephemeris.get_bootstrap_result()
            if result and result.success:
                eph_version = result.path_version
                eph_hash = result.path_hash or None
                engine_name = "swisseph"

        return {
            "data": prepared.model_dump(),
            "meta": {
                "request_id": request_id,
                "engine": engine_name,
                "ephemeris_path_version": eph_version,
                "ephemeris_path_hash": eph_hash,
                "time_scale": prepared.time_scale,
                "delta_t_sec": prepared.delta_t_sec,
                "jd_tt": prepared.jd_tt,
            },
        }
    except ValidationError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except BirthPreparationError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/natal/calculate",
    response_model=NatalCalculateResponse,
    responses={
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def calculate_natal(
    request: Request,
    payload: dict[str, Any],
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed_payload = NatalCalculateRequest.model_validate(payload)
        birth_input = BirthInput(
            birth_date=parsed_payload.birth_date,
            birth_time=parsed_payload.birth_time,
            birth_place=parsed_payload.birth_place,
            birth_timezone=parsed_payload.birth_timezone,
            birth_lat=parsed_payload.birth_lat,
            birth_lon=parsed_payload.birth_lon,
            place_resolved_id=parsed_payload.place_resolved_id,
        )
        effective_tt_enabled = parsed_payload.tt_enabled or settings.swisseph_pro_mode
        result = NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            reference_version=parsed_payload.reference_version,
            accurate=parsed_payload.accurate,
            zodiac=parsed_payload.zodiac,
            ayanamsa=parsed_payload.ayanamsa,
            frame=parsed_payload.frame,
            house_system=parsed_payload.house_system,
            altitude_m=parsed_payload.altitude_m,
            request_id=request_id,
            tt_enabled=effective_tt_enabled,
        )
        chart_id = ChartResultService.persist_trace(
            db=db,
            birth_input=birth_input,
            natal_result=result,
        )
        db.commit()

        eph_version = None
        eph_hash = None
        if result.engine == "swisseph":
            eph_res = ephemeris.get_bootstrap_result()
            if eph_res and eph_res.success:
                eph_version = eph_res.path_version
                eph_hash = eph_res.path_hash or None

        prepared = result.prepared_input
        return {
            "data": {"chart_id": chart_id, "result": result.model_dump()},
            "meta": {
                "request_id": request_id,
                "engine": result.engine,
                "ephemeris_path_version": eph_version,
                "ephemeris_path_hash": eph_hash,
                "time_scale": result.time_scale,
                "delta_t_sec": prepared.delta_t_sec,
                "jd_tt": prepared.jd_tt,
            },
        }
    except ValidationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except BirthPreparationError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except NatalCalculationError as error:
        db.rollback()
        return _error_response(
            status_code=_status_code_for_natal_error(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except ChartResultServiceError as error:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/natal/compare",
    response_model=NatalCompareResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def compare_natal_engines(
    request: Request,
    payload: dict[str, Any],
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    if current_user.role not in {"support", "ops"}:
        return _error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "support,ops", "actual_role": current_user.role},
        )

    if settings.app_env == "production" or not settings.natal_engine_compare_enabled:
        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
            code="endpoint_not_available",
            message="endpoint is not available in this environment",
            details={},
        )

    try:
        parsed_payload = NatalCompareRequest.model_validate(payload)
        birth_input = BirthInput(
            birth_date=parsed_payload.birth_date,
            birth_time=parsed_payload.birth_time,
            birth_place=parsed_payload.birth_place,
            birth_timezone=parsed_payload.birth_timezone,
            birth_lat=parsed_payload.birth_lat,
            birth_lon=parsed_payload.birth_lon,
            place_resolved_id=parsed_payload.place_resolved_id,
        )

        swisseph_result = NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            reference_version=parsed_payload.reference_version,
            accurate=False,
            engine_override="swisseph",
            internal_request=True,
        )
        simplified_result = NatalCalculationService.calculate(
            db=db,
            birth_input=birth_input,
            reference_version=parsed_payload.reference_version,
            accurate=False,
            engine_override="simplified",
            internal_request=True,
        )

        swisseph_dump = swisseph_result.model_dump(mode="json")
        simplified_dump = simplified_result.model_dump(mode="json")
        diff = _build_engine_diff(
            simplified_result=simplified_dump,
            swisseph_result=swisseph_dump,
        )
        logger.info(
            "natal_engine_compare_completed",
            extra={
                "request_id": request_id,
                "planet_positions_count": diff["summary"]["planet_positions_count"],
                "houses_count": diff["summary"]["houses_count"],
                "max_planet_delta_degrees": diff["summary"]["max_planet_delta_degrees"],
                "max_house_delta_degrees": diff["summary"]["max_house_delta_degrees"],
            },
        )

        return {
            "data": {
                "swisseph": {
                    "engine": swisseph_dump.get("engine"),
                    "house_system": swisseph_dump.get("house_system"),
                    "ephemeris_path_version": swisseph_dump.get("ephemeris_path_version"),
                    "ephemeris_path_hash": swisseph_dump.get("ephemeris_path_hash"),
                },
                "simplified": {
                    "engine": simplified_dump.get("engine"),
                    "house_system": simplified_dump.get("house_system"),
                    "ephemeris_path_version": simplified_dump.get("ephemeris_path_version"),
                    "ephemeris_path_hash": simplified_dump.get("ephemeris_path_hash"),
                },
                "simplified_vs_swisseph": diff,
            },
            "meta": {"request_id": request_id},
        }
    except ValidationError as error:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except NatalCalculationError as error:
        return _error_response(
            status_code=_status_code_for_natal_error(error.code),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/results/{chart_id}",
    response_model=ChartResultAuditResponse,
    responses={404: {"model": ErrorEnvelope}},
)
def get_chart_result(
    request: Request,
    chart_id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"support", "ops"}:
        return _error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "support,ops", "actual_role": current_user.role},
        )
    try:
        audit_record = ChartResultService.get_audit_record(db, chart_id=chart_id)
        return {"data": audit_record.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ChartResultServiceError as error:
        return _error_response(
            status_code=404 if error.code == "chart_result_not_found" else 422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.request_id import resolve_request_id
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.session import get_db_session
from app.services.natal_interpretation_service import (
    NatalInterpretationData,
    NatalInterpretationService,
    NatalInterpretationServiceError,
)
from app.services.user_birth_profile_service import (
    UserBirthProfileData,
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_natal_chart_service import (
    UserNatalChartConsistencyData,
    UserNatalChartGenerationData,
    UserNatalChartReadData,
    UserNatalChartService,
    UserNatalChartServiceError,
)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class UserBirthProfileApiResponse(BaseModel):
    data: UserBirthProfileData
    meta: ResponseMeta


class NatalChartGenerateRequest(BaseModel):
    reference_version: str | None = None


class UserNatalChartApiResponse(BaseModel):
    data: UserNatalChartGenerationData
    meta: ResponseMeta


class UserNatalChartReadApiResponse(BaseModel):
    data: UserNatalChartReadData
    meta: ResponseMeta


class UserNatalChartConsistencyApiResponse(BaseModel):
    data: UserNatalChartConsistencyData
    meta: ResponseMeta


class NatalInterpretationApiResponse(BaseModel):
    data: NatalInterpretationData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get(
    "/me/birth-data",
    response_model=UserBirthProfileApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
def get_me_birth_data(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        profile = UserBirthProfileService.get_for_user(db, user_id=current_user.id)
        return {"data": profile.model_dump(), "meta": {"request_id": request_id}}
    except UserBirthProfileServiceError as error:
        status_code = 404 if error.code == "birth_profile_not_found" else 422
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.get(
    "/me/natal-chart/latest",
    response_model=UserNatalChartReadApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
async def get_me_latest_natal_chart(
    request: Request,
    include_interpretation: bool = False,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        latest = UserNatalChartService.get_latest_for_user(db=db, user_id=current_user.id)
    except UserNatalChartServiceError as error:
        status_code = (
            404 if error.code in {"natal_chart_not_found", "birth_profile_not_found"} else 422
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )

    response_data = latest.model_dump(mode="json")

    if include_interpretation:
        trace_id = request.headers.get("X-Trace-Id", request_id)
        try:
            profile = UserBirthProfileService.get_for_user(db, user_id=current_user.id)
            interpretation = await NatalInterpretationService.interpret_chart(
                natal_chart=latest,
                birth_profile=profile,
                user_id=current_user.id,
                request_id=request_id,
                trace_id=trace_id,
            )
            response_data["interpretation"] = interpretation.model_dump(mode="json")
        except (
            UserBirthProfileServiceError,
            NatalInterpretationServiceError,
            asyncio.TimeoutError,
        ):
            pass

    return {"data": response_data, "meta": {"request_id": request_id}}


@router.get(
    "/me/natal-chart/interpretation",
    response_model=NatalInterpretationApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def get_me_natal_chart_interpretation(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Génère une interprétation textuelle du thème natal de l'utilisateur."""
    request_id = resolve_request_id(request)
    trace_id = request.headers.get("X-Trace-Id", request_id)

    try:
        chart = UserNatalChartService.get_latest_for_user(db=db, user_id=current_user.id)
    except UserNatalChartServiceError as error:
        status_code = (
            404 if error.code in {"natal_chart_not_found", "birth_profile_not_found"} else 422
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )

    try:
        profile = UserBirthProfileService.get_for_user(db, user_id=current_user.id)
    except UserBirthProfileServiceError as error:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )

    try:
        interpretation = await NatalInterpretationService.interpret_chart(
            natal_chart=chart,
            birth_profile=profile,
            user_id=current_user.id,
            request_id=request_id,
            trace_id=trace_id,
        )
        return {
            "data": interpretation.model_dump(mode="json"),
            "meta": {"request_id": request_id},
        }
    except NatalInterpretationServiceError as error:
        if error.code == "ai_engine_timeout":
            status_code = 503
        elif "rate" in error.code.lower() or error.code == "rate_limit_exceeded":
            status_code = 429
        else:
            status_code = 503
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.get(
    "/{user_id}/natal-chart/consistency",
    response_model=UserNatalChartConsistencyApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
    },
)
def get_natal_chart_consistency(
    request: Request,
    user_id: int,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if current_user.role not in {"support", "ops"}:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "insufficient_role",
                    "message": "role is not allowed",
                    "details": {"required_roles": "support,ops"},
                    "request_id": request_id,
                }
            },
        )

    try:
        report = UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)
        return {"data": report.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except UserNatalChartServiceError as error:
        if error.code == "natal_result_mismatch":
            return {
                "data": {
                    "user_id": user_id,
                    "consistent": False,
                    "reason": error.details.get("reason", "payload_mismatch"),
                    "mismatch_code": "natal_result_mismatch",
                    "latest_chart_id": error.details.get("latest_chart_id", ""),
                    "baseline_chart_id": error.details.get("baseline_chart_id", ""),
                    "reference_version": error.details.get("reference_version", ""),
                    "ruleset_version": error.details.get("ruleset_version", ""),
                    "input_hash": error.details.get("input_hash", ""),
                },
                "meta": {"request_id": request_id},
            }

        status_code = (
            404 if error.code in {"no_comparable_charts", "birth_profile_not_found"} else 422
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )


@router.put(
    "/me/birth-data",
    response_model=UserBirthProfileApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
def upsert_me_birth_data(
    request: Request,
    payload: dict[str, Any],
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed = BirthInput.model_validate(payload)
        profile = UserBirthProfileService.upsert_for_user(
            db,
            user_id=current_user.id,
            payload=parsed,
        )
        db.commit()
        return {"data": profile.model_dump(), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_birth_input",
                    "message": "birth input validation failed",
                    "details": {"errors": error.errors()},
                    "request_id": request_id,
                }
            },
        )
    except BirthPreparationError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except UserBirthProfileServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "user_not_found" else 422
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "birth profile persistence failed",
            extra={"user_id": current_user.id, "request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "birth_profile_persistence_error",
                    "message": "birth profile could not be persisted",
                    "details": {},
                    "request_id": request_id,
                }
            },
        )


@router.post(
    "/me/natal-chart",
    response_model=UserNatalChartApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def generate_me_natal_chart(
    request: Request,
    payload: dict[str, Any],
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        parsed_payload = NatalChartGenerateRequest.model_validate(payload)
        generated = UserNatalChartService.generate_for_user(
            db=db,
            user_id=current_user.id,
            reference_version=parsed_payload.reference_version,
        )
        db.commit()
        return {"data": generated.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "invalid_natal_chart_request",
                    "message": "natal chart request validation failed",
                    "details": {"errors": error.errors()},
                    "request_id": request_id,
                }
            },
        )
    except UserNatalChartServiceError as error:
        db.rollback()
        if error.code in {"birth_profile_not_found", "reference_version_not_found"}:
            status_code = 404
        elif error.code in {"natal_generation_timeout", "natal_engine_unavailable"}:
            status_code = 503
        else:
            status_code = 422
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": error.details,
                    "request_id": request_id,
                }
            },
        )

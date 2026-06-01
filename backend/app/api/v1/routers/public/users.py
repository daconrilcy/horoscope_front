# Commentaire global: routes publiques de gestion du profil utilisateur et de ses preferences.
"""Routes publiques de gestion du profil utilisateur et de ses préférences."""

from __future__ import annotations

import logging
from threading import Lock
from time import monotonic
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.errors import build_error_response
from app.api.v1.constants import VALID_ASTROLOGER_PROFILES
from app.core.request_id import resolve_request_id
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.users import (
    NatalChartGenerateRequest,
    UserBirthProfileApiResponse,
    UserBirthProfileWithAstroApiResponse,
    UserBirthProfileWithAstroData,
    UserNatalChartApiResponse,
    UserNatalChartConsistencyApiResponse,
    UserNatalChartLatestApiResponse,
    UserSettingsApiResponse,
    UserSettingsPatchRequest,
)
from app.services.user_profile.astro_profile_service import (
    UserAstroProfileData,
    UserAstroProfileService,
    UserAstroProfileServiceError,
)
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartService,
    UserNatalChartServiceError,
)
from app.services.user_profile.public_users import (
    _natal_inconsistent_metric_name,
    _should_log_inconsistent_result_event,
)
from app.services.user_profile.settings_service import (
    UserSettingsService,
    UserSettingsServiceError,
)

router = APIRouter(prefix="/v1/users", tags=["users"])
logger = logging.getLogger(__name__)
_INCONSISTENT_LOG_WINDOW_SECONDS = 60.0
_INCONSISTENT_LOG_ALWAYS_PER_WINDOW = 10
_INCONSISTENT_LOG_SAMPLING_RATIO = 0.01
_inconsistent_log_sampling_lock = Lock()
_inconsistent_log_sampling_state = {"window_start": monotonic(), "count": 0}


@router.get(
    "/me/birth-data",
    response_model=UserBirthProfileWithAstroApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
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
    except UserBirthProfileServiceError as error:
        status_code = 404 if error.code == "birth_profile_not_found" else 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    astro_profile: UserAstroProfileData | None = None
    try:
        astro_profile = UserAstroProfileService.get_for_user(db, user_id=current_user.id)
    except UserAstroProfileServiceError as error:
        logger.warning(
            "astro profile computation failed",
            extra={"user_id": current_user.id, "request_id": request_id, "code": error.code},
        )
    except Exception:
        logger.exception(
            "unexpected astro profile failure",
            extra={"user_id": current_user.id, "request_id": request_id},
        )
        return build_error_response(
            status_code=500,
            request_id=request_id,
            code="astro_profile_computation_error",
            message="astro profile could not be computed",
            details={},
        )

    data = UserBirthProfileWithAstroData(
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        birth_place=profile.birth_place,
        birth_place_text=profile.birth_place_text,
        birth_timezone=profile.birth_timezone,
        birth_city=profile.birth_city,
        birth_country=profile.birth_country,
        birth_lat=profile.birth_lat,
        birth_lon=profile.birth_lon,
        birth_place_resolved_id=profile.birth_place_resolved_id,
        birth_place_resolved=profile.birth_place_resolved,
        geolocation_consent=profile.geolocation_consent,
        current_city=profile.current_city,
        current_country=profile.current_country,
        current_lat=profile.current_lat,
        current_lon=profile.current_lon,
        current_location_display=profile.current_location_display,
        current_timezone=profile.current_timezone,
        astro_profile=astro_profile,
    )
    return {"data": data.model_dump(), "meta": {"request_id": request_id}}


@router.get(
    "/me/natal-chart/latest",
    response_model=UserNatalChartLatestApiResponse,
    responses={
        200: {"description": "Latest natal chart with astro profile"},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def get_me_latest_natal_chart(
    request: Request,
    include_interpretation: bool = False,
    persona_id: str | None = None,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if include_interpretation:
        return _legacy_natal_interpretation_gone(request_id)

    try:
        latest = UserNatalChartService.get_latest_for_user(db=db, user_id=current_user.id)
    except UserNatalChartServiceError as error:
        status_code = (
            404 if error.code in {"natal_chart_not_found", "birth_profile_not_found"} else 422
        )
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    response_data = latest.model_dump(mode="json")

    try:
        astro_profile = UserAstroProfileService.get_for_user(db, user_id=current_user.id)
        response_data["astro_profile"] = astro_profile.model_dump()
    except UserAstroProfileServiceError as error:
        logger.warning(
            "astro profile computation failed",
            extra={"user_id": current_user.id, "request_id": request_id, "code": error.code},
        )
        response_data["astro_profile"] = None
    except Exception:
        logger.exception(
            "unexpected astro profile failure",
            extra={"user_id": current_user.id, "request_id": request_id},
        )
        return build_error_response(
            status_code=500,
            request_id=request_id,
            code="astro_profile_computation_error",
            message="astro profile could not be computed",
            details={},
        )

    return {"data": response_data, "meta": {"request_id": request_id}}


@router.get(
    "/me/natal-chart/interpretation",
    response_model=None,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        410: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def get_me_natal_chart_interpretation(
    request: Request,
    persona_id: str | None = None,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Refuse l'ancien endpoint generateur au profit de l'action produit canonique."""
    request_id = resolve_request_id(request)
    _ = (persona_id, current_user, db)
    return _legacy_natal_interpretation_gone(request_id)


def _legacy_natal_interpretation_gone(request_id: str) -> Any:
    """Retourne l'arret controle des generations natales publiques legacy."""
    return build_error_response(
        status_code=410,
        request_id=request_id,
        code="natal_interpretation_endpoint_gone",
        message="Legacy natal generation is readonly; use POST /v1/theme-natal/readings.",
        details={"state": "readonly", "replacement": "/v1/theme-natal/readings"},
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
    if current_user.role not in {"support", "ops", "admin"}:
        return build_error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "support,ops,admin"},
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
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
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
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_birth_input",
            message="birth input validation failed",
            details={"errors": error.errors()},
        )
    except BirthPreparationError as error:
        db.rollback()
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except UserBirthProfileServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "user_not_found" else 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "birth profile persistence failed",
            extra={"user_id": current_user.id, "request_id": request_id},
        )
        return build_error_response(
            status_code=500,
            request_id=request_id,
            code="birth_profile_persistence_error",
            message="birth profile could not be persisted",
            details={},
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
            accurate=parsed_payload.accurate,
            zodiac=parsed_payload.zodiac,
            ayanamsa=parsed_payload.ayanamsa,
            frame=parsed_payload.frame,
            house_system=parsed_payload.house_system,
            altitude_m=parsed_payload.altitude_m,
        )
        db.commit()

        return {"data": generated.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        return build_error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_natal_chart_request",
            message="natal chart request validation failed",
            details={"errors": error.errors()},
        )
    except UserNatalChartServiceError as error:
        db.rollback()
        if error.code == "inconsistent_natal_result":
            reference_version = error.details.get("reference_version")
            house_system = error.details.get("house_system")
            planet_code = error.details.get("planet_code")
            increment_counter("natal_inconsistent_result_total", 1.0)
            increment_counter(
                _natal_inconsistent_metric_name(
                    reference_version=reference_version,
                    house_system=house_system,
                    planet_code=planet_code,
                ),
                1.0,
            )
            if _should_log_inconsistent_result_event():
                logger.warning(
                    "natal_inconsistent_result_detected",
                    extra={
                        "request_id": request_id,
                        "reference_version": reference_version or "unknown",
                        "house_system": house_system or "unknown",
                        "planet_code": planet_code,
                        "longitude": error.details.get("longitude"),
                        "expected_sign_code": error.details.get("expected_sign_code"),
                        "actual_sign_code": error.details.get("actual_sign_code"),
                        "house_number": error.details.get("house_number"),
                        "interval_start": error.details.get("interval_start"),
                        "interval_end": error.details.get("interval_end"),
                    },
                )
        if error.code in {"birth_profile_not_found", "reference_version_not_found"}:
            status_code = 404
        elif error.code in {"natal_generation_timeout", "natal_engine_unavailable"}:
            status_code = 503
        else:
            status_code = 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/me/settings",
    response_model=UserSettingsApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
def get_me_settings(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        data = UserSettingsService.get_for_user(db, current_user.id)
    except UserSettingsServiceError as error:
        return build_error_response(
            status_code=404,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    return {
        "data": data,
        "meta": {"request_id": request_id},
    }


@router.patch(
    "/me/settings",
    response_model=UserSettingsApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
def patch_me_settings(
    request: Request,
    payload: UserSettingsPatchRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        data = UserSettingsService.patch_for_user(
            db,
            current_user.id,
            payload,
            set(VALID_ASTROLOGER_PROFILES),
        )
    except UserSettingsServiceError as error:
        if error.code == "user_not_found":
            status_code = 404
        elif error.code == "user_settings_persistence_error":
            status_code = 500
            logger.exception(
                "user settings persistence failed",
                extra={"user_id": current_user.id, "request_id": request_id},
            )
        else:
            status_code = 422
        return build_error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    return {
        "data": data,
        "meta": {"request_id": request_id},
    }

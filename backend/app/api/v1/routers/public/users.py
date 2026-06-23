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
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.common import ErrorEnvelope
from app.services.api_contracts.public.users import (
    UserBirthProfileApiResponse,
    UserBirthProfileWithAstroApiResponse,
    UserBirthProfileWithAstroData,
    UserSettingsApiResponse,
    UserSettingsPatchRequest,
)
from app.services.user_profile.birth_profile_service import (
    BirthInput,
    UserBirthProfileService,
    UserBirthProfileServiceError,
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

    data = UserBirthProfileWithAstroData(
        birth_date=profile.birth_date,
        birth_year=profile.birth_year,
        birth_month=profile.birth_month,
        birth_day=profile.birth_day,
        birth_date_precision=profile.birth_date_precision,
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
        astro_profile=None,
    )
    return {"data": data.model_dump(), "meta": {"request_id": request_id}}


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

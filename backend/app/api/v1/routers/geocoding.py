from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_optional_authenticated_user
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.repositories.geo_place_resolved_repository import GeoPlaceResolvedRepository
from app.infra.db.session import get_db_session
from app.services.geocoding_service import (
    GeocodingSearchResult,
    GeocodingService,
    GeocodingServiceError,
)

router = APIRouter(prefix="/v1/geocoding", tags=["geocoding"])


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


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


def _normalize_query(q: str) -> str:
    """Trim et collapse des espaces multiples."""
    return re.sub(r"\s+", " ", q.strip())


def _result_to_dict(r: GeocodingSearchResult) -> dict[str, Any]:
    return r.model_dump(by_alias=True)


def _resolved_place_to_dict(model: Any) -> dict[str, Any]:
    return {
        "id": model.id,
        "provider": model.provider,
        "provider_place_id": model.provider_place_id,
        "osm_type": model.osm_type,
        "osm_id": model.osm_id,
        "display_name": model.display_name,
        "latitude": float(model.latitude),
        "longitude": float(model.longitude),
        "timezone_iana": model.timezone_iana,
        "timezone_source": model.timezone_source,
        "timezone_confidence": model.timezone_confidence,
    }


def _can_use_seed_token_fallback() -> bool:
    return (
        settings.enable_reference_seed_admin_fallback
        and settings.app_env in {"development", "dev", "local", "test", "testing"}
    )


def _validate_nocache_access(
    *,
    nocache: bool,
    x_admin_token: str | None,
    current_user: AuthenticatedUser | None,
) -> tuple[bool, str, str, dict[str, Any]]:
    if not nocache:
        return True, "", "", {}
    if current_user is not None and current_user.role in {"support", "ops"}:
        return True, "", "", {}
    if current_user is not None and current_user.role not in {"support", "ops"}:
        return (
            False,
            "insufficient_role",
            "role is not allowed",
            {"required_roles": "support,ops", "actual_role": current_user.role},
        )
    if _can_use_seed_token_fallback() and x_admin_token == settings.reference_seed_admin_token:
        return True, "", "", {}
    return False, "unauthorized_nocache_access", "invalid admin token", {}


@router.get(
    "/search",
    response_model=None,
    responses={
        200: {"model": dict[str, Any]},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def search_places(
    request: Request,
    q: str = Query(..., description="Requête de recherche de lieu"),
    limit: int = Query(default=5, description="Nombre max de résultats (1-10)"),
    nocache: bool = Query(default=False, description="Bypass du cache DB (usage dev/admin)"),
    country_code: str | None = Query(default=None, description="Code pays ISO-3166 alpha-2"),
    lang: str | None = Query(default=None, description="Langue de réponse (ex: fr, en)"),
    x_admin_token: str | None = Header(default=None),
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    allowed, code, message, details = _validate_nocache_access(
        nocache=nocache,
        x_admin_token=x_admin_token,
        current_user=current_user,
    )
    if not allowed:
        return _error_response(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if code == "insufficient_role"
                else status.HTTP_401_UNAUTHORIZED
            ),
            request_id=request_id,
            code=code,
            message=message,
            details=details,
        )

    normalized = _normalize_query(q)
    if len(normalized) < 2:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            request_id=request_id,
            code="invalid_geocoding_query",
            message="Query must be at least 2 characters",
            details={"query": normalized, "min_length": 2},
        )

    clamped_limit = max(1, min(10, limit))
    normalized_country_code = country_code.strip().lower() if country_code else None
    normalized_lang = lang.strip().lower() if lang else None

    try:
        results = GeocodingService.search_with_cache(
            db,
            normalized,
            clamped_limit,
            nocache=nocache,
            country_code=normalized_country_code,
            lang=normalized_lang,
        )
    except GeocodingServiceError as err:
        if err.code == "geocoding_rate_limited":
            return _error_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                request_id=request_id,
                code=err.code,
                message=err.message,
                details=err.details,
            )
        return _error_response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            request_id=request_id,
            code=err.code,
            message=err.message,
            details=err.details,
        )

    return {
        "data": {
            "results": [_result_to_dict(r) for r in results],
            "count": len(results),
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/resolved/{place_resolved_id}",
    response_model=None,
    responses={
        200: {"model": dict[str, Any]},
        404: {"model": ErrorEnvelope},
    },
)
def get_resolved_place(
    place_resolved_id: int,
    request: Request,
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    place = GeoPlaceResolvedRepository(db).find_by_id(place_resolved_id)
    if place is None:
        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
            code="resolved_place_not_found",
            message="Resolved place not found",
            details={"place_resolved_id": place_resolved_id},
        )

    return {
        "data": _resolved_place_to_dict(place),
        "meta": {"request_id": request_id},
    }

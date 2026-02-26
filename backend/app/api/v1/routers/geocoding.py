from __future__ import annotations

import math
import re
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_optional_authenticated_user
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

router = APIRouter(prefix="/v1/geocoding", tags=["geocoding"])


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class GeocodingResolveRequest(BaseModel):
    provider: Literal["nominatim"]
    provider_place_id: int = Field(gt=0)
    snapshot: GeocodingSearchResult | None = None


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


def _validate_resolve_snapshot(snapshot: GeocodingSearchResult) -> None:
    if snapshot.provider_place_id <= 0:
        raise ValueError("snapshot provider_place_id must be positive")
    if not snapshot.display_name.strip():
        raise ValueError("snapshot display_name must not be blank")
    if not snapshot.osm_type.strip():
        raise ValueError("snapshot osm_type must not be blank")
    if snapshot.osm_id <= 0:
        raise ValueError("snapshot osm_id must be positive")
    if not math.isfinite(snapshot.lat) or snapshot.lat < -90 or snapshot.lat > 90:
        raise ValueError("snapshot lat must be within [-90, 90]")
    if not math.isfinite(snapshot.lon) or snapshot.lon < -180 or snapshot.lon > 180:
        raise ValueError("snapshot lon must be within [-180, 180]")


def _can_use_seed_token_fallback() -> bool:
    return settings.enable_reference_seed_admin_fallback and settings.app_env in {
        "development",
        "dev",
        "local",
        "test",
        "testing",
    }


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


@router.post(
    "/resolve",
    response_model=None,
    responses={
        200: {"model": dict[str, Any]},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
def resolve_place(
    request: Request,
    payload: GeocodingResolveRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)

    if payload.snapshot is None:
        try:
            snapshot = GeocodingService.resolve_place_snapshot(
                provider=payload.provider,
                provider_place_id=payload.provider_place_id,
            )
        except GeocodingServiceError as err:
            return _error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                request_id=request_id,
                code=err.code,
                message=err.message,
                details=err.details,
            )
    else:
        snapshot = payload.snapshot

    if isinstance(snapshot, dict):
        try:
            snapshot = GeocodingSearchResult.model_validate(snapshot)
        except ValidationError as err:
            return _error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                request_id=request_id,
                code="geocoding_provider_unavailable",
                message="Invalid response from geocoding provider",
                details={"errors": err.errors()},
            )

    try:
        if snapshot.provider_place_id != payload.provider_place_id:
            raise ValueError("snapshot provider_place_id must match request provider_place_id")
        _validate_resolve_snapshot(snapshot)
    except ValueError as err:
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            request_id=request_id,
            code="invalid_geocoding_resolve_payload",
            message="resolve payload validation failed",
            details={"reason": str(err)},
        )

    repo = GeoPlaceResolvedRepository(db)
    try:
        resolved, _ = repo.find_or_create(
            data=GeoPlaceResolvedCreateData(
                provider=payload.provider,
                provider_place_id=snapshot.provider_place_id,
                display_name=snapshot.display_name,
                latitude=snapshot.lat,
                longitude=snapshot.lon,
                osm_type=snapshot.osm_type,
                osm_id=snapshot.osm_id,
                place_type=snapshot.type,
                place_class=snapshot.class_,
                importance=snapshot.importance,
                place_rank=snapshot.place_rank,
                country_code=snapshot.address.country_code,
                country=snapshot.address.country,
                state=snapshot.address.state,
                county=snapshot.address.county,
                city=snapshot.address.city,
                postcode=snapshot.address.postcode,
                raw_payload=snapshot.model_dump(mode="json", by_alias=True),
            )
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
            code="geocoding_resolve_persistence_error",
            message="resolved place could not be persisted",
            details={},
        )

    return {"data": _resolved_place_to_dict(resolved), "meta": {"request_id": request_id}}

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    AuthenticatedUser,
    get_optional_authenticated_user,
    require_authenticated_user,
)
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.public.geocoding import (
    GeocodingResolveRequest,
    ReverseGeocodingRequest,
)
from app.core.request_id import resolve_request_id
from app.infra.db.repositories.geo_place_resolved_repository import (
    GeoPlaceResolvedCreateData,
    GeoPlaceResolvedRepository,
)
from app.infra.db.session import get_db_session
from app.services.geocoding.public_support import (
    _error_response,
    _normalize_query,
    _resolved_place_to_dict,
    _result_to_dict,
    _validate_nocache_access,
    _validate_resolve_snapshot,
)
from app.services.geocoding_service import (
    GeocodingSearchResult,
    GeocodingService,
    GeocodingServiceError,
)

logger = logging.getLogger(__name__)

try:
    from timezonefinder import TimezoneFinder as _TimezoneFinder

    _TF: _TimezoneFinder | None = _TimezoneFinder()
except Exception:
    logger.warning("timezonefinder not available — reverse geocoding timezone resolution disabled")
    _TF = None

router = APIRouter(prefix="/v1/geocoding", tags=["geocoding"])


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


@router.post(
    "/reverse",
    response_model=None,
    responses={
        200: {"model": dict[str, Any]},
        401: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def reverse_geocode(
    request: Request,
    payload: ReverseGeocodingRequest,
    lang: str | None = Query(default=None, description="Langue de réponse (ex: fr, en)"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    normalized_lang = lang.strip().lower() if lang else None

    try:
        result = GeocodingService.reverse(
            lat=payload.lat,
            lon=payload.lon,
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

    # Resolution timezone IANA via timezonefinder (singleton initialisé au démarrage du module)
    timezone_iana: str | None = None
    if _TF is not None:
        try:
            timezone_iana = _TF.timezone_at(lng=payload.lon, lat=payload.lat)
        except Exception:
            logger.exception("timezone_resolution_failed_in_reverse")

    return {
        "data": {
            "display_name": result.display_name,
            "city": result.address.city,
            "country": result.address.country,
            "lat": result.lat,
            "lon": result.lon,
            "timezone_iana": timezone_iana,
        },
        "meta": {"request_id": request_id},
    }

import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.ai_engine.routes import router as ai_engine_router
from app.api.dependencies.auth import UserAuthenticationError
from app.api.dependencies.b2b_auth import EnterpriseApiKeyAuthenticationError
from app.api.health import router as health_router
from app.api.v1.routers.astrology_engine import router as astrology_engine_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.b2b_astrology import router as b2b_astrology_router
from app.api.v1.routers.b2b_billing import router as b2b_billing_router
from app.api.v1.routers.b2b_editorial import router as b2b_editorial_router
from app.api.v1.routers.b2b_reconciliation import router as b2b_reconciliation_router
from app.api.v1.routers.b2b_usage import router as b2b_usage_router
from app.api.v1.routers.billing import router as billing_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.chat_modules import router as chat_modules_router
from app.api.v1.routers.enterprise_credentials import router as enterprise_credentials_router
from app.api.v1.routers.ephemeris import router as ephemeris_router
from app.api.v1.routers.geocoding import router as geocoding_router
from app.api.v1.routers.guidance import router as guidance_router
from app.api.v1.routers.ops_feature_flags import router as ops_feature_flags_router
from app.api.v1.routers.ops_monitoring import router as ops_monitoring_router
from app.api.v1.routers.ops_persona import router as ops_persona_router
from app.api.v1.routers.privacy import router as privacy_router
from app.api.v1.routers.reference_data import router as reference_data_router
from app.api.v1.routers.support import router as support_router
from app.api.v1.routers.users import router as users_router
from app.core import ephemeris as _eph
from app.core.config import settings
from app.core.ephemeris import EphemerisDataMissingError, SwissEphInitError
from app.core.request_id import resolve_request_id
from app.domain.astrology.ephemeris_provider import EphemerisCalcError
from app.domain.astrology.houses_provider import HousesCalcError, UnsupportedHouseSystemError
from app.domain.astrology.natal_preparation import (
    warmup_timezone_finder,
)
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.pricing_experiment_service import PricingExperimentService


@asynccontextmanager
async def _app_lifespan(_: FastAPI):
    PricingExperimentService.record_variant_state_change(
        enabled=PricingExperimentService.is_enabled(),
        request_id=None,
    )
    if settings.timezone_derived_enabled:
        # Pre-load timezone polygon data to avoid first-request latency spike.
        warmup_timezone_finder()

    if settings.swisseph_enabled:
        try:
            _eph.bootstrap_swisseph(
                data_path=settings.ephemeris_path,
                path_version=settings.ephemeris_path_version,
                expected_path_hash=settings.ephemeris_path_hash,
                required_files=settings.ephemeris_required_files,
                validate_required_files=True,
            )
        except (EphemerisDataMissingError, SwissEphInitError):
            # Error stored in ephemeris module state; accurate endpoints return 5xx.
            pass
    yield


app = FastAPI(title="horoscope-backend", version="0.1.0", lifespan=_app_lifespan)
logger = logging.getLogger(__name__)


def _sanitize_metric_value(value: str) -> str:
    return value.replace("|", "_").replace("=", "_").replace(" ", "_")


def _metric_name(base: str, **labels: str) -> str:
    if not labels:
        return base
    parts = [base]
    for key in sorted(labels):
        parts.append(f"{key}={_sanitize_metric_value(labels[key])}")
    return "|".join(parts)


def _resolve_route_template(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    if isinstance(route_path, str) and route_path:
        return route_path
    return "__unmatched__"


def _record_http_metrics(
    method: str, route: str, status_code: int, duration_seconds: float
) -> None:
    status_class = f"{status_code // 100}xx"
    labels = {"method": method, "route": route, "status_class": status_class}
    increment_counter(_metric_name("http_requests_total", **labels), 1.0)
    observe_duration(_metric_name("http_request_duration_seconds", **labels), duration_seconds)

    if 400 <= status_code < 500:
        increment_counter(_metric_name("http_requests_client_errors_total", **labels), 1.0)
    elif status_code >= 500:
        increment_counter(_metric_name("http_requests_server_errors_total", **labels), 1.0)


@app.middleware("http")
async def observability_http_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = resolve_request_id(request)
    started = monotonic()
    method = request.method

    try:
        response = await call_next(request)
    except Exception:
        duration = monotonic() - started
        route = _resolve_route_template(request)
        _record_http_metrics(method, route, 500, duration)
        logger.exception(
            "http_request_failed request_id=%s method=%s route=%s status_code=500 duration_ms=%.2f",
            request_id,
            method,
            route,
            duration * 1000.0,
        )
        raise

    duration = monotonic() - started
    route = _resolve_route_template(request)
    _record_http_metrics(method, route, response.status_code, duration)
    response.headers["X-Request-Id"] = request_id

    if response.status_code >= 500:
        logger.error(
            (
                "http_request_server_error request_id=%s method=%s route=%s "
                "status_code=%s duration_ms=%.2f"
            ),
            request_id,
            method,
            route,
            response.status_code,
            duration * 1000.0,
        )

    return response


@app.exception_handler(RequestValidationError)
def handle_request_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_birth_input",
                "message": "request payload validation failed",
                "details": {"errors": error.errors()},
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(UserAuthenticationError)
def handle_user_authentication_error(
    request: Request, error: UserAuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(EnterpriseApiKeyAuthenticationError)
def handle_enterprise_api_key_authentication_error(
    request: Request, error: EnterpriseApiKeyAuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(EphemerisDataMissingError)
def handle_ephemeris_data_missing_error(
    request: Request, error: EphemerisDataMissingError
) -> JSONResponse:
    details: dict[str, str] = {}
    if getattr(error, "missing_file", None) is not None:
        details["missing_file"] = error.missing_file  # type: ignore[assignment]
    logger.error(
        "swisseph_error_handled code=%s missing_file=%s request_id=%s",
        error.code,
        details.get("missing_file", ""),
        resolve_request_id(request),
    )
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": details,
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(SwissEphInitError)
def handle_swisseph_init_error(request: Request, error: SwissEphInitError) -> JSONResponse:
    logger.error(
        "swisseph_error_handled code=%s request_id=%s",
        error.code,
        resolve_request_id(request),
    )
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": {},
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(EphemerisCalcError)
def handle_ephemeris_calc_error(request: Request, error: EphemerisCalcError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": {},
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(HousesCalcError)
def handle_houses_calc_error(request: Request, error: HousesCalcError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": {},
                "request_id": resolve_request_id(request),
            }
        },
    )


@app.exception_handler(UnsupportedHouseSystemError)
def handle_unsupported_house_system_error(
    request: Request, error: UnsupportedHouseSystemError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": {},
                "request_id": resolve_request_id(request),
            }
        },
    )


# Restrictive-by-default CORS for local development bootstrap.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(ephemeris_router)
app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(billing_router)
app.include_router(astrology_engine_router)
app.include_router(b2b_astrology_router)
app.include_router(b2b_billing_router)
app.include_router(b2b_editorial_router)
app.include_router(b2b_reconciliation_router)
app.include_router(b2b_usage_router)
app.include_router(chat_router)
app.include_router(chat_modules_router)
app.include_router(geocoding_router)
app.include_router(enterprise_credentials_router)
app.include_router(guidance_router)
app.include_router(ops_monitoring_router)
app.include_router(ops_feature_flags_router)
app.include_router(ops_persona_router)
app.include_router(privacy_router)
app.include_router(reference_data_router)
app.include_router(users_router)
app.include_router(support_router)
app.include_router(ai_engine_router)

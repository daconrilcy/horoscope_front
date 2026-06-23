# Commentaire global: point d'entree FastAPI et assemblage runtime de l'application backend.
"""Point d'entree FastAPI et assemblage runtime de l'application backend."""

import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.dependencies.auth import UserAuthenticationError
from app.api.dependencies.b2b_auth import EnterpriseApiKeyAuthenticationError
from app.api.errors.handlers import application_error_handler, build_error_response
from app.api.route_exceptions import include_registered_route_exceptions
from app.api.v1.routers.registry import include_api_v1_routers
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.core.request_id import resolve_request_id
from app.infra.db.bootstrap import ensure_local_sqlite_schema_ready
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.billing.pricing_experiment_service import PricingExperimentService
from app.startup.canonical_db_validation import run_canonical_db_startup_validation
from app.startup.feature_scope_validation import run_feature_scope_startup_validation
from app.startup.stripe_portal_validation import run_stripe_portal_startup_validation

logger = logging.getLogger(__name__)


def _open_startup_db_session() -> Session:
    """Ouvre une session DB pour les routines de demarrage local."""
    from app.infra.db.session import SessionLocal

    return SessionLocal()


def _ensure_support_categories_seeded() -> None:
    """Auto-seed support categories locally when the table is empty."""
    if settings.app_env in {"production", "prod"}:
        return

    from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
    from app.infra.db.session import SessionLocal
    from scripts.seed_support_categories import seed_support_categories

    try:
        with SessionLocal() as db:
            count = db.query(SupportTicketCategoryModel).count()
            if count > 0:
                return
        logger.warning("support_categories_auto_seed table is empty, seeding...")
        seed_support_categories()
    except Exception as e:
        logger.error("support_categories_auto_seed_failed error=%s", e)


def _ensure_canonical_entitlements_seeded() -> None:
    """Auto-heal canonical entitlements locally before strict startup validation."""
    if settings.app_env in {"production", "prod"}:
        return

    from sqlalchemy.exc import OperationalError

    from app.infra.db.models.product_entitlements import FeatureCatalogModel
    from app.infra.db.session import SessionLocal
    from app.services.entitlement.feature_scope_registry import FEATURE_SCOPE_REGISTRY
    from scripts.seed_product_entitlements import seed as seed_product_entitlements

    def _missing_feature_codes() -> set[str]:
        with SessionLocal() as db:
            existing = {row.feature_code for row in db.query(FeatureCatalogModel).all()}
        return set(FEATURE_SCOPE_REGISTRY) - existing

    try:
        missing_codes = _missing_feature_codes()
    except OperationalError as error:
        is_local_dev = settings.app_env in {"development", "dev", "local"}
        if not is_local_dev or not settings._is_local_sqlite_database_url(settings.database_url):
            raise
        logger.warning("canonical_entitlements_local_sqlite_repair error=%s", error)
        ensure_local_sqlite_schema_ready()
        missing_codes = _missing_feature_codes()

    if not missing_codes:
        return

    logger.warning(
        "canonical_entitlements_auto_heal missing_features=%s",
        ",".join(sorted(missing_codes)),
    )
    seed_product_entitlements()

    with SessionLocal() as db:
        for feature_code in sorted(missing_codes):
            if feature_code != "b2b_api_access":
                continue
            feature = (
                db.query(FeatureCatalogModel)
                .filter(FeatureCatalogModel.feature_code == feature_code)
                .one_or_none()
            )
            if feature is None:
                db.add(
                    FeatureCatalogModel(
                        feature_code=feature_code,
                        feature_name="B2B API Access",
                        description="Acces volumetrique a l API entreprise",
                        is_metered=True,
                        is_active=True,
                    )
                )
            else:
                feature.feature_name = "B2B API Access"
                feature.description = "Acces volumetrique a l API entreprise"
                feature.is_metered = True
                feature.is_active = True
        db.commit()


@asynccontextmanager
async def _app_lifespan(_: FastAPI):
    from app.core.scheduler import shutdown_scheduler, start_scheduler

    start_scheduler()

    ensure_local_sqlite_schema_ready()
    PricingExperimentService.record_variant_state_change(
        enabled=PricingExperimentService.is_enabled(),
        request_id=None,
    )
    _ensure_canonical_entitlements_seeded()
    _ensure_support_categories_seeded()
    from app.startup import seed_dev_admin

    await seed_dev_admin()

    # Story 61.29: Enforcement du registre de scope au démarrage
    run_feature_scope_startup_validation(settings.feature_scope_validation_mode)

    # Story 61.64: Safeguard for Stripe Customer Portal
    run_stripe_portal_startup_validation(settings)

    from app.infra.db.session import SessionLocal

    with SessionLocal() as db:
        run_canonical_db_startup_validation(settings.canonical_db_validation_mode, db)

    yield
    shutdown_scheduler()


app = FastAPI(title="horoscope-backend", version="0.1.0", lifespan=_app_lifespan)
app.add_exception_handler(ApplicationError, application_error_handler)


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
    sanitized_errors = []
    for entry in error.errors():
        sanitized_entry = dict(entry)
        ctx = sanitized_entry.get("ctx")
        if ctx:
            sanitized_entry["ctx"] = {
                key: str(value) if isinstance(value, Exception) else value
                for key, value in ctx.items()
            }
        sanitized_errors.append(sanitized_entry)

    return build_error_response(
        status_code=422,
        request_id=resolve_request_id(request),
        code="invalid_request_payload",
        message="request payload validation failed",
        details={"errors": sanitized_errors},
    )


@app.exception_handler(UserAuthenticationError)
def handle_user_authentication_error(
    request: Request, error: UserAuthenticationError
) -> JSONResponse:
    return build_error_response(
        status_code=error.http_status_code,
        request_id=resolve_request_id(request),
        code=error.code,
        message=error.message,
        details=error.details,
    )


@app.exception_handler(EnterpriseApiKeyAuthenticationError)
def handle_enterprise_api_key_authentication_error(
    request: Request, error: EnterpriseApiKeyAuthenticationError
) -> JSONResponse:
    return build_error_response(
        status_code=error.http_status_code,
        request_id=resolve_request_id(request),
        code=error.code,
        message=error.message,
        details=error.details,
    )


# Restrictive-by-default CORS for local development bootstrap.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

include_api_v1_routers(app)
include_registered_route_exceptions(app)

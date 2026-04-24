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
from app.api.v1.routers.admin.llm.assemblies import router as admin_llm_assembly_router
from app.api.v1.routers.admin.llm.consumption import router as admin_llm_consumption_router
from app.api.v1.routers.admin.llm.prompts import (
    ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER,
    ADMIN_MANUAL_EXECUTE_ROUTE_PATH,
)
from app.api.v1.routers.admin.llm.prompts import (
    router as admin_llm_router,
)
from app.api.v1.routers.admin.llm.releases import router as admin_llm_release_router
from app.api.v1.routers.admin.llm.sample_payloads import (
    router as admin_llm_sample_payloads_router,
)
from app.api.v1.routers.admin_ai import router as admin_ai_router
from app.api.v1.routers.admin_audit import router as admin_audit_router
from app.api.v1.routers.admin_content import router as admin_content_router
from app.api.v1.routers.admin_dashboard import router as admin_dashboard_router
from app.api.v1.routers.admin_entitlements import router as admin_entitlements_router
from app.api.v1.routers.admin_exports import router as admin_exports_router
from app.api.v1.routers.admin_logs import router as admin_logs_router
from app.api.v1.routers.admin_pdf_templates import router as admin_pdf_templates_router
from app.api.v1.routers.admin_support import router as admin_support_router
from app.api.v1.routers.admin_users import router as admin_users_router
from app.api.v1.routers.astrologers import router as astrologers_router
from app.api.v1.routers.astrology_engine import router as astrology_engine_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.b2b_astrology import router as b2b_astrology_router
from app.api.v1.routers.b2b_billing import router as b2b_billing_router
from app.api.v1.routers.b2b_editorial import router as b2b_editorial_router
from app.api.v1.routers.b2b_entitlement_repair import router as b2b_entitlement_repair_router
from app.api.v1.routers.b2b_entitlements_audit import router as b2b_entitlements_audit_router
from app.api.v1.routers.b2b_reconciliation import router as b2b_reconciliation_router
from app.api.v1.routers.b2b_usage import router as b2b_usage_router
from app.api.v1.routers.billing import router as billing_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.consultations import router as consultations_router
from app.api.v1.routers.email import router as email_router
from app.api.v1.routers.enterprise_credentials import router as enterprise_credentials_router
from app.api.v1.routers.entitlements import router as entitlements_router
from app.api.v1.routers.ephemeris import router as ephemeris_router
from app.api.v1.routers.geocoding import router as geocoding_router
from app.api.v1.routers.guidance import router as guidance_router
from app.api.v1.routers.help import router as help_router
from app.api.v1.routers.natal_interpretation import router as natal_interpretation_router
from app.api.v1.routers.ops_entitlement_mutation_audits import (
    router as ops_entitlement_mutation_audits_router,
)
from app.api.v1.routers.ops_feature_flags import router as ops_feature_flags_router
from app.api.v1.routers.ops_monitoring import router as ops_monitoring_router
from app.api.v1.routers.ops_monitoring_llm import router as ops_monitoring_llm_router
from app.api.v1.routers.ops_persona import router as ops_persona_router
from app.api.v1.routers.predictions import router as predictions_router
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
from app.domain.llm.runtime.contracts import InputValidationError
from app.infra.db.bootstrap import ensure_local_sqlite_schema_ready
from app.infra.observability.metrics import increment_counter, observe_duration
from app.services.pricing_experiment_service import PricingExperimentService
from app.startup.canonical_db_validation import run_canonical_db_startup_validation
from app.startup.feature_scope_validation import run_feature_scope_startup_validation
from app.startup.llm_coherence_validation import run_llm_coherence_startup_validation
from app.startup.stripe_portal_validation import run_stripe_portal_startup_validation

logger = logging.getLogger(__name__)


def _include_internal_llm_qa_router(application: FastAPI) -> None:
    if not settings.llm_qa_routes_enabled:
        logger.info("internal_llm_qa_router_disabled")
        return
    if settings.app_env in {"production", "prod"} and not settings.llm_qa_routes_allow_production:
        logger.warning("internal_llm_qa_router_blocked_in_production")
        return

    from app.api.v1.routers.internal.llm.qa import router as internal_llm_qa_router

    application.include_router(internal_llm_qa_router)


def _ensure_llm_registry_seeded() -> None:
    """Legacy-only local reseed guarded by an explicit opt-in flag."""
    logger.info("llm_registry_legacy_seed_disabled")


def _ensure_canonical_llm_bootstrap_seeded() -> None:
    """
    Auto-heal the canonical LLM bootstrap locally when nominal tables are empty.

    This preserves the local non-production startup path after disabling the
    old explicit legacy reseed flag: published prompts/use-cases/personas are
    still created when the database is blank, then canonical assemblies and
    execution profiles are seeded so supported families resolve nominally.
    """
    if settings.app_env in {"production", "prod"}:
        return

    from sqlalchemy.exc import IntegrityError, OperationalError

    from app.domain.llm.configuration.prompt_version_lookup import get_active_prompt_version
    from app.infra.db.models.llm.llm_assembly import PromptAssemblyConfigModel
    from app.infra.db.models.llm.llm_execution_profile import LlmExecutionProfileModel
    from app.infra.db.models.llm.llm_output_schema import LlmOutputSchemaModel
    from app.infra.db.models.llm.llm_persona import LlmPersonaModel
    from app.infra.db.models.llm.llm_prompt import LlmPromptVersionModel
    from app.infra.db.session import SessionLocal
    from app.ops.llm.bootstrap.seed_29_prompts import seed_prompts
    from app.ops.llm.bootstrap.seed_30_8_v3_prompts import seed as seed_natal_v3_prompts
    from app.ops.llm.bootstrap.seed_30_14_chat_prompt import seed as seed_chat_prompt_v2
    from app.ops.llm.bootstrap.seed_66_20_taxonomy import seed_66_20_taxonomy
    from app.ops.llm.bootstrap.seed_guidance_prompts import seed_guidance_prompts
    from app.ops.llm.bootstrap.seed_horoscope_narrator_assembly import (
        seed_horoscope_narrator_assembly,
    )
    from app.ops.llm.bootstrap.use_cases_seed import seed_bootstrap_contracts
    from scripts.seed_astrologers_6_profiles import seed_astrologers

    def collect_state() -> tuple[int, int, int, int, int, bool]:
        with SessionLocal() as db:
            return (
                db.query(LlmOutputSchemaModel).count(),
                db.query(LlmPromptVersionModel).count(),
                db.query(LlmPersonaModel).filter(LlmPersonaModel.enabled == True).count(),  # noqa: E712
                db.query(PromptAssemblyConfigModel).count(),
                db.query(LlmExecutionProfileModel).count(),
                get_active_prompt_version(db, "natal_interpretation_short") is not None,
            )

    try:
        (
            output_schema_count,
            prompt_count,
            enabled_personas,
            assembly_count,
            profile_count,
            has_active_short_prompt,
        ) = collect_state()
    except OperationalError as error:
        is_local_dev = settings.app_env in {"development", "dev", "local"}
        if not is_local_dev or not settings._is_local_sqlite_database_url(settings.database_url):
            raise
        logger.warning("canonical_llm_bootstrap_local_sqlite_repair error=%s", error)
        ensure_local_sqlite_schema_ready()
        (
            output_schema_count,
            prompt_count,
            enabled_personas,
            assembly_count,
            profile_count,
            has_active_short_prompt,
        ) = collect_state()

    needs_registry_seed = (
        output_schema_count == 0
        or prompt_count == 0
        or enabled_personas == 0
        or not has_active_short_prompt
    )
    needs_canonical_seed = assembly_count == 0 or profile_count == 0

    if not needs_registry_seed and not needs_canonical_seed:
        return

    logger.warning(
        (
            "canonical_llm_bootstrap_auto_heal schemas=%s prompts=%s personas=%s "
            "assemblies=%s profiles=%s active_short=%s"
        ),
        output_schema_count,
        prompt_count,
        enabled_personas,
        assembly_count,
        profile_count,
        has_active_short_prompt,
    )

    try:
        if needs_registry_seed:
            with SessionLocal() as db:
                seed_astrologers(db)
                seed_bootstrap_contracts(db)
            seed_prompts()
            seed_natal_v3_prompts()
            seed_chat_prompt_v2()
            seed_guidance_prompts()

        with SessionLocal() as db:
            seed_horoscope_narrator_assembly(db)
            seed_66_20_taxonomy(db)
    except IntegrityError:
        logger.debug("canonical_llm_bootstrap_auto_heal_concurrent_skip")
    except Exception as e:
        logger.error("canonical_llm_bootstrap_auto_heal_failed error=%s", e)


def _ensure_consultation_templates_seeded() -> None:
    """Auto-seed consultation templates when the table is empty (idempotent)."""
    from app.infra.db.models.consultation_template import ConsultationTemplateModel
    from app.infra.db.session import SessionLocal

    try:
        with SessionLocal() as db:
            count = db.query(ConsultationTemplateModel).count()
            if count > 0:
                return
        logger.warning("consultation_templates_auto_seed table is empty, seeding...")
        from scripts.seed_consultation_templates import seed_consultation_templates

        seed_consultation_templates()
    except Exception as e:
        logger.error("consultation_templates_auto_seed_failed error=%s", e)


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
    from app.services.feature_scope_registry import FEATURE_SCOPE_REGISTRY
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
                        description="Acces volumetrique a l API astrologique entreprise",
                        is_metered=True,
                        is_active=True,
                    )
                )
            else:
                feature.feature_name = "B2B API Access"
                feature.description = "Acces volumetrique a l API astrologique entreprise"
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
    _ensure_canonical_entitlements_seeded()
    _ensure_canonical_llm_bootstrap_seeded()
    _ensure_consultation_templates_seeded()
    _ensure_support_categories_seeded()
    from app.startup import seed_dev_admin, seed_llm_qa_user

    await seed_dev_admin()
    await seed_llm_qa_user()

    # Story 61.29: Enforcement du registre de scope au démarrage
    run_feature_scope_startup_validation(settings.feature_scope_validation_mode)

    # Story 61.64: Safeguard for Stripe Customer Portal
    run_stripe_portal_startup_validation(settings)

    from app.infra.db.session import SessionLocal

    with SessionLocal() as db:
        run_canonical_db_startup_validation(settings.canonical_db_validation_mode, db)
        # Story 66.31: Validate LLM configuration coherence at startup
        await run_llm_coherence_startup_validation(settings.llm_coherence_validation_mode, db)

    yield
    shutdown_scheduler()


app = FastAPI(title="horoscope-backend", version="0.1.0", lifespan=_app_lifespan)


@app.middleware("http")
async def llm_simulation_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Story 66.35: capture simulation header for qualification runs."""
    from app.domain.llm.runtime.simulation import simulation_error as simulation_error_ctx

    header_val = request.headers.get("X-LLM-Simulate-Error") or request.headers.get(
        "x-llm-simulate-error"
    )
    token = simulation_error_ctx.set(header_val)
    try:
        response = await call_next(request)
        return response
    finally:
        simulation_error_ctx.reset(token)


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


def _is_post_admin_llm_catalog_execute_sample(request: Request) -> bool:
    """POST execute-sample identifié par le template FastAPI partagé avec le router."""
    return (
        request.method == "POST"
        and _resolve_route_template(request)
        == f"{admin_llm_router.prefix}{ADMIN_MANUAL_EXECUTE_ROUTE_PATH}"
    )


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
    if _is_post_admin_llm_catalog_execute_sample(request):
        response.headers[ADMIN_MANUAL_EXECUTE_RESPONSE_HEADER] = "1"

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

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_request_payload",
                "message": "request payload validation failed",
                "details": {"errors": sanitized_errors},
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


@app.exception_handler(InputValidationError)
def handle_input_validation_error(request: Request, error: InputValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "input_validation_failed",
                "message": error.message,
                "details": error.details,
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
app.include_router(admin_dashboard_router)
app.include_router(admin_entitlements_router)
app.include_router(admin_ai_router)
app.include_router(admin_logs_router)
app.include_router(admin_exports_router)
app.include_router(admin_llm_router)
app.include_router(admin_llm_sample_payloads_router)
app.include_router(admin_llm_consumption_router)
app.include_router(admin_llm_assembly_router)
app.include_router(
    admin_llm_release_router, prefix="/v1/admin/llm/releases", tags=["Admin LLM Releases"]
)
app.include_router(admin_users_router)
app.include_router(admin_support_router)
app.include_router(admin_pdf_templates_router)
app.include_router(admin_audit_router)
app.include_router(admin_content_router)
app.include_router(astrologers_router)
app.include_router(ephemeris_router)
app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(billing_router)
app.include_router(entitlements_router)
app.include_router(astrology_engine_router)
app.include_router(b2b_astrology_router)
app.include_router(b2b_billing_router)
app.include_router(b2b_editorial_router)
app.include_router(b2b_reconciliation_router)
app.include_router(b2b_usage_router)
app.include_router(b2b_entitlement_repair_router)
app.include_router(b2b_entitlements_audit_router)
app.include_router(chat_router)
app.include_router(consultations_router, prefix="/v1/consultations", tags=["Consultations"])
app.include_router(geocoding_router)
app.include_router(enterprise_credentials_router)
app.include_router(guidance_router)
app.include_router(natal_interpretation_router)
app.include_router(ops_monitoring_router)
app.include_router(ops_monitoring_llm_router)
app.include_router(ops_feature_flags_router)
app.include_router(ops_persona_router)
app.include_router(ops_entitlement_mutation_audits_router)
app.include_router(predictions_router)
app.include_router(privacy_router)
app.include_router(reference_data_router)
app.include_router(users_router)
app.include_router(support_router)
app.include_router(ai_engine_router)
app.include_router(help_router)
app.include_router(email_router, prefix="/api", tags=["email"])
_include_internal_llm_qa_router(app)

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.routers.users import ErrorEnvelope
from app.api.v1.schemas.natal_interpretation import (
    NatalChartLongEntitlementInfo,
    NatalInterpretationListResponse,
    NatalInterpretationRequest,
    NatalInterpretationResponse,
    NatalPdfTemplateListResponse,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.domain.llm.runtime.adapter import AIEngineAdapterError
from app.domain.llm.runtime.contracts import (
    GatewayConfigError,
    InputValidationError,
    OutputValidationError,
    UnknownUseCaseError,
)
from app.domain.llm.runtime.errors import (
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.infra.db.models.pdf_template import PdfTemplateModel, PdfTemplateStatus
from app.infra.db.session import get_db_session
from app.services.disclaimer_registry import get_disclaimers
from app.services.llm_generation.natal_interpretation_service_v2 import NatalInterpretationServiceV2
from app.services.natal_chart_long_entitlement_gate import (
    NatalChartLongAccessDeniedError,
    NatalChartLongEntitlementGate,
    NatalChartLongEntitlementResult,
    NatalChartLongQuotaExceededError,
)
from app.services.user_birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_natal_chart_service import UserNatalChartService, UserNatalChartServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/natal", tags=["natal-interpretation"])


def _create_error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "details": details or {},
            }
        },
    )


def _build_natal_entitlement_info(
    result: NatalChartLongEntitlementResult,
) -> NatalChartLongEntitlementInfo:
    if result.usage_states:
        state = result.usage_states[0]
        return NatalChartLongEntitlementInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,  # None pour lifetime
            variant_code=result.variant_code,
        )
    return NatalChartLongEntitlementInfo(variant_code=result.variant_code)


@router.post(
    "/interpretation",
    response_model=NatalInterpretationResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        501: {"model": ErrorEnvelope},
        502: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        504: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)
async def interpret_natal_chart(
    request: Request,
    body: NatalInterpretationRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    trace_id = request_id
    current_step = "init"
    debug_errors_enabled = request.headers.get("x-debug-errors") == "1"

    # Gate entitlement — uniquement pour use_case_level="complete" (natal_chart_long)
    entitlement_info: NatalChartLongEntitlementInfo | None = None
    variant_code: str | None = None
    if body.use_case_level == "complete":
        try:
            entitlement_result = NatalChartLongEntitlementGate.check_and_consume(
                db, user_id=current_user.id
            )
            entitlement_info = _build_natal_entitlement_info(entitlement_result)
            variant_code = entitlement_result.variant_code
        except NatalChartLongQuotaExceededError as error:
            db.rollback()
            return _create_error_response(
                status_code=429,
                code="natal_chart_long_quota_exceeded",
                message="quota d'interprétations complètes du thème natal épuisé",
                request_id=request_id,
                details={
                    "quota_key": error.quota_key,
                    "used": error.used,
                    "limit": error.limit,
                    "reason_code": "quota_exhausted",
                    "window_end": error.window_end.isoformat() if error.window_end else None,
                },
            )
        except NatalChartLongAccessDeniedError as error:
            db.rollback()
            return _create_error_response(
                status_code=403,
                code="natal_chart_long_access_denied",
                message="accès à l'interprétation complète du thème natal refusé",
                request_id=request_id,
                details={
                    "reason": error.reason,
                    "reason_code": error.reason_code,
                    "billing_status": error.billing_status,
                },
            )

    try:
        # Step A: Load last natal chart and profile
        current_step = "load_chart_and_profile"
        try:
            chart = UserNatalChartService.get_latest_for_user(db, current_user.id)
            profile = UserBirthProfileService.get_for_user(db, current_user.id)
        except (UserNatalChartServiceError, UserBirthProfileServiceError) as e:
            db.rollback()
            if e.code == "natal_chart_not_found" or e.code == "birth_profile_not_found":
                return _create_error_response(
                    status_code=404,
                    code="natal_chart_not_found",
                    message="No natal chart found for this user. Please generate one first.",
                    request_id=request_id,
                )
            raise

        # Step B to F: Orchestration via Service V2
        current_step = "service_interpret"
        response = await NatalInterpretationServiceV2.interpret(
            db=db,
            user_id=current_user.id,
            chart_id=chart.chart_id,
            natal_result=chart.result,
            birth_profile=profile,
            level=body.use_case_level,
            persona_id=body.persona_id,
            locale=body.locale,
            question=body.question,
            request_id=request_id,
            trace_id=trace_id,
            force_refresh=body.force_refresh,
            module=body.module,
            variant_code=variant_code,
        )

        current_step = "apply_disclaimers"
        response.disclaimers = get_disclaimers(body.locale)
        response.entitlement_info = entitlement_info

        # Persist quota consumption and interpretation
        db.commit()

        current_step = "return_response"
        return response

    except AIEngineAdapterError as e:
        db.rollback()
        # Map internal codes to status codes
        code = e.code or "interpretation_failed"
        status_code = 500
        if "unknown_use_case" in code or "not configured" in str(e).lower():
            status_code = 404
            code = "unknown_use_case"
        elif "timeout" in code or "timeout" in str(e).lower():
            status_code = 504
            code = "llm_upstream_timeout"
        elif "rate_limit" in code:
            status_code = 429
            code = "llm_rate_limit"
        elif "config" in code:
            status_code = 500
            code = "gateway_config_error"

        return _create_error_response(status_code, code, str(e), request_id)
    except UnknownUseCaseError as e:
        db.rollback()
        logger.error(f"Unknown use case error: {e}")
        return _create_error_response(404, "unknown_use_case", str(e), request_id)
    except GatewayConfigError as e:
        db.rollback()
        logger.error(f"Gateway configuration error: {e}")
        code = "gateway_config_error"
        if e.error_code:
            code = e.error_code
        return _create_error_response(500, code, str(e), request_id)
    except InputValidationError as e:
        db.rollback()
        # Note: Local catch here to ensure 422 response for natal interpretation,
        # overriding the global 400 handler in main.py.
        return _create_error_response(422, "natal_input_invalid", str(e), request_id)
    except OutputValidationError:
        db.rollback()
        return _create_error_response(
            502, "interpretation_failed", "Failed to generate a valid interpretation.", request_id
        )
    except RuntimeError as e:
        db.rollback()
        if "no structured output" in str(e) or "empty complete interpretation" in str(e):
            return _create_error_response(502, "interpretation_failed", str(e), request_id)
        raise
    except UpstreamRateLimitError:
        db.rollback()
        return _create_error_response(
            429, "llm_rate_limit", "Upstream rate limit reached.", request_id
        )
    except UpstreamTimeoutError:
        db.rollback()
        return _create_error_response(
            504, "llm_upstream_timeout", "Upstream request timed out.", request_id
        )
    except UpstreamError:
        db.rollback()
        return _create_error_response(
            503, "llm_upstream_error", "LLM provider is currently unavailable.", request_id
        )
    except Exception as e:
        db.rollback()
        logger.exception(
            "Unexpected error during natal interpretation request_id=%s step=%s error=%s",
            request_id,
            current_step,
            e,
        )
        details: dict[str, Any] = {"step": current_step}
        if settings.app_env in {"development", "dev", "local", "test", "testing"} or (
            debug_errors_enabled
        ):
            details = {
                "step": current_step,
                "exception_type": type(e).__name__,
                "exception_message": str(e),
            }
        return _create_error_response(
            500, "internal_error", "An unexpected error occurred.", request_id, details=details
        )


@router.get(
    "/pdf-templates",
    response_model=NatalPdfTemplateListResponse,
    responses={
        401: {"model": ErrorEnvelope},
    },
)
async def list_natal_pdf_templates(
    request: Request,
    locale: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        stmt = select(PdfTemplateModel).where(PdfTemplateModel.status == PdfTemplateStatus.ACTIVE)
        if locale:
            stmt = stmt.where(PdfTemplateModel.locale == locale)
        stmt = stmt.order_by(PdfTemplateModel.is_default.desc(), PdfTemplateModel.key.asc())
        templates = db.execute(stmt).scalars().all()
        logger.info(
            "Listed active natal PDF templates user_id=%s locale=%s count=%s",
            current_user.id,
            locale,
            len(templates),
        )
        return {
            "items": [
                {
                    "key": item.key,
                    "name": item.name,
                    "description": item.description,
                    "locale": item.locale,
                    "is_default": item.is_default,
                }
                for item in templates
            ]
        }
    except Exception as e:
        logger.exception("Error listing natal PDF templates request_id=%s error=%s", request_id, e)
        return _create_error_response(
            500, "internal_error", "Failed to list PDF templates", request_id
        )


@router.get(
    "/interpretations",
    response_model=NatalInterpretationListResponse,
    responses={
        401: {"model": ErrorEnvelope},
    },
)
async def list_natal_interpretations(
    request: Request,
    chart_id: Optional[str] = None,
    level: Optional[Literal["short", "complete"]] = None,
    persona_id: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()
    try:
        items, total = NatalInterpretationServiceV2.list_interpretations(
            db=db,
            user_id=current_user.id,
            chart_id=chart_id,
            level=level,
            persona_id=persona_id,
            module=module,
            limit=limit,
            offset=offset,
        )

        observe_duration("natal_interpretations_list_latency", (monotonic() - start_time) * 1000)
        logger.info(
            "Listed natal interpretations user_id=%s chart_id=%s count=%s total=%s",
            current_user.id,
            chart_id,
            len(items),
            total,
        )

        return {
            "items": [
                {
                    "id": item.id,
                    "chart_id": item.chart_id,
                    "level": item.level.value,
                    "persona_id": str(item.persona_id) if item.persona_id else None,
                    "persona_name": item.persona_name,
                    "module": (
                        item.use_case
                        if item.use_case.startswith("natal_")
                        and item.use_case
                        not in {"natal_interpretation", "natal_interpretation_short"}
                        else None
                    ),
                    "created_at": item.created_at,
                    "use_case": item.use_case,
                    "prompt_version_id": str(item.prompt_version_id)
                    if item.prompt_version_id
                    else None,
                    "was_fallback": item.was_fallback,
                }
                for item in items
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.exception(f"Error listing interpretations: {e}")
        return _create_error_response(
            500, "internal_error", "Failed to list interpretations", request_id
        )


@router.get(
    "/interpretations/{interpretation_id}",
    response_model=NatalInterpretationResponse,
    responses={
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
async def get_natal_interpretation(
    request: Request,
    interpretation_id: int,
    locale: str = "fr-FR",
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    item = NatalInterpretationServiceV2.get_interpretation_by_id(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
    )
    if not item:
        return _create_error_response(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    from app.api.v1.schemas.natal_interpretation import InterpretationMeta
    from app.infra.db.models.user_natal_interpretation import InterpretationLevel

    meta = InterpretationMeta(
        level="short" if item.level == InterpretationLevel.SHORT else "complete",
        use_case=item.use_case,
        persona_id=str(item.persona_id) if item.persona_id else None,
        persona_name=item.persona_name,
        prompt_version_id=str(item.prompt_version_id) if item.prompt_version_id else None,
        schema_version="unknown",
        validation_status="valid",
        was_fallback=item.was_fallback,
        request_id=request_id,
        cached=True,
        persisted_at=item.created_at,
    )

    result = NatalInterpretationServiceV2.format_interpretation_response(item, meta, locale)
    observe_duration("natal_interpretation_get_latency", (monotonic() - start_time) * 1000)
    logger.info(
        "Fetched natal interpretation user_id=%s id=%s chart_id=%s",
        current_user.id,
        interpretation_id,
        item.chart_id,
    )
    return result


@router.delete(
    "/interpretations/{interpretation_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
)
async def delete_natal_interpretation(
    request: Request,
    interpretation_id: int,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    success = NatalInterpretationServiceV2.delete_interpretation(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
        request_id=request_id,
        actor_role=current_user.role,
    )
    if not success:
        logger.warning(
            "Failed to delete interpretation user_id=%s id=%s (not found or denied)",
            current_user.id,
            interpretation_id,
        )
        return _create_error_response(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    observe_duration("natal_interpretation_delete_latency", (monotonic() - start_time) * 1000)
    logger.info(
        "Deleted natal interpretation user_id=%s id=%s request_id=%s",
        current_user.id,
        interpretation_id,
        request_id,
    )
    return Response(status_code=204)


@router.get(
    "/interpretations/{interpretation_id}/pdf",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "The generated PDF file",
        },
        401: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
    },
)
async def download_natal_interpretation_pdf(
    request: Request,
    interpretation_id: int,
    template_key: Optional[str] = None,
    locale: str = "fr-FR",
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    from time import monotonic

    from app.infra.observability.metrics import observe_duration

    start_time = monotonic()

    item = NatalInterpretationServiceV2.get_interpretation_by_id(
        db=db,
        user_id=current_user.id,
        interpretation_id=interpretation_id,
    )
    if not item:
        return _create_error_response(
            404, "interpretation_not_found", "Interpretation not found or access denied", request_id
        )

    try:
        from app.services.natal_pdf_export_service import NatalPdfExportService

        pdf_bytes = NatalPdfExportService.generate_pdf(
            db=db,
            interpretation=item,
            template_key=template_key,
            locale=locale,
        )

        filename = f"natal-{item.chart_id}-{item.created_at.strftime('%Y%m%d')}.pdf"

        observe_duration("natal_pdf_export_latency", (monotonic() - start_time) * 1000)
        logger.info(
            "Exported natal PDF user_id=%s id=%s chart_id=%s template=%s size=%s",
            current_user.id,
            interpretation_id,
            item.chart_id,
            template_key,
            len(pdf_bytes),
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        return _create_error_response(
            500, "pdf_generation_failed", "Failed to generate PDF", request_id
        )

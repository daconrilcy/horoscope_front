from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.ai_engine.exceptions import (
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)
from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.routers.users import ErrorEnvelope
from app.api.v1.schemas.natal_interpretation import (
    NatalInterpretationRequest,
    NatalInterpretationResponse,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.llm_orchestration.models import (
    GatewayConfigError,
    InputValidationError,
    OutputValidationError,
    UnknownUseCaseError,
)
from app.services.disclaimer_registry import get_disclaimers
from app.services.natal_interpretation_service_v2 import NatalInterpretationServiceV2
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


@router.post(
    "/interpretation",
    response_model=NatalInterpretationResponse,
    responses={
        401: {"model": ErrorEnvelope},
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

    # AC7 — Feature flag check
    if not getattr(settings, "llm_orchestration_v2", False):
        return _create_error_response(
            status_code=501,
            code="feature_disabled",
            message="LLM Orchestration V2 is not enabled.",
            request_id=request_id,
        )

    try:
        # Step A: Load last natal chart and profile
        try:
            chart = UserNatalChartService.get_latest_for_user(db, current_user.id)
            profile = UserBirthProfileService.get_for_user(db, current_user.id)
        except (UserNatalChartServiceError, UserBirthProfileServiceError) as e:
            if e.code == "natal_chart_not_found" or e.code == "birth_profile_not_found":
                return _create_error_response(
                    status_code=404,
                    code="natal_chart_not_found",
                    message="No natal chart found for this user. Please generate one first.",
                    request_id=request_id,
                )
            raise

        # Step B to F: Orchestration via Service V2
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
        )

        response.disclaimers = get_disclaimers(body.locale)
        return response

    except UnknownUseCaseError as e:
        logger.error(f"Unknown use case error: {e}")
        return _create_error_response(404, "unknown_use_case", str(e), request_id)
    except GatewayConfigError as e:
        logger.error(f"Gateway configuration error: {e}")
        return _create_error_response(500, "gateway_config_error", str(e), request_id)
    except InputValidationError as e:
        # Note: Local catch here to ensure 422 response for natal interpretation,
        # overriding the global 400 handler in main.py.
        return _create_error_response(422, "natal_input_invalid", str(e), request_id)
    except OutputValidationError:
        return _create_error_response(
            502, "interpretation_failed", "Failed to generate a valid interpretation.", request_id
        )
    except RuntimeError as e:
        if "no structured output" in str(e):
            return _create_error_response(502, "interpretation_failed", str(e), request_id)
        raise
    except UpstreamRateLimitError:
        return _create_error_response(
            429, "llm_rate_limit", "Upstream rate limit reached.", request_id
        )
    except UpstreamTimeoutError:
        return _create_error_response(
            504, "llm_upstream_timeout", "Upstream request timed out.", request_id
        )
    except UpstreamError:
        return _create_error_response(
            503, "llm_upstream_error", "LLM provider is currently unavailable.", request_id
        )
    except Exception as e:
        logger.exception(f"Unexpected error during natal interpretation: {e}")
        return _create_error_response(
            500, "internal_error", "An unexpected error occurred.", request_id
        )

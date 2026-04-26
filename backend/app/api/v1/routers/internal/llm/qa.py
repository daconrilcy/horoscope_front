"""Routeur interne QA pour executer les parcours de generation LLM canoniques."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_ops_user
from app.api.v1.routers.predictions import (
    _extract_llm_narrative_payload,
    _raise_daily_prediction_service_error,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_reference_repository import PredictionReferenceRepository
from app.infra.db.repositories.user_repository import UserRepository
from app.infra.db.session import get_db_session
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.public_projection import PublicPredictionAssembler
from app.services.daily_prediction_service import DailyPredictionService
from app.services.entitlement.horoscope_daily_entitlement_gate import (
    HoroscopeDailyAccessDeniedError,
    HoroscopeDailyEntitlementGate,
)
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatGuidanceService,
    ChatGuidanceServiceError,
)
from app.services.llm_generation.guidance.guidance_service import (
    GuidanceService,
    GuidanceServiceError,
)
from app.services.llm_generation.natal.interpretation_service import NatalInterpretationService
from app.services.llm_generation.qa_seed_service import (
    LLM_QA_TEST_USER_EMAIL,
    LlmQaSeedResult,
    LlmQaSeedService,
)
from app.services.prediction.types import ComputeMode, DailyPredictionServiceError
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileService,
    UserBirthProfileServiceError,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartService,
    UserNatalChartServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/internal/llm/qa", tags=["internal-llm-qa"])


class ResponseMeta(BaseModel):
    request_id: str
    target_user_email: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class SeedUserResponse(BaseModel):
    user_id: int
    email: str
    birth_place_resolved_id: int
    birth_timezone: str
    chart_id: str
    chart_reused: bool


class GuidanceQaRequest(BaseModel):
    period: Literal["daily", "weekly"] = "daily"
    target_email: str | None = None
    conversation_id: int | None = None


class ChatQaRequest(BaseModel):
    message: str = Field(min_length=1)
    target_email: str | None = None
    conversation_id: int | None = None
    persona_id: str | None = None
    client_message_id: str | None = None


class NatalQaRequest(BaseModel):
    target_email: str | None = None
    use_case_level: Literal["short", "complete"] = "complete"
    locale: str = "fr"
    question: str | None = None
    persona_id: str | None = None
    force_refresh: bool = False
    module: str | None = None


class DailyQaRequest(BaseModel):
    target_email: str | None = None
    date: str | None = None


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "request_id": request_id,
            }
        },
    )


def _seed_result_to_response(result: LlmQaSeedResult) -> SeedUserResponse:
    return SeedUserResponse(
        user_id=result.user_id,
        email=result.email,
        birth_place_resolved_id=result.birth_place_resolved_id,
        birth_timezone=result.birth_timezone,
        chart_id=result.chart_id,
        chart_reused=result.chart_reused,
    )


def _resolve_target_user(db: Session, *, requested_email: str | None) -> UserModel:
    normalized_email = (requested_email or LLM_QA_TEST_USER_EMAIL).strip().lower()
    if normalized_email == LLM_QA_TEST_USER_EMAIL:
        seeded = LlmQaSeedService.ensure_canonical_test_user(db)
        user = UserRepository(db).get_by_id(seeded.user_id)
    else:
        user = UserRepository(db).get_by_email(normalized_email)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "qa_target_user_not_found",
                "message": "target user was not found",
                "details": {"target_email": normalized_email},
            },
        )
    return user


def _map_guidance_error(error: GuidanceServiceError) -> int:
    if error.code in {"llm_timeout", "llm_unavailable"}:
        return 503
    if error.code in {"conversation_not_found", "missing_birth_profile"}:
        return 404
    if error.code == "conversation_forbidden":
        return 403
    return 422


def _map_chat_error(error: ChatGuidanceServiceError) -> int:
    if error.code in {"llm_timeout", "llm_unavailable"}:
        return 503
    if error.code == "conversation_not_found":
        return 404
    if error.code == "conversation_forbidden":
        return 403
    return 422


def _map_natal_error(request_id: str, error: Exception) -> JSONResponse:
    if isinstance(error, UserNatalChartServiceError):
        return _error_response(
            status_code=404 if error.code == "natal_chart_not_found" else 422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    if isinstance(error, UserBirthProfileServiceError):
        return _error_response(
            status_code=404 if error.code == "birth_profile_not_found" else 422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    logger.exception("llm_qa_natal_unexpected_error")
    return _error_response(
        status_code=500,
        request_id=request_id,
        code="internal_error",
        message="unexpected natal qa error",
    )


@router.post(
    "/seed-user",
    response_model=dict[str, Any],
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
def seed_canonical_user(
    request: Request,
    _: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    try:
        seeded = LlmQaSeedService.ensure_canonical_test_user(db)
    except Exception as error:
        db.rollback()
        if hasattr(error, "code") and hasattr(error, "message"):
            return _error_response(
                status_code=403 if getattr(error, "code", "") == "llm_qa_seed_not_allowed" else 422,
                request_id=request_id,
                code=error.code,
                message=error.message,
                details=getattr(error, "details", {}),
            )
        logger.exception("llm_qa_seed_unexpected_error")
        return _error_response(
            status_code=500,
            request_id=request_id,
            code="internal_error",
            message="unexpected qa seed error",
        )

    return {
        "data": _seed_result_to_response(seeded).model_dump(mode="json"),
        "meta": {"request_id": request_id, "target_user_email": seeded.email},
    }


@router.post(
    "/guidance",
    response_model=dict[str, Any],
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
async def run_guidance_generation(
    request: Request,
    payload: GuidanceQaRequest = Body(default_factory=GuidanceQaRequest),
    _: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    try:
        target_user = _resolve_target_user(db, requested_email=payload.target_email)
        response = await GuidanceService.request_guidance_async(
            db,
            user_id=target_user.id,
            period=payload.period,
            conversation_id=payload.conversation_id,
            request_id=request_id,
        )
    except GuidanceServiceError as error:
        db.rollback()
        return _error_response(
            status_code=_map_guidance_error(error),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except HTTPException as error:
        db.rollback()
        detail = error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=detail.get("code", "qa_target_user_not_found"),
            message=detail.get("message", "target user was not found"),
            details=detail.get("details", {}),
        )

    return {
        "data": response.model_dump(mode="json"),
        "meta": {"request_id": request_id, "target_user_email": target_user.email},
    }


@router.post(
    "/chat",
    response_model=dict[str, Any],
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
async def run_chat_generation(
    request: Request,
    payload: ChatQaRequest,
    _: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    try:
        target_user = _resolve_target_user(db, requested_email=payload.target_email)
        response = await ChatGuidanceService.send_message_async(
            db,
            user_id=target_user.id,
            message=payload.message,
            conversation_id=payload.conversation_id,
            request_id=request_id,
            persona_id=payload.persona_id,
            client_message_id=payload.client_message_id,
            entitlement_result=None,
        )
        db.commit()
    except ChatGuidanceServiceError as error:
        db.rollback()
        return _error_response(
            status_code=_map_chat_error(error),
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except HTTPException as error:
        db.rollback()
        detail = error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=detail.get("code", "qa_target_user_not_found"),
            message=detail.get("message", "target user was not found"),
            details=detail.get("details", {}),
        )

    return {
        "data": response.model_dump(mode="json"),
        "meta": {"request_id": request_id, "target_user_email": target_user.email},
    }


@router.post(
    "/natal",
    response_model=dict[str, Any],
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
async def run_natal_generation(
    request: Request,
    payload: NatalQaRequest = Body(default_factory=NatalQaRequest),
    _: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    try:
        target_user = _resolve_target_user(db, requested_email=payload.target_email)
        chart = UserNatalChartService.get_latest_for_user(db, target_user.id)
        profile = UserBirthProfileService.get_for_user(db, target_user.id)
        response = await NatalInterpretationService.interpret(
            db=db,
            user_id=target_user.id,
            chart_id=chart.chart_id,
            natal_result=chart.result,
            birth_profile=profile,
            level=payload.use_case_level,
            persona_id=payload.persona_id,
            locale=payload.locale,
            question=payload.question,
            request_id=request_id,
            trace_id=request_id,
            force_refresh=payload.force_refresh,
            module=payload.module,
            variant_code=None,
        )
        db.commit()
    except HTTPException as error:
        db.rollback()
        detail = error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=detail.get("code", "qa_target_user_not_found"),
            message=detail.get("message", "target user was not found"),
            details=detail.get("details", {}),
        )
    except Exception as error:
        db.rollback()
        return _map_natal_error(request_id, error)

    return {
        "data": response.model_dump(mode="json"),
        "meta": {"request_id": request_id, "target_user_email": target_user.email},
    }


@router.post(
    "/horoscope-daily",
    response_model=dict[str, Any],
    responses={401: {"model": ErrorEnvelope}, 403: {"model": ErrorEnvelope}},
)
async def run_horoscope_daily_generation(
    request: Request,
    payload: DailyQaRequest = Body(default_factory=DailyQaRequest),
    _: AuthenticatedUser = Depends(require_ops_user),
    db: Session = Depends(get_db_session),
) -> dict[str, Any] | JSONResponse:
    request_id = resolve_request_id(request)
    try:
        target_user = _resolve_target_user(db, requested_email=payload.target_email)
        target_date = None
        if payload.date:
            target_date = datetime.strptime(payload.date, "%Y-%m-%d").date()

        try:
            variant_code = HoroscopeDailyEntitlementGate.check_and_get_variant(
                db, user_id=target_user.id
            ).variant_code
        except HoroscopeDailyAccessDeniedError as error:
            return _error_response(
                status_code=403,
                request_id=request_id,
                code=error.reason_code,
                message=str(error),
                details={
                    "billing_status": error.billing_status,
                    "plan_code": error.plan_code,
                },
            )

        service = DailyPredictionService(
            context_loader=PredictionContextLoader(),
            persistence_service=PredictionPersistenceService(),
        )
        result = service.get_or_compute(
            user_id=target_user.id,
            db=db,
            date_local=target_date,
            mode=ComputeMode.compute_if_missing,
            ruleset_version=settings.ruleset_version,
        )
        if result is None:
            return _error_response(
                status_code=404,
                request_id=request_id,
                code="prediction_not_found",
                message="prediction not found",
            )
        if not result.was_reused:
            db.commit()

        snapshot = result.run
        if not isinstance(snapshot, PersistedPredictionSnapshot):
            reloaded_snapshot = DailyPredictionRepository(db).get_full_run(result.run.run_id)
            if reloaded_snapshot is None:
                return _error_response(
                    status_code=404,
                    request_id=request_id,
                    code="prediction_not_found",
                    message="prediction not found",
                )
            snapshot = reloaded_snapshot

        ref_repo = PredictionReferenceRepository(db)
        categories_data = ref_repo.get_categories(snapshot.reference_version_id)
        cat_id_to_code = {item.id: item.code for item in categories_data}

        reference_version = settings.active_reference_version
        version_model = db.get(ReferenceVersionModel, snapshot.reference_version_id)
        if version_model is not None:
            reference_version = version_model.version

        prompt_context = None
        if settings.llm_narrator_enabled:
            from app.domain.llm.prompting.context import CommonContextBuilder

            try:
                prompt_context = CommonContextBuilder.build(
                    user_id=target_user.id,
                    use_case_key="horoscope_daily",
                    period="daily",
                    db=db,
                )
            except Exception:
                logger.warning("llm_qa_daily_prompt_context_failed", exc_info=True)

        assembled = await PublicPredictionAssembler().assemble(
            snapshot=snapshot,
            cat_id_to_code=cat_id_to_code,
            db=db,
            engine_output=result.bundle,
            was_reused=result.was_reused,
            reference_version=reference_version,
            ruleset_version=settings.ruleset_version,
            astrologer_profile_key=target_user.astrologer_profile or "standard",
            lang="fr",
            prompt_context=prompt_context,
            variant_code=variant_code,
        )

        if settings.llm_narrator_enabled and not getattr(snapshot, "llm_narrative", None):
            llm_payload = _extract_llm_narrative_payload(assembled)
            if llm_payload is not None:
                try:
                    DailyPredictionRepository(db).update_llm_narrative(snapshot.run_id, llm_payload)
                    db.commit()
                except Exception:
                    db.rollback()
                    logger.warning("llm_qa_daily_llm_payload_persist_failed", exc_info=True)
    except DailyPredictionServiceError as error:
        db.rollback()
        try:
            _raise_daily_prediction_service_error(error, not_found_codes={"natal_missing"})
        except HTTPException as http_error:
            detail = http_error.detail if isinstance(http_error.detail, dict) else {}
            return _error_response(
                status_code=http_error.status_code,
                request_id=request_id,
                code=detail.get("code", error.code),
                message=detail.get("message", error.message),
                details=detail.get("details", {}),
            )
        raise
    except HTTPException as error:
        db.rollback()
        detail = error.detail if isinstance(error.detail, dict) else {"message": str(error.detail)}
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=detail.get("code", "qa_target_user_not_found"),
            message=detail.get("message", "target user was not found"),
            details=detail.get("details", {}),
        )
    except ValueError:
        db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_date",
            message="invalid date value, expected YYYY-MM-DD",
        )

    return {
        "data": assembled,
        "meta": {"request_id": request_id, "target_user_email": target_user.email},
    }

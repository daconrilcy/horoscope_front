"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.api.v1.errors import api_error_response
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.user_repository import UserRepository
from app.services.llm_generation.chat.chat_guidance_service import (
    ChatGuidanceServiceError,
)
from app.services.llm_generation.guidance.guidance_service import (
    GuidanceServiceError,
)
from app.services.llm_generation.qa_seed_service import (
    LLM_QA_TEST_USER_EMAIL,
    LlmQaSeedResult,
    LlmQaSeedService,
)
from app.services.user_profile.birth_profile_service import (
    UserBirthProfileServiceError,
)
from app.services.user_profile.natal_chart_service import (
    UserNatalChartServiceError,
)

logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.internal.llm.qa import SeedUserResponse


class QATargetUserNotFoundError(Exception):
    """Signale qu'un utilisateur cible de QA LLM est introuvable."""

    def __init__(self, *, target_email: str) -> None:
        super().__init__("target user was not found")
        self.target_email = target_email


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> Any:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
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
        raise QATargetUserNotFoundError(target_email=normalized_email)
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


def _map_natal_error(request_id: str, error: Exception) -> Any:
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

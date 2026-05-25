"""Routes admin protégées pour la revue des réponses narratives rejetées."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_admin_user
from app.api.errors import raise_api_error
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.api_contracts.admin.audit import (
    RejectedAnswerReviewDetailResponse,
    RejectedAnswerReviewListResponse,
    RejectedAnswerReviewStatus,
    RejectedAnswerReviewUpdateRequest,
)
from app.services.ops.rejected_answer_review import (
    RejectedAnswerReviewInvalidStatusError,
    RejectedAnswerReviewNotFoundError,
    RejectedAnswerReviewService,
    RejectedAnswerReviewUnavailableError,
)

router = APIRouter(prefix="/v1/admin/answer-audits", tags=["admin-answer-audit"])


@router.get("/rejected", response_model=RejectedAnswerReviewListResponse)
def list_rejected_answers(
    request: Request,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    review_status: RejectedAnswerReviewStatus | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Liste les réponses rejetées accessibles au workflow de revue admin."""
    _ = current_user
    try:
        result = RejectedAnswerReviewService.list_rejected_answers(
            db,
            page=page,
            per_page=per_page,
            review_status=review_status,
            request_id=resolve_request_id(request),
            current_user=current_user,
        )
    except RejectedAnswerReviewUnavailableError as error:
        raise_api_error(
            status_code=503,
            message="Rejected answer review store unavailable",
            details={"cause": error.__class__.__name__},
        )

    return {
        "data": result.items,
        "total": result.total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/rejected/{answer_id}", response_model=RejectedAnswerReviewDetailResponse)
def get_rejected_answer_detail(
    answer_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Any:
    """Consulte le détail protégé d'une réponse rejetée et journalise l'accès."""
    try:
        return RejectedAnswerReviewService.get_rejected_answer_detail(
            db,
            answer_id=answer_id,
            request_id=resolve_request_id(request),
            current_user=current_user,
        )
    except RejectedAnswerReviewNotFoundError as error:
        raise_api_error(
            status_code=404,
            message="Rejected answer audit record not found",
            details={"answer_id": str(error)},
        )


@router.patch("/rejected/{answer_id}/review", status_code=status.HTTP_204_NO_CONTENT)
def update_rejected_answer_review_status(
    answer_id: str,
    payload: RejectedAnswerReviewUpdateRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_admin_user),
    db: Session = Depends(get_db_session),
) -> Response:
    """Met à jour le statut interne de revue sans publier la réponse rejetée."""
    try:
        RejectedAnswerReviewService.update_review_status(
            db,
            answer_id=answer_id,
            review_status=payload.review_status,
            review_note=payload.review_note,
            request_id=resolve_request_id(request),
            current_user=current_user,
        )
    except RejectedAnswerReviewNotFoundError as error:
        raise_api_error(
            status_code=404,
            message="Rejected answer audit record not found",
            details={"answer_id": str(error)},
        )
    except RejectedAnswerReviewInvalidStatusError as error:
        raise_api_error(
            status_code=400,
            message="Invalid rejected answer review status",
            details={"review_status": str(error)},
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

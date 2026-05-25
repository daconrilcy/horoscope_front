"""Service de revue admin des réponses narratives rejetées via le journal d'audit."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, get_args

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.infra.db.models.audit_event import AuditEventModel
from app.services.api_contracts.admin.audit import (
    RejectedAnswerReviewAuditEvent,
    RejectedAnswerReviewDetailResponse,
    RejectedAnswerReviewItem,
    RejectedAnswerReviewStatus,
)
from app.services.ops.audit_service import AuditEventCreatePayload, AuditEventData, AuditService

CONTRACT_ID = "admin_answer_audit_v1"
REJECTED_STATUS = "rejected"
REJECTED_ANSWER_ACTIONS = ("narrative_answer_rejected", "admin_rejected_answer_recorded")
REVIEW_ACCESSED_ACTION = "admin_rejected_answer_review_accessed"
REVIEWED_ACTION = "admin_rejected_answer_reviewed"
REVIEW_TARGET_TYPE = "rejected_answer_review"
DEFAULT_REVIEW_STATUS: RejectedAnswerReviewStatus = "pending_review"
ALLOWED_REVIEW_STATUSES = set(get_args(RejectedAnswerReviewStatus))
MANUAL_CORRECTION_LIMITS = [
    "diagnostic_only_no_client_delivery",
    "prompt_changes_require_dedicated_story",
    "contract_changes_require_validation_review",
    "validation_followup_must_not_replay_rejected_answer",
]


class RejectedAnswerReviewNotFoundError(Exception):
    """Erreur levée quand aucune réponse rejetée ne correspond à l'identifiant."""


class RejectedAnswerReviewUnavailableError(Exception):
    """Erreur levée quand le journal d'audit ne peut pas alimenter la revue."""


class RejectedAnswerReviewInvalidStatusError(Exception):
    """Erreur levée quand un statut de revue ne respecte pas le contrat."""


@dataclass(frozen=True)
class RejectedAnswerReviewListResult:
    """Résultat paginé interne pour la liste de revue admin."""

    items: list[RejectedAnswerReviewItem]
    total: int


def _as_string(value: object, *, default: str = "unknown") -> str:
    """Convertit une valeur d'audit en chaîne bornée pour le contrat admin."""
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _as_missing_evidence_refs(value: object) -> list[str]:
    """Normalise les preuves manquantes sans exposer de payload brut."""
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _as_rejection_reason(details: dict[str, object]) -> dict[str, object]:
    """Construit la raison structurée de rejet attendue par le contrat."""
    reason = details.get("rejection_reason")
    if isinstance(reason, dict):
        return reason
    return {"code": _as_string(reason, default="unknown_rejection_reason")}


def _as_review_status(value: object) -> RejectedAnswerReviewStatus:
    """Normalise un statut de revue persistant vers une valeur contractuelle."""
    status = _as_string(value, default=DEFAULT_REVIEW_STATUS)
    if status not in ALLOWED_REVIEW_STATUSES:
        return DEFAULT_REVIEW_STATUS
    return status  # type: ignore[return-value]


def _validate_review_status(value: str) -> RejectedAnswerReviewStatus:
    """Valide le statut demandé afin de renvoyer une erreur métier contrôlée."""
    status = _as_string(value, default="")
    if status not in ALLOWED_REVIEW_STATUSES:
        raise RejectedAnswerReviewInvalidStatusError(status)
    return status  # type: ignore[return-value]


def _review_event_to_audit_event(event: AuditEventData) -> RejectedAnswerReviewAuditEvent:
    """Expose une preuve d'audit compacte dans la réponse admin."""
    return RejectedAnswerReviewAuditEvent(
        event_id=event.event_id,
        action=event.action,
        target_type=event.target_type,
        target_id=event.target_id,
        status=event.status,
        created_at=event.created_at,
    )


def _rejected_answer_query() -> Any:
    """Retourne la requête canonique des réponses rejetées journalisées."""
    return (
        select(AuditEventModel)
        .where(
            AuditEventModel.action.in_(REJECTED_ANSWER_ACTIONS),
            AuditEventModel.target_type == "narrative_answer",
            AuditEventModel.status == "success",
        )
        .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
    )


def _find_rejected_answer(db: Session, answer_id: str) -> AuditEventModel | None:
    """Retrouve une réponse rejetée depuis le store canonique `audit_events`."""
    return db.scalar(
        _rejected_answer_query().where(
            AuditEventModel.target_id == answer_id,
        )
    )


def _latest_review_event(db: Session, answer_id: str) -> AuditEventModel | None:
    """Lit le dernier changement de statut interne pour une réponse rejetée."""
    return db.scalar(
        select(AuditEventModel)
        .where(
            AuditEventModel.action == REVIEWED_ACTION,
            AuditEventModel.target_type == REVIEW_TARGET_TYPE,
            AuditEventModel.target_id == answer_id,
            AuditEventModel.status == "success",
        )
        .order_by(AuditEventModel.created_at.desc(), AuditEventModel.id.desc())
    )


def _build_review_item(
    rejected_event: AuditEventModel,
    *,
    review_event: AuditEventModel | None,
) -> RejectedAnswerReviewItem:
    """Transforme les événements d'audit en payload admin stable."""
    details = rejected_event.details or {}
    review_details = review_event.details if review_event is not None else {}
    review_status = _as_review_status(
        review_details.get("review_status") if review_details else None
    )
    answer_id = _as_string(details.get("answer_id") or rejected_event.target_id)

    return RejectedAnswerReviewItem(
        answer_id=answer_id,
        review_status=review_status,
        rejection_reason=_as_rejection_reason(details),
        missing_evidence_refs=_as_missing_evidence_refs(details.get("missing_evidence_refs")),
        prompt_version=_as_string(details.get("prompt_version")),
        projection_version=_as_string(details.get("projection_version")),
        provider=_as_string(details.get("provider")),
        model=_as_string(details.get("model")),
        created_at=rejected_event.created_at,
        reviewed_at=review_event.created_at if review_event is not None else None,
        reviewed_by=review_event.actor_user_id if review_event is not None else None,
        review_note=(
            _as_string(review_details.get("review_note"), default="")
            if review_details.get("review_note")
            else None
        ),
    )


def _review_events_by_answer_id(
    db: Session,
    answer_ids: Iterable[str],
) -> dict[str, AuditEventModel]:
    """Associe chaque réponse à son dernier statut de revue connu."""
    latest: dict[str, AuditEventModel] = {}
    for answer_id in answer_ids:
        event = _latest_review_event(db, answer_id)
        if event is not None:
            latest[answer_id] = event
    return latest


def _record_review_audit_event(
    db: Session,
    *,
    request_id: str,
    current_user: AuthenticatedUser,
    action: str,
    answer_id: str | None,
    details: dict[str, object],
) -> AuditEventData:
    """Journalise une consultation ou action de revue via `AuditService`."""
    return AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action=action,
            target_type=REVIEW_TARGET_TYPE,
            target_id=answer_id,
            status="success",
            details={
                "contract_id": CONTRACT_ID,
                **details,
            },
        ),
    )


class RejectedAnswerReviewService:
    """Orchestre la revue admin sans créer de store d'audit parallèle."""

    @staticmethod
    def list_rejected_answers(
        db: Session,
        *,
        page: int,
        per_page: int,
        review_status: RejectedAnswerReviewStatus | None = None,
        request_id: str,
        current_user: AuthenticatedUser,
    ) -> RejectedAnswerReviewListResult:
        """Liste les réponses rejetées depuis `audit_events` avec statut de revue."""
        if per_page <= 0 or per_page > 100 or page <= 0:
            raise RejectedAnswerReviewUnavailableError("invalid pagination")

        query = _rejected_answer_query()
        if review_status is None:
            total = int(db.scalar(select(func.count()).select_from(query.subquery())) or 0)
            events = db.scalars(query.offset((page - 1) * per_page).limit(per_page)).all()
        else:
            all_events = db.scalars(query).all()
            all_answer_ids = [
                _as_string((event.details or {}).get("answer_id") or event.target_id)
                for event in all_events
            ]
            all_review_events = _review_events_by_answer_id(db, all_answer_ids)
            filtered_events = [
                event
                for event in all_events
                if _build_review_item(
                    event,
                    review_event=all_review_events.get(
                        _as_string((event.details or {}).get("answer_id") or event.target_id)
                    ),
                ).review_status
                == review_status
            ]
            total = len(filtered_events)
            start = (page - 1) * per_page
            events = filtered_events[start : start + per_page]
        answer_ids = [
            _as_string((event.details or {}).get("answer_id") or event.target_id)
            for event in events
        ]
        review_events = _review_events_by_answer_id(db, answer_ids)

        items = [
            _build_review_item(
                event,
                review_event=review_events.get(
                    _as_string((event.details or {}).get("answer_id") or event.target_id)
                ),
            )
            for event in events
        ]
        _record_review_audit_event(
            db,
            request_id=request_id,
            current_user=current_user,
            action=REVIEW_ACCESSED_ACTION,
            answer_id=None,
            details={
                "consultation": "list",
                "review_status": review_status or "all",
                "record_count": len(items),
            },
        )
        db.commit()
        return RejectedAnswerReviewListResult(items=items, total=total)

    @staticmethod
    def get_rejected_answer_detail(
        db: Session,
        *,
        answer_id: str,
        request_id: str,
        current_user: AuthenticatedUser,
    ) -> RejectedAnswerReviewDetailResponse:
        """Retourne le détail admin et journalise la consultation protégée."""
        rejected_event = _find_rejected_answer(db, answer_id)
        if rejected_event is None:
            raise RejectedAnswerReviewNotFoundError(answer_id)

        item = _build_review_item(
            rejected_event,
            review_event=_latest_review_event(db, answer_id),
        )
        audit_event = _record_review_audit_event(
            db,
            request_id=request_id,
            current_user=current_user,
            action=REVIEW_ACCESSED_ACTION,
            answer_id=answer_id,
            details={"review_status": item.review_status},
        )
        db.commit()

        return RejectedAnswerReviewDetailResponse(
            **item.model_dump(),
            manual_correction_limits=MANUAL_CORRECTION_LIMITS,
            audit_event=_review_event_to_audit_event(audit_event),
        )

    @staticmethod
    def update_review_status(
        db: Session,
        *,
        answer_id: str,
        review_status: str,
        review_note: str | None,
        request_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Change le statut interne de revue en journalisant l'action."""
        if _find_rejected_answer(db, answer_id) is None:
            raise RejectedAnswerReviewNotFoundError(answer_id)

        valid_review_status = _validate_review_status(review_status)

        _record_review_audit_event(
            db,
            request_id=request_id,
            current_user=current_user,
            action=REVIEWED_ACTION,
            answer_id=answer_id,
            details={
                "review_status": valid_review_status,
                "review_note": review_note,
            },
        )
        db.commit()

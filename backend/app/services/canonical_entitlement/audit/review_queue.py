# Service de construction de la review queue entitlement mutation.
"""Compose les lignes SLA à partir des audits, des reviews et du diff canonique."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.services.canonical_entitlement.audit.audit_query import (
    CanonicalEntitlementMutationAuditQueryService,
)
from app.services.canonical_entitlement.audit.diff_service import (
    CanonicalEntitlementMutationDiffService,
)

_STATUS_PRIORITY: dict[str | None, int] = {
    "pending_review": 0,
    "investigating": 1,
    "acknowledged": 2,
    "expected": 3,
    "closed": 4,
    None: 5,
}

_SLA_TARGETS: dict[tuple[str, str | None], int] = {
    ("high", "pending_review"): 14_400,  # 4h
    ("high", "investigating"): 86_400,  # 24h
    ("medium", "pending_review"): 86_400,  # 24h
    ("medium", None): 86_400,  # 24h (medium sans revue)
}
_SLA_DUE_SOON_RATIO = 0.20

ReviewStatusLiteral = Literal[
    "pending_review", "acknowledged", "expected", "investigating", "closed"
]


@dataclass
class ReviewQueueRow:
    audit: Any
    diff: Any
    review_record: CanonicalEntitlementMutationAuditReviewModel | None
    effective_review_status: ReviewStatusLiteral | None
    sla_target_seconds: int | None
    due_at: datetime | None
    sla_status: Literal["within_sla", "due_soon", "overdue"] | None
    overdue_seconds: int | None
    age_seconds: int
    age_hours: float


@dataclass
class ReviewQueueSummarySnapshot:
    pending_review_count: int
    investigating_count: int
    acknowledged_count: int
    closed_count: int
    expected_count: int
    no_review_count: int
    high_unreviewed_count: int
    total_count: int
    overdue_count: int
    due_soon_count: int
    oldest_pending_age_seconds: int | None = None


class CanonicalEntitlementReviewQueueService:
    @staticmethod
    def build_review_queue_rows(
        db: Session,
        *,
        now_utc: datetime,
        risk_level: str | None = None,
        effective_review_status: str | None = None,
        feature_code: str | None = None,
        actor_type: str | None = None,
        actor_identifier: str | None = None,
        incident_key: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        sla_status: str | None = None,
        max_sql_rows: int = 10000,
    ) -> list[ReviewQueueRow]:
        sql_kwargs = dict(
            feature_code=feature_code,
            actor_type=actor_type,
            actor_identifier=actor_identifier,
            date_from=date_from,
            date_to=date_to,
        )

        all_items, _ = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
            db, page=1, page_size=max_sql_rows, **sql_kwargs
        )

        if not all_items:
            return []

        # Load reviews
        audit_ids = [a.id for a in all_items]
        reviews_by_id = {}
        if audit_ids:
            result = db.execute(
                select(CanonicalEntitlementMutationAuditReviewModel).where(
                    CanonicalEntitlementMutationAuditReviewModel.audit_id.in_(audit_ids)
                )
            )
            reviews_by_id = {r.audit_id: r for r in result.scalars().all()}

        rows: list[ReviewQueueRow] = []
        for audit in all_items:
            diff = CanonicalEntitlementMutationDiffService.compute_diff(
                audit.before_payload or {}, audit.after_payload or {}
            )

            if risk_level and diff.risk_level != risk_level:
                continue

            review_record = reviews_by_id.get(audit.id)
            eff_status = CanonicalEntitlementReviewQueueService._compute_review_state_status(
                diff.risk_level, review_record
            )

            if effective_review_status and eff_status != effective_review_status:
                continue

            if incident_key:
                if review_record is None or review_record.incident_key != incident_key:
                    continue

            occurred_at = audit.occurred_at
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)

            age_seconds = int((now_utc - occurred_at).total_seconds())
            sla_data = CanonicalEntitlementReviewQueueService._compute_sla(
                diff.risk_level, eff_status, occurred_at, now_utc
            )

            if sla_status and sla_data["sla_status"] != sla_status:
                continue

            rows.append(
                ReviewQueueRow(
                    audit=audit,
                    diff=diff,
                    review_record=review_record,
                    effective_review_status=eff_status,
                    sla_target_seconds=sla_data["sla_target_seconds"],
                    due_at=sla_data["due_at"],
                    sla_status=sla_data["sla_status"],
                    overdue_seconds=sla_data["overdue_seconds"],
                    age_seconds=age_seconds,
                    age_hours=round(age_seconds / 3600, 2),
                )
            )

        rows.sort(
            key=lambda row: (
                _STATUS_PRIORITY.get(row.effective_review_status, _STATUS_PRIORITY[None]),
                CanonicalEntitlementReviewQueueService._normalize_occurred_at(
                    row.audit.occurred_at
                ),
                row.audit.id,
            )
        )
        return rows

    @staticmethod
    def summarize_review_queue_rows(rows: list[ReviewQueueRow]) -> ReviewQueueSummarySnapshot:
        counts: dict[str, int] = {}
        high_unreviewed = 0
        overdue_count = 0
        due_soon_count = 0
        oldest_pending_age: int | None = None

        for row in rows:
            eff_status = row.effective_review_status
            key = eff_status if eff_status is not None else "none"
            counts[key] = counts.get(key, 0) + 1

            if row.diff.risk_level == "high" and eff_status == "pending_review":
                high_unreviewed += 1

            if row.sla_status == "overdue":
                overdue_count += 1
            elif row.sla_status == "due_soon":
                due_soon_count += 1

            if eff_status == "pending_review":
                if oldest_pending_age is None or row.age_seconds > oldest_pending_age:
                    oldest_pending_age = row.age_seconds

        return ReviewQueueSummarySnapshot(
            pending_review_count=counts.get("pending_review", 0),
            investigating_count=counts.get("investigating", 0),
            acknowledged_count=counts.get("acknowledged", 0),
            closed_count=counts.get("closed", 0),
            expected_count=counts.get("expected", 0),
            no_review_count=counts.get("none", 0),
            high_unreviewed_count=high_unreviewed,
            total_count=len(rows),
            overdue_count=overdue_count,
            due_soon_count=due_soon_count,
            oldest_pending_age_seconds=oldest_pending_age,
        )

    @staticmethod
    def _compute_review_state_status(
        risk_level: str,
        review_record: CanonicalEntitlementMutationAuditReviewModel | None,
    ) -> ReviewStatusLiteral | None:
        if review_record is not None:
            return review_record.review_status
        if risk_level == "high":
            return "pending_review"
        return None

    @staticmethod
    def _compute_sla(
        risk_level: str,
        eff_status: str | None,
        occurred_at: datetime,
        now_utc: datetime,
    ) -> dict[str, Any]:
        """Retourne les 4 champs SLA pour un item de la review queue."""
        # Normalisation timezone
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        target = _SLA_TARGETS.get((risk_level, eff_status))
        if target is None:
            return {
                "sla_target_seconds": None,
                "due_at": None,
                "sla_status": None,
                "overdue_seconds": None,
            }

        age_s = int((now_utc - occurred_at).total_seconds())
        remaining = target - age_s
        due_soon_threshold = int(target * _SLA_DUE_SOON_RATIO)
        due_at = occurred_at + timedelta(seconds=target)

        if remaining <= 0:
            sla_status = "overdue"
            overdue_s = abs(remaining)
        elif remaining < due_soon_threshold:
            sla_status = "due_soon"
            overdue_s = None
        else:
            sla_status = "within_sla"
            overdue_s = None

        return {
            "sla_target_seconds": target,
            "due_at": due_at,
            "sla_status": sla_status,
            "overdue_seconds": overdue_s,
        }

    @staticmethod
    def _normalize_occurred_at(occurred_at: datetime) -> datetime:
        if occurred_at.tzinfo is None:
            return occurred_at.replace(tzinfo=timezone.utc)
        return occurred_at

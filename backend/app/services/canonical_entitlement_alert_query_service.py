from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import case, func, literal, select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)

AlertDeliveryStatus = Literal["sent", "failed"]


@dataclass
class AlertEventRow:
    event: CanonicalEntitlementMutationAlertEventModel
    attempt_count: int
    last_attempt_number: int | None
    last_attempt_status: str | None


@dataclass
class AlertSummaryResult:
    total_count: int
    failed_count: int
    sent_count: int
    retryable_count: int
    webhook_failed_count: int
    log_sent_count: int


class CanonicalEntitlementAlertQueryService:
    @staticmethod
    def list_alert_events(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        alert_kind: str | None = None,
        delivery_status: AlertDeliveryStatus | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[AlertEventRow], int]:
        model = CanonicalEntitlementMutationAlertEventModel
        column_names = [column.name for column in model.__table__.columns]
        base_subquery = CanonicalEntitlementAlertQueryService._build_filtered_query(
            alert_kind=alert_kind,
            delivery_status=delivery_status,
            audit_id=audit_id,
            feature_code=feature_code,
            plan_code=plan_code,
            actor_type=actor_type,
            request_id=request_id,
            date_from=date_from,
            date_to=date_to,
        ).subquery()
        paged_subquery = (
            select(base_subquery)
            .order_by(base_subquery.c.created_at.desc(), base_subquery.c.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .subquery()
        )
        total_count_subquery = (
            select(func.count())
            .select_from(base_subquery)
            .scalar_subquery()
        )
        has_page_items = select(literal(1)).select_from(paged_subquery).exists()
        page_query = (
            select(
                *[paged_subquery.c[name].label(name) for name in column_names],
                total_count_subquery.label("total_count"),
                literal(False).label("is_empty"),
            )
            .union_all(
                select(
                    *[
                        literal(None, type_=model.__table__.c[name].type).label(name)
                        for name in column_names
                    ],
                    total_count_subquery.label("total_count"),
                    literal(True).label("is_empty"),
                ).where(~has_page_items)
            )
        )
        page_rows = list(db.execute(page_query).mappings().all())
        if not page_rows:
            return [], 0
        if page_rows[0]["is_empty"]:
            return [], page_rows[0]["total_count"] or 0

        events = [
            model(**{name: row[name] for name in column_names})
            for row in page_rows
        ]
        total_count = page_rows[0]["total_count"] or 0

        attempts_by_event = CanonicalEntitlementAlertQueryService._load_attempts_by_event(
            db,
            event_ids=[event.id for event in events],
        )
        rows: list[AlertEventRow] = []
        for event in events:
            attempts = attempts_by_event.get(event.id, [])
            if attempts:
                last_attempt = max(attempts, key=lambda attempt: attempt.attempt_number)
                rows.append(
                    AlertEventRow(
                        event=event,
                        attempt_count=len(attempts),
                        last_attempt_number=last_attempt.attempt_number,
                        last_attempt_status=last_attempt.delivery_status,
                    )
                )
                continue
            rows.append(
                AlertEventRow(
                    event=event,
                    attempt_count=0,
                    last_attempt_number=None,
                    last_attempt_status=None,
                )
            )
        return rows, total_count

    @staticmethod
    def get_summary(
        db: Session,
        *,
        alert_kind: str | None = None,
        delivery_status: AlertDeliveryStatus | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AlertSummaryResult:
        base = CanonicalEntitlementAlertQueryService._build_filtered_query(
            alert_kind=alert_kind,
            delivery_status=delivery_status,
            audit_id=audit_id,
            feature_code=feature_code,
            plan_code=plan_code,
            actor_type=actor_type,
            request_id=request_id,
            date_from=date_from,
            date_to=date_to,
        ).subquery()

        row = db.execute(
            select(
                func.count().label("total_count"),
                func.count(case((base.c.delivery_status == "failed", 1))).label("failed_count"),
                func.count(case((base.c.delivery_status == "sent", 1))).label("sent_count"),
                func.count(
                    case(
                        (
                            (base.c.delivery_channel == "webhook")
                            & (base.c.delivery_status == "failed"),
                            1,
                        )
                    )
                ).label("webhook_failed_count"),
                func.count(
                    case(
                        (
                            (base.c.delivery_channel == "log")
                            & (base.c.delivery_status == "sent"),
                            1,
                        )
                    )
                ).label("log_sent_count"),
            ).select_from(base)
        ).one()

        failed_count = row.failed_count or 0
        return AlertSummaryResult(
            total_count=row.total_count or 0,
            failed_count=failed_count,
            sent_count=row.sent_count or 0,
            retryable_count=failed_count,
            webhook_failed_count=row.webhook_failed_count or 0,
            log_sent_count=row.log_sent_count or 0,
        )

    @staticmethod
    def _build_filtered_query(
        *,
        alert_kind: str | None = None,
        delivery_status: AlertDeliveryStatus | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ):
        model = CanonicalEntitlementMutationAlertEventModel
        query = select(model)
        if alert_kind is not None:
            query = query.where(model.alert_kind == alert_kind)
        if delivery_status is not None:
            query = query.where(model.delivery_status == delivery_status)
        if audit_id is not None:
            query = query.where(model.audit_id == audit_id)
        if feature_code is not None:
            query = query.where(model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            query = query.where(model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            query = query.where(model.actor_type_snapshot == actor_type)
        if request_id is not None:
            query = query.where(model.request_id == request_id)
        if date_from is not None:
            query = query.where(model.created_at >= date_from)
        if date_to is not None:
            query = query.where(model.created_at <= date_to)
        return query

    @staticmethod
    def _load_attempts_by_event(
        db: Session, *, event_ids: list[int]
    ) -> dict[int, list[CanonicalEntitlementMutationAlertDeliveryAttemptModel]]:
        attempts = list(
            db.scalars(
                select(CanonicalEntitlementMutationAlertDeliveryAttemptModel).where(
                    CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id.in_(
                        event_ids
                    )
                )
            ).all()
        )
        attempts_by_event: dict[
            int, list[CanonicalEntitlementMutationAlertDeliveryAttemptModel]
        ] = defaultdict(list)
        for attempt in attempts:
            attempts_by_event[attempt.alert_event_id].append(attempt)
        return attempts_by_event

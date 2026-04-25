# Service de batch handling des alertes entitlement mutation.
"""Applique des handlings de masse sans dupliquer la logique de current state."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.services.canonical_entitlement.alert.handling import (
    CanonicalEntitlementAlertHandlingService,
)

logger = logging.getLogger(__name__)


@dataclass
class BatchHandleResult:
    candidate_count: int
    handled_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int] = field(default_factory=list)


class CanonicalEntitlementAlertBatchHandlingService:
    @staticmethod
    def batch_handle(
        db: Session,
        *,
        limit: int,
        handling_status: str,
        ops_comment: str | None = None,
        suppression_key: str | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        handled_by_user_id: int | None = None,
        alert_kind: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> BatchHandleResult:
        candidates = CanonicalEntitlementAlertBatchHandlingService._load_batch_candidates(
            db,
            limit=limit,
            alert_kind=alert_kind,
            audit_id=audit_id,
            feature_code=feature_code,
            plan_code=plan_code,
            actor_type=actor_type,
            request_id_filter=request_id_filter,
            date_from=date_from,
            date_to=date_to,
        )
        alert_event_ids = [event.id for event in candidates]
        existing_handlings = CanonicalEntitlementAlertBatchHandlingService._load_existing_handlings(
            db, alert_event_ids=alert_event_ids
        )

        handled_count = 0
        skipped_count = 0

        for event in candidates:
            existing = existing_handlings.get(event.id)
            is_noop = (
                existing is not None
                and existing.handling_status == handling_status
                and existing.ops_comment == ops_comment
                and existing.suppression_key == suppression_key
            )
            if is_noop:
                skipped_count += 1
                continue

            if not dry_run:
                CanonicalEntitlementAlertHandlingService.upsert_handling(
                    db,
                    alert_event_id=event.id,
                    handling_status=handling_status,
                    handled_by_user_id=handled_by_user_id,
                    ops_comment=ops_comment,
                    suppression_key=suppression_key,
                    request_id=request_id,
                )
            handled_count += 1

        return BatchHandleResult(
            candidate_count=len(candidates),
            handled_count=handled_count,
            skipped_count=skipped_count,
            dry_run=dry_run,
            alert_event_ids=alert_event_ids,
        )

    @staticmethod
    def _load_existing_handlings(
        db: Session, *, alert_event_ids: list[int]
    ) -> dict[int, CanonicalEntitlementMutationAlertHandlingModel]:
        if not alert_event_ids:
            return {}

        result = db.execute(
            select(CanonicalEntitlementMutationAlertHandlingModel).where(
                CanonicalEntitlementMutationAlertHandlingModel.alert_event_id.in_(alert_event_ids)
            )
        )
        return {handling.alert_event_id: handling for handling in result.scalars().all()}

    @staticmethod
    def _load_batch_candidates(
        db: Session,
        *,
        limit: int,
        alert_kind: str | None,
        audit_id: int | None,
        feature_code: str | None,
        plan_code: str | None,
        actor_type: str | None,
        request_id_filter: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[CanonicalEntitlementMutationAlertEventModel]:
        model = CanonicalEntitlementMutationAlertEventModel
        query = select(model)
        if alert_kind is not None:
            query = query.where(model.alert_kind == alert_kind)
        if audit_id is not None:
            query = query.where(model.audit_id == audit_id)
        if feature_code is not None:
            query = query.where(model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            query = query.where(model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            query = query.where(model.actor_type_snapshot == actor_type)
        if request_id_filter is not None:
            query = query.where(model.request_id == request_id_filter)
        if date_from is not None:
            query = query.where(model.created_at >= date_from)
        if date_to is not None:
            query = query.where(model.created_at <= date_to)
        query = query.order_by(model.id.asc()).limit(limit)
        return list(db.scalars(query).all())

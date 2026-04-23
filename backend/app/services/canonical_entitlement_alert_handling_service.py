from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling_event import (
    CanonicalEntitlementMutationAlertEventHandlingEventModel,
)


class CanonicalEntitlementAlertHandlingService:
    @staticmethod
    def upsert_handling(
        db: Session,
        *,
        alert_event_id: int,
        handling_status: str,
        handled_by_user_id: int | None,
        ops_comment: str | None,
        suppression_key: str | None,
        request_id: str | None = None,
    ) -> CanonicalEntitlementMutationAlertEventHandlingModel:
        alert_event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
        if alert_event is None:
            raise HTTPException(status_code=404, detail="alert event not found")

        handling = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id == alert_event_id
            )
        ).scalar_one_or_none()

        is_creation = handling is None
        previous_status = None if is_creation else handling.handling_status
        previous_comment = None if is_creation else handling.ops_comment
        previous_suppression_key = None if is_creation else handling.suppression_key

        is_noop = (
            not is_creation
            and previous_status == handling_status
            and previous_comment == ops_comment
            and previous_suppression_key == suppression_key
        )
        if is_noop:
            return handling

        now = datetime_provider.utcnow()
        if is_creation:
            handling = CanonicalEntitlementMutationAlertEventHandlingModel(
                alert_event_id=alert_event_id,
                handling_status=handling_status,
                handled_by_user_id=handled_by_user_id,
                handled_at=now,
                ops_comment=ops_comment,
                suppression_key=suppression_key,
            )
            db.add(handling)
        else:
            handling.handling_status = handling_status
            handling.handled_by_user_id = handled_by_user_id
            handling.handled_at = now
            handling.ops_comment = ops_comment
            handling.suppression_key = suppression_key

        CanonicalEntitlementAlertHandlingService.append_handling_event(
            db,
            alert_event_id=alert_event_id,
            handling_status=handling_status,
            handled_by_user_id=handled_by_user_id,
            handled_at=now,
            ops_comment=ops_comment,
            suppression_key=suppression_key,
            request_id=request_id,
        )
        return handling

    @staticmethod
    def append_handling_event(
        db: Session,
        *,
        alert_event_id: int,
        handling_status: str,
        handled_by_user_id: int | None,
        ops_comment: str | None,
        suppression_key: str | None,
        request_id: str | None,
        handled_at: datetime | None = None,
    ) -> CanonicalEntitlementMutationAlertEventHandlingEventModel:
        event = CanonicalEntitlementMutationAlertEventHandlingEventModel(
            alert_event_id=alert_event_id,
            handling_status=handling_status,
            handled_by_user_id=handled_by_user_id,
            handled_at=handled_at or datetime_provider.utcnow(),
            ops_comment=ops_comment,
            suppression_key=suppression_key,
            request_id=request_id,
        )
        db.add(event)
        db.flush()
        return event

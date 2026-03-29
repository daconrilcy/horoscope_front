from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
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
    ) -> CanonicalEntitlementMutationAlertEventHandlingModel:
        alert_event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
        if alert_event is None:
            raise HTTPException(status_code=404, detail="alert event not found")

        handling = db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
                CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id == alert_event_id
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if handling is None:
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

        db.flush()
        return handling

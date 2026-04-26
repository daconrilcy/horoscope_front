# Service de gestion du current handling des alertes entitlement mutation.
"""Versionne le handling courant, historise les transitions et synchronise l'alerte."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.services.canonical_entitlement.suppression.application import (
    CanonicalEntitlementAlertSuppressionApplicationService,
)


class AlertEventNotFoundError(Exception):
    """Signale qu'un événement d'alerte entitlement est introuvable."""


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
    ) -> CanonicalEntitlementMutationAlertHandlingModel:
        alert_event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
        if alert_event is None:
            raise AlertEventNotFoundError("alert event not found")

        handling = db.execute(
            select(CanonicalEntitlementMutationAlertHandlingModel).where(
                CanonicalEntitlementMutationAlertHandlingModel.alert_event_id == alert_event_id
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
        suppression_application = (
            CanonicalEntitlementAlertHandlingService._create_suppression_application(
                db=db,
                alert_event_id=alert_event_id,
                suppression_key=suppression_key,
                ops_comment=ops_comment,
                handled_by_user_id=handled_by_user_id,
                request_id=request_id,
                applied_at=now,
            )
            if handling_status == "suppressed"
            else None
        )
        if is_creation:
            handling = CanonicalEntitlementMutationAlertHandlingModel(
                alert_event_id=alert_event_id,
                handling_status=handling_status,
                handled_by_user_id=handled_by_user_id,
                handled_at=now,
                ops_comment=ops_comment,
                suppression_key=suppression_key,
                suppression_application_id=(
                    suppression_application.id if suppression_application is not None else None
                ),
                resolution_code=handling_status,
                request_id=request_id,
                handling_version=1,
            )
            db.add(handling)
        else:
            handling.handling_status = handling_status
            handling.handled_by_user_id = handled_by_user_id
            handling.handled_at = now
            handling.ops_comment = ops_comment
            handling.suppression_key = suppression_key
            handling.suppression_application_id = (
                suppression_application.id if suppression_application is not None else None
            )
            handling.resolution_code = handling_status
            handling.request_id = request_id
            handling.handling_version += 1
            handling.updated_at = now

        CanonicalEntitlementAlertHandlingService._synchronise_alert_event(
            alert_event=alert_event,
            handling_status=handling_status,
            ops_comment=ops_comment,
            suppression_key=suppression_key,
            handled_at=now,
        )

        CanonicalEntitlementAlertHandlingService.append_handling_event(
            db,
            alert_event_id=alert_event_id,
            handling_status=handling_status,
            handled_by_user_id=handled_by_user_id,
            handled_at=now,
            ops_comment=ops_comment,
            suppression_key=suppression_key,
            request_id=request_id,
            event_type="created" if is_creation else "updated",
            resolution_code=handling_status,
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
        event_type: str = "updated",
        resolution_code: str | None = None,
    ) -> CanonicalEntitlementMutationAlertHandlingEventModel:
        event = CanonicalEntitlementMutationAlertHandlingEventModel(
            alert_event_id=alert_event_id,
            event_type=event_type,
            handling_status=handling_status,
            handled_by_user_id=handled_by_user_id,
            handled_at=handled_at or datetime_provider.utcnow(),
            ops_comment=ops_comment,
            suppression_key=suppression_key,
            request_id=request_id,
            resolution_code=resolution_code,
        )
        db.add(event)
        db.flush()
        return event

    @staticmethod
    def _create_suppression_application(
        *,
        db: Session,
        alert_event_id: int,
        suppression_key: str | None,
        ops_comment: str | None,
        handled_by_user_id: int | None,
        request_id: str | None,
        applied_at: datetime,
    ) -> CanonicalEntitlementMutationAlertSuppressionApplicationModel:
        application = (
            CanonicalEntitlementAlertSuppressionApplicationService.ensure_manual_application(
                db,
                alert_event_id=alert_event_id,
                suppression_key=suppression_key,
                ops_comment=ops_comment,
                handled_by_user_id=handled_by_user_id,
                request_id=request_id,
                applied_at=applied_at,
            )
        )
        return application

    @staticmethod
    def _synchronise_alert_event(
        *,
        alert_event: CanonicalEntitlementMutationAlertEventModel,
        handling_status: str,
        ops_comment: str | None,
        suppression_key: str | None,
        handled_at: datetime,
    ) -> None:
        alert_event.updated_at = handled_at
        if handling_status == "suppressed":
            alert_event.alert_status = "suppressed"
            alert_event.is_suppressed = True
            alert_event.suppressed_at = handled_at
            alert_event.suppression_reason = ops_comment or suppression_key
            alert_event.closed_at = handled_at
            return

        if handling_status == "resolved":
            alert_event.alert_status = "closed"
            alert_event.is_suppressed = False
            alert_event.suppressed_at = None
            alert_event.suppression_reason = None
            alert_event.closed_at = handled_at

# Primitives partagées de livraison d'alertes entitlement mutation.
"""Mutualise la livraison webhook/log et la synchronisation du state de delivery."""

from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertDeliveryOutcome:
    """Décrit le résultat canonique d'une livraison d'alerte."""

    channel: str
    status: str
    error: str | None
    delivered_at: datetime | None
    is_retryable: bool


class CanonicalEntitlementAlertDeliveryRuntime:
    """Centralise les primitives DRY de delivery pour les services d'alertes."""

    @staticmethod
    def deliver_payload(
        payload: dict[str, Any],
        *,
        log_message: str,
        delivered_at: datetime | None = None,
    ) -> AlertDeliveryOutcome:
        """Livre un payload via webhook si configuré, sinon via log applicatif."""

        effective_delivered_at = delivered_at or datetime_provider.utcnow()
        if settings.ops_review_queue_alert_webhook_url:
            success, error_message = CanonicalEntitlementAlertDeliveryRuntime._deliver_webhook(
                settings.ops_review_queue_alert_webhook_url,
                payload,
            )
            if success:
                return AlertDeliveryOutcome(
                    channel="webhook",
                    status="sent",
                    error=None,
                    delivered_at=effective_delivered_at,
                    is_retryable=False,
                )
            return AlertDeliveryOutcome(
                channel="webhook",
                status="failed",
                error=error_message,
                delivered_at=None,
                is_retryable=True,
            )

        logger.info("%s payload=%s", log_message, payload)
        return AlertDeliveryOutcome(
            channel="log",
            status="sent",
            error=None,
            delivered_at=effective_delivered_at,
            is_retryable=False,
        )

    @staticmethod
    def add_delivery_attempt(
        *,
        db,
        alert_event: CanonicalEntitlementMutationAlertEventModel,
        attempt_number: int,
        request_id: str | None,
        payload: dict[str, Any],
        outcome: AlertDeliveryOutcome,
    ) -> None:
        """Ajoute une tentative append-only avec le format canonique partagé."""

        db.add(
            CanonicalEntitlementMutationAlertDeliveryAttemptModel(
                alert_event_id=alert_event.id,
                attempt_number=attempt_number,
                delivery_provider=outcome.channel,
                delivery_channel=outcome.channel,
                delivery_status=outcome.status,
                delivery_error=outcome.error,
                request_id=request_id,
                payload=payload,
                delivered_at=outcome.delivered_at,
                is_retryable=outcome.is_retryable,
            )
        )

    @staticmethod
    def apply_delivery_state(
        *,
        alert_event: CanonicalEntitlementMutationAlertEventModel,
        outcome: AlertDeliveryOutcome,
        attempt_number: int,
        updated_at=None,
    ) -> None:
        """Synchronise le current state d'une alerte après une livraison."""

        effective_updated_at = updated_at or datetime_provider.utcnow()
        alert_event.delivery_channel = outcome.channel
        alert_event.last_delivery_status = outcome.status
        alert_event.delivery_status = outcome.status
        alert_event.last_delivery_error = outcome.error
        alert_event.delivery_error = outcome.error
        alert_event.last_delivered_at = outcome.delivered_at
        alert_event.delivered_at = outcome.delivered_at
        alert_event.delivery_attempt_count = attempt_number
        alert_event.updated_at = effective_updated_at
        if outcome.delivered_at is not None and alert_event.first_delivered_at is None:
            alert_event.first_delivered_at = outcome.delivered_at

    @staticmethod
    def _deliver_webhook(url: str, payload: dict[str, Any]) -> tuple[bool, str | None]:
        """Exécute la livraison webhook synchrone avec timeout borné."""

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if 200 <= response.status < 300:
                    return True, None
                return False, f"HTTP {response.status}"
        except Exception as error:  # pragma: no cover - dépend des erreurs I/O runtime
            return False, str(error)

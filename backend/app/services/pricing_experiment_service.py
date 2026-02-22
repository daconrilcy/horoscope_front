"""
Service d'expérimentation tarifaire.

Ce module gère les expérimentations A/B sur les offres tarifaires :
assignation de variantes, enregistrement des événements (exposition,
conversion, rétention, revenus).
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.core.config import settings
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)

EXPERIMENT_KEY = "packaging_pricing_v1"
EVENT_VERSION = "1.0"
VARIANTS: tuple[str, ...] = ("control", "value_plus")


class PricingExperimentServiceError(Exception):
    """Exception levée lors d'erreurs d'expérimentation tarifaire."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur d'expérimentation.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class PricingExperimentEvent(BaseModel):
    """Événement d'expérimentation tarifaire."""

    event_name: Literal["offer_exposure", "offer_conversion", "offer_retention", "offer_revenue"]
    event_version: str = EVENT_VERSION
    variant_id: str
    user_segment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_id: str | None = None
    user_id: int | None = None
    plan_code: str | None = None
    conversion_type: str | None = None
    conversion_status: str | None = None
    revenue_cents: int | None = None
    retention_event: str | None = None

    @model_validator(mode="after")
    def _validate_payload(self) -> "PricingExperimentEvent":
        """Valide les champs requis selon le type d'événement."""
        if self.event_version != EVENT_VERSION:
            raise ValueError("event_version is invalid")
        if not self.variant_id.strip():
            raise ValueError("variant_id is required")
        if not self.user_segment.strip():
            raise ValueError("user_segment is required")

        if self.event_name == "offer_conversion":
            if self.conversion_type is None or not self.conversion_type.strip():
                raise ValueError("conversion_type is required for conversion event")
            if self.conversion_status is None or not self.conversion_status.strip():
                raise ValueError("conversion_status is required for conversion event")

        if self.event_name == "offer_revenue":
            if self.revenue_cents is None or self.revenue_cents <= 0:
                raise ValueError("revenue_cents must be > 0 for revenue event")

        if self.event_name == "offer_retention":
            if self.retention_event is None or not self.retention_event.strip():
                raise ValueError("retention_event is required for retention event")

        return self


class PricingExperimentService:
    """
    Service d'expérimentation tarifaire A/B.

    Gère l'assignation déterministe des variantes et l'enregistrement
    des événements pour mesurer l'impact des offres.
    """

    @staticmethod
    def is_enabled() -> bool:
        """Indique si l'expérimentation est activée."""
        return settings.pricing_experiment_enabled

    @staticmethod
    def assign_variant(user_id: int) -> str:
        """Assigne une variante de façon déterministe basée sur l'ID utilisateur."""
        digest = hashlib.sha256(f"{EXPERIMENT_KEY}:{user_id}".encode("utf-8")).digest()
        variant_index = digest[0] % len(VARIANTS)
        return VARIANTS[variant_index]

    @staticmethod
    def _segment_from_role(user_role: str) -> str:
        """Normalise le rôle utilisateur en segment."""
        normalized = user_role.strip().lower()
        return normalized or "unknown"

    @staticmethod
    def _metric_name(base: str, **labels: str) -> str:
        """Construit un nom de métrique avec labels."""
        parts = [base]
        for key in sorted(labels):
            safe_value = labels[key].replace("|", "_").replace("=", "_").replace(" ", "_")
            parts.append(f"{key}={safe_value}")
        return "|".join(parts)

    @staticmethod
    def _guard_enabled() -> bool:
        """Vérifie si l'expérimentation est activée et incrémente le compteur si désactivée."""
        if settings.pricing_experiment_enabled:
            return True
        increment_counter("pricing_experiment_events_dropped_total|reason=disabled", 1.0)
        return False

    @staticmethod
    def record_offer_exposure(
        *,
        user_id: int,
        user_role: str,
        plan_code: str,
        request_id: str | None,
    ) -> PricingExperimentEvent | None:
        """Enregistre une exposition à une offre."""
        if not PricingExperimentService._guard_enabled():
            return None
        event = PricingExperimentEvent(
            event_name="offer_exposure",
            variant_id=PricingExperimentService.assign_variant(user_id),
            user_segment=PricingExperimentService._segment_from_role(user_role),
            request_id=request_id,
            user_id=user_id,
            plan_code=plan_code,
        )
        increment_counter(
            PricingExperimentService._metric_name(
                "pricing_experiment_exposure_total",
                variant_id=event.variant_id,
                user_segment=event.user_segment,
                plan_code=event.plan_code or "unknown",
            ),
            1.0,
        )
        return event

    @staticmethod
    def record_offer_conversion(
        *,
        user_id: int,
        user_role: str,
        plan_code: str,
        conversion_type: str,
        conversion_status: str,
        request_id: str | None,
    ) -> PricingExperimentEvent | None:
        """Enregistre une conversion (souscription ou achat)."""
        if not PricingExperimentService._guard_enabled():
            return None
        event = PricingExperimentEvent(
            event_name="offer_conversion",
            variant_id=PricingExperimentService.assign_variant(user_id),
            user_segment=PricingExperimentService._segment_from_role(user_role),
            request_id=request_id,
            user_id=user_id,
            plan_code=plan_code,
            conversion_type=conversion_type,
            conversion_status=conversion_status,
        )
        increment_counter(
            PricingExperimentService._metric_name(
                "pricing_experiment_conversion_total",
                variant_id=event.variant_id,
                user_segment=event.user_segment,
                plan_code=event.plan_code or "unknown",
                conversion_type=event.conversion_type or "unknown",
                status=event.conversion_status or "unknown",
            ),
            1.0,
        )
        return event

    @staticmethod
    def record_offer_revenue(
        *,
        user_id: int,
        user_role: str,
        plan_code: str,
        revenue_cents: int,
        request_id: str | None,
    ) -> PricingExperimentEvent | None:
        """Enregistre un revenu généré."""
        if not PricingExperimentService._guard_enabled():
            return None
        event = PricingExperimentEvent(
            event_name="offer_revenue",
            variant_id=PricingExperimentService.assign_variant(user_id),
            user_segment=PricingExperimentService._segment_from_role(user_role),
            request_id=request_id,
            user_id=user_id,
            plan_code=plan_code,
            revenue_cents=revenue_cents,
        )
        increment_counter(
            PricingExperimentService._metric_name(
                "pricing_experiment_revenue_cents_total",
                variant_id=event.variant_id,
                user_segment=event.user_segment,
                plan_code=event.plan_code or "unknown",
            ),
            float(event.revenue_cents or 0),
        )
        return event

    @staticmethod
    def record_retention_usage(
        *,
        user_id: int,
        user_role: str,
        plan_code: str,
        retention_event: str,
        request_id: str | None,
    ) -> PricingExperimentEvent | None:
        """Enregistre un événement de rétention (usage continu)."""
        if not PricingExperimentService._guard_enabled():
            return None
        event = PricingExperimentEvent(
            event_name="offer_retention",
            variant_id=PricingExperimentService.assign_variant(user_id),
            user_segment=PricingExperimentService._segment_from_role(user_role),
            request_id=request_id,
            user_id=user_id,
            plan_code=plan_code,
            retention_event=retention_event,
        )
        increment_counter(
            PricingExperimentService._metric_name(
                "pricing_experiment_retention_usage_total",
                variant_id=event.variant_id,
                user_segment=event.user_segment,
                plan_code=event.plan_code or "unknown",
                retention_event=event.retention_event or "unknown",
            ),
            1.0,
        )
        return event

    @staticmethod
    def record_variant_state_change(*, enabled: bool, request_id: str | None = None) -> None:
        """Enregistre un changement d'état de l'expérimentation."""
        logger.info(
            "pricing_experiment_state_changed enabled=%s request_id=%s variants=%s",
            enabled,
            request_id or "n/a",
            ",".join(VARIANTS),
        )

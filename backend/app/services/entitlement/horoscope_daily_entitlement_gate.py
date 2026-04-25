"""Gate entitlement canonique pour la variation horoscope daily."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)

logger = logging.getLogger(__name__)


class HoroscopeDailyAccessDeniedError(Exception):
    def __init__(
        self,
        reason: str,
        billing_status: str,
        plan_code: str,
        reason_code: str | None = None,
    ) -> None:
        self.reason = reason
        self.reason_code = reason_code or reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Horoscope daily access denied: {reason}")


@dataclass
class HoroscopeDailyEntitlementResult:
    variant_code: str


class HoroscopeDailyEntitlementGate:
    FEATURE_CODE = "horoscope_daily"

    @staticmethod
    def check_and_get_variant(db: Session, *, user_id: int) -> HoroscopeDailyEntitlementResult:
        """Retourne le variant canonique ou refuse explicitement l'accès."""
        if not isinstance(db, Session):
            raise HoroscopeDailyAccessDeniedError(
                reason="invalid_db_session",
                billing_status="unknown",
                plan_code="none",
                reason_code="invalid_db_session",
            )

        try:
            snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                db, app_user_id=user_id
            )
        except Exception as exc:
            logger.warning(
                "horoscope_daily_entitlement_resolution_failed user_id=%s reason=%s",
                user_id,
                exc.__class__.__name__,
            )
            raise HoroscopeDailyAccessDeniedError(
                reason="entitlement_resolution_failed",
                billing_status="unknown",
                plan_code="none",
                reason_code="entitlement_resolution_failed",
            ) from exc
        access = snapshot.entitlements.get(HoroscopeDailyEntitlementGate.FEATURE_CODE)

        if access is None:
            raise HoroscopeDailyAccessDeniedError(
                reason="feature_not_configured",
                billing_status=snapshot.billing_status,
                plan_code=snapshot.plan_code,
                reason_code="feature_not_configured",
            )

        if not access.granted:
            raise HoroscopeDailyAccessDeniedError(
                reason=access.reason_code,
                billing_status=snapshot.billing_status,
                plan_code=snapshot.plan_code,
                reason_code=access.reason_code,
            )

        # Le variant_code est résolu depuis le catalog DB via le EffectiveEntitlementResolverService
        # Les valeurs attendues : "summary_only" (free) | "full" (basic, premium)
        variant = access.variant_code or "full"
        return HoroscopeDailyEntitlementResult(variant_code=variant)

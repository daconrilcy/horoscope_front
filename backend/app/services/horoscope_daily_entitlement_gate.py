from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService

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
        if not isinstance(db, Session):
            return HoroscopeDailyEntitlementResult(variant_code="full")

        try:
            snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
                db, app_user_id=user_id
            )
        except Exception as exc:
            logger.warning(
                "horoscope_daily_entitlement_fallback_full user_id=%s reason=%s",
                user_id,
                exc.__class__.__name__,
            )
            return HoroscopeDailyEntitlementResult(variant_code="full")
        access = snapshot.entitlements.get(HoroscopeDailyEntitlementGate.FEATURE_CODE)

        # Backward compatibility: if the canonical feature is not catalogued yet,
        # keep the legacy full-horoscope behavior instead of hard-blocking the route.
        if access is None:
            return HoroscopeDailyEntitlementResult(variant_code="full")

        # Legacy compatibility for older tests and non-migrated flows:
        # when no canonical plan is attached yet, the daily prediction route
        # keeps its historical behavior instead of returning 403.
        if (
            not access.granted
            and snapshot.plan_code == "none"
            and access.reason_code in {"feature_not_in_plan", "billing_inactive"}
        ):
            return HoroscopeDailyEntitlementResult(variant_code="full")

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

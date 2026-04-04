from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService


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
    def check_and_get_variant(
        db: Session, *, user_id: int
    ) -> HoroscopeDailyEntitlementResult:
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
            db, app_user_id=user_id
        )
        access = snapshot.entitlements.get(HoroscopeDailyEntitlementGate.FEATURE_CODE)

        if not access or not access.granted:
            raise HoroscopeDailyAccessDeniedError(
                reason=access.reason_code if access else "feature_not_in_plan",
                billing_status=snapshot.billing_status,
                plan_code=snapshot.plan_code,
                reason_code=access.reason_code if access else "feature_not_in_plan",
            )

        # Le variant_code est résolu depuis le catalog DB via le EffectiveEntitlementResolverService
        # Les valeurs attendues : "summary_only" (free) | "full" (basic, premium)
        variant = access.variant_code or "full"
        return HoroscopeDailyEntitlementResult(variant_code=variant)

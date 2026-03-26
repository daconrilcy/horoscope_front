from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaUsageService, QuotaExhaustedError


class NatalChartLongAccessDeniedError(Exception):
    def __init__(self, reason: str, billing_status: str, plan_code: str) -> None:
        self.reason = reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Natal chart long access denied: {reason}")


class NatalChartLongQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Natal chart long quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class NatalChartLongEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited"
    variant_code: str | None  # "single_astrologer" | "multi_astrologer" | None
    usage_states: list[UsageState] = field(default_factory=list)


class NatalChartLongEntitlementGate:
    FEATURE_CODE = "natal_chart_long"

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> NatalChartLongEntitlementResult:
        entitlement = EntitlementService.get_feature_entitlement(
            db, user_id=user_id, feature_code=NatalChartLongEntitlementGate.FEATURE_CODE
        )

        # Pas de chemin legacy — natal_chart_long est 100% canonique
        if entitlement.reason == "legacy_fallback":
            raise NatalChartLongAccessDeniedError(
                reason="canonical_no_binding",
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if not entitlement.final_access:
            if entitlement.quota_exhausted and entitlement.usage_states:
                exhausted_state = next((s for s in entitlement.usage_states if s.exhausted), None)
                if exhausted_state:
                    raise NatalChartLongQuotaExceededError(
                        quota_key=exhausted_state.quota_key,
                        used=exhausted_state.used,
                        limit=exhausted_state.quota_limit,
                        window_end=exhausted_state.window_end,  # None pour lifetime
                    )
            raise NatalChartLongAccessDeniedError(
                reason=entitlement.reason,
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if entitlement.access_mode == "unlimited":
            return NatalChartLongEntitlementResult(
                path="canonical_unlimited",
                variant_code=entitlement.variant_code,
                usage_states=entitlement.usage_states,
            )

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for quota in entitlement.quotas:
            try:
                state = QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=NatalChartLongEntitlementGate.FEATURE_CODE,
                    quota=quota,
                    amount=1,
                )
                consumed_states.append(state)
            except QuotaExhaustedError as exc:
                # Pour les quotas lifetime, window_end est None dans usage_states
                window_end = next(
                    (s.window_end for s in entitlement.usage_states if s.quota_key == exc.quota_key),
                    None,
                )
                raise NatalChartLongQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=window_end,
                ) from exc

        return NatalChartLongEntitlementResult(
            path="canonical_quota",
            variant_code=entitlement.variant_code,
            usage_states=consumed_states,
        )

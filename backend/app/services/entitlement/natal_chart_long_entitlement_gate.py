"""Gate entitlement canonique pour l'acces natal long cote runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.entitlement.b2c_runtime_gate import (
    consume_b2c_quota,
    resolve_b2c_access,
)
from app.services.entitlement.entitlement_types import UsageState


class NatalChartLongAccessDeniedError(Exception):
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
    def check_access(db: Session, *, user_id: int) -> NatalChartLongEntitlementResult:
        """Verifie l acces natal long sans consommer de quota."""
        access_snapshot = resolve_b2c_access(
            db,
            user_id=user_id,
            feature_code=NatalChartLongEntitlementGate.FEATURE_CODE,
            denied_error_factory=NatalChartLongAccessDeniedError,
            quota_error_factory=NatalChartLongQuotaExceededError,
        )
        return NatalChartLongEntitlementResult(
            path=access_snapshot.path,
            variant_code=access_snapshot.variant_code,
            usage_states=access_snapshot.usage_states,
        )

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> NatalChartLongEntitlementResult:
        """Verifie puis consomme les quotas natal long applicables."""
        result = NatalChartLongEntitlementGate.check_access(db, user_id=user_id)

        if result.path == "canonical_unlimited":
            return result

        consumed_states = consume_b2c_quota(
            db,
            user_id=user_id,
            feature_code=NatalChartLongEntitlementGate.FEATURE_CODE,
            usage_states=result.usage_states,
            quota_error_factory=NatalChartLongQuotaExceededError,
        )

        return NatalChartLongEntitlementResult(
            path="canonical_quota",
            variant_code=result.variant_code,
            usage_states=consumed_states,
        )

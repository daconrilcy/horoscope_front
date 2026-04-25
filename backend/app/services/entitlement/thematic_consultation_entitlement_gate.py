"""Gate entitlement canonique pour l'acces consultation thematique."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.entitlement.b2c_runtime_gate import (
    consume_b2c_quota,
    resolve_b2c_access,
)
from app.services.entitlement.entitlement_types import UsageState


class ConsultationAccessDeniedError(Exception):
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
        super().__init__(f"Consultation access denied: {reason}")


class ConsultationQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Consultation quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class ConsultationEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited"
    usage_states: list[UsageState] = field(default_factory=list)


class ThematicConsultationEntitlementGate:
    FEATURE_CODE = "thematic_consultation"

    @staticmethod
    def check_access(db: Session, *, user_id: int) -> ConsultationEntitlementResult:
        """Verifie l acces consultation thematique sans consommer de quota."""
        access_snapshot = resolve_b2c_access(
            db,
            user_id=user_id,
            feature_code=ThematicConsultationEntitlementGate.FEATURE_CODE,
            denied_error_factory=ConsultationAccessDeniedError,
            quota_error_factory=ConsultationQuotaExceededError,
        )
        return ConsultationEntitlementResult(
            path=access_snapshot.path,
            usage_states=access_snapshot.usage_states,
        )

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> ConsultationEntitlementResult:
        """Verifie puis consomme les quotas consultation applicables."""
        result = ThematicConsultationEntitlementGate.check_access(db, user_id=user_id)

        if result.path == "canonical_unlimited":
            return result

        consumed_states = consume_b2c_quota(
            db,
            user_id=user_id,
            feature_code=ThematicConsultationEntitlementGate.FEATURE_CODE,
            usage_states=result.usage_states,
            quota_error_factory=ConsultationQuotaExceededError,
            skip_quota_keys={"tokens"},
        )

        return ConsultationEntitlementResult(path="canonical_quota", usage_states=consumed_states)

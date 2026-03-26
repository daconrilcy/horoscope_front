from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.entitlement_service import EntitlementService
from app.services.entitlement_types import UsageState
from app.services.quota_usage_service import QuotaExhaustedError, QuotaUsageService


class ChatAccessDeniedError(Exception):
    def __init__(self, reason: str, billing_status: str, plan_code: str) -> None:
        self.reason = reason
        self.billing_status = billing_status
        self.plan_code = plan_code
        super().__init__(f"Chat access denied: {reason}")


class ChatQuotaExceededError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, window_end: datetime | None) -> None:
        self.quota_key = quota_key
        self.used = used
        self.limit = limit
        self.window_end = window_end
        super().__init__(f"Chat quota '{quota_key}' exceeded: {used}/{limit}")


@dataclass
class ChatEntitlementResult:
    path: str  # "canonical_quota" | "canonical_unlimited"
    usage_states: list[UsageState] = field(default_factory=list)


class ChatEntitlementGate:
    FEATURE_CODE = "astrologer_chat"

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> ChatEntitlementResult:
        entitlement = EntitlementService.get_feature_entitlement(
            db, user_id=user_id, feature_code=ChatEntitlementGate.FEATURE_CODE
        )

        # PRIORITÉ 1 : refus canoniques
        if not entitlement.final_access:
            if entitlement.quota_exhausted and entitlement.usage_states:
                # Find the first exhausted state to raise the error
                exhausted_state = next((s for s in entitlement.usage_states if s.exhausted), None)
                if exhausted_state:
                    raise ChatQuotaExceededError(
                        quota_key=exhausted_state.quota_key,
                        used=exhausted_state.used,
                        limit=exhausted_state.quota_limit,
                        window_end=exhausted_state.window_end,
                    )

            # Default to access denied if not specifically quota exhausted or no states
            raise ChatAccessDeniedError(
                reason=entitlement.reason,
                billing_status=entitlement.billing_status,
                plan_code=entitlement.plan_code,
            )

        if entitlement.access_mode == "unlimited":
            return ChatEntitlementResult(
                path="canonical_unlimited", usage_states=entitlement.usage_states
            )

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for quota in entitlement.quotas:
            try:
                state = QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=ChatEntitlementGate.FEATURE_CODE,
                    quota=quota,
                    amount=1,
                )
                consumed_states.append(state)
            except QuotaExhaustedError as exc:
                # If QuotaUsageService raises QuotaExhaustedError, we wrap it
                # Try to find the window_end from entitlement.usage_states
                window_end = next(
                    (
                        s.window_end
                        for s in entitlement.usage_states
                        if s.quota_key == exc.quota_key
                    ),
                    None,
                )
                raise ChatQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=window_end,
                ) from exc

        return ChatEntitlementResult(path="canonical_quota", usage_states=consumed_states)

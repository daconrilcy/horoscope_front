from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.effective_entitlement_gate_helpers import (
    map_b2c_reason_to_legacy,
    select_quota_usage_state,
)
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaExhaustedError, QuotaUsageService


class ChatAccessDeniedError(Exception):
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
    def check_access(db: Session, *, user_id: int) -> ChatEntitlementResult:
        """
        Only checks if the user has access and enough quota, WITHOUT consuming.
        """
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
            db, app_user_id=user_id
        )
        access = snapshot.entitlements.get(ChatEntitlementGate.FEATURE_CODE)

        if not access or not access.granted:
            reason_code = access.reason_code if access else "subject_not_eligible"
            if reason_code == "quota_exhausted":
                exhausted_state = select_quota_usage_state(access)
                quota_key = ChatEntitlementGate.FEATURE_CODE
                if exhausted_state:
                    quota_key = exhausted_state.quota_key
                used = (
                    exhausted_state.used
                    if exhausted_state
                    else (access.quota_used if access else 0)
                )
                limit = (
                    exhausted_state.quota_limit
                    if exhausted_state
                    else (access.quota_limit if access else 0)
                )
                raise ChatQuotaExceededError(
                    quota_key=quota_key,
                    used=used,
                    limit=limit,
                    window_end=exhausted_state.window_end if exhausted_state else None,
                )
            raise ChatAccessDeniedError(
                reason=map_b2c_reason_to_legacy(snapshot, access),
                reason_code=reason_code,
                billing_status=snapshot.billing_status,
                plan_code=snapshot.plan_code,
            )

        path = "canonical_unlimited" if access.access_mode == "unlimited" else "canonical_quota"
        return ChatEntitlementResult(
            path=path,
            usage_states=access.usage_states,
        )

    @staticmethod
    def check_and_consume(db: Session, *, user_id: int) -> ChatEntitlementResult:
        """
        Legacy/Simple flow: check access and consume 1 unit immediately.
        NOTE: For tokenized features, use check_access() then post-call consumption instead.
        """
        result = ChatEntitlementGate.check_access(db, user_id=user_id)

        if result.path == "canonical_unlimited":
            return result

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for state in result.usage_states:
            # Token quotas are consumed post-call with the exact LLM usage.
            if state.quota_key == "tokens":
                continue

            q_def = QuotaDefinition(
                quota_key=state.quota_key,
                quota_limit=state.quota_limit,
                period_unit=state.period_unit,
                period_value=state.period_value,
                reset_mode=state.reset_mode,
            )
            try:
                new_state = QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=ChatEntitlementGate.FEATURE_CODE,
                    quota=q_def,
                    amount=1,
                )
                consumed_states.append(new_state)
            except QuotaExhaustedError as exc:
                raise ChatQuotaExceededError(
                    quota_key=exc.quota_key,
                    used=exc.used,
                    limit=exc.limit,
                    window_end=state.window_end,
                ) from exc

        return ChatEntitlementResult(path="canonical_quota", usage_states=consumed_states)

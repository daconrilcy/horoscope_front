from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from sqlalchemy.orm import Session

from app.services.b2b.enterprise_quota_usage_service import EnterpriseQuotaUsageService
from app.services.entitlement.effective_entitlement_gate_helpers import select_quota_usage_state
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaExhaustedError

logger = logging.getLogger(__name__)


class B2BApiAccessDeniedError(Exception):
    def __init__(
        self,
        code: str,
        message: str = "B2B API access denied",
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{message} (code={code})")


class B2BApiQuotaExceededError(Exception):
    def __init__(
        self,
        code: str,
        message: str = "B2B API quota exceeded",
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{message} (code={code})")


@dataclass
class B2BApiEntitlementResult:
    path: Literal["canonical_quota", "canonical_unlimited"]
    usage_states: list[UsageState] = field(default_factory=list)
    source: str = "canonical"


class B2BApiEntitlementGate:
    FEATURE_CODE = "b2b_api_access"

    @staticmethod
    def check_and_consume(db: Session, *, account_id: int) -> B2BApiEntitlementResult:
        snapshot = EffectiveEntitlementResolverService.resolve_b2b_account_snapshot(
            db, enterprise_account_id=account_id
        )
        access = snapshot.entitlements.get(B2BApiEntitlementGate.FEATURE_CODE)

        if not access or not access.granted:
            reason_code = access.reason_code if access else "subject_not_eligible"
            if reason_code == "quota_exhausted":
                exhausted_state = select_quota_usage_state(access)
                raise B2BApiQuotaExceededError(
                    code="b2b_api_quota_exceeded",
                    details={
                        "quota_key": exhausted_state.quota_key
                        if exhausted_state
                        else B2BApiEntitlementGate.FEATURE_CODE,
                        "used": str(exhausted_state.used)
                        if exhausted_state
                        else str(access.quota_used)
                        if access
                        else "0",
                        "limit": str(exhausted_state.quota_limit)
                        if exhausted_state
                        else str(access.quota_limit)
                        if access
                        else "0",
                        "reason_code": "quota_exhausted",
                    },
                )

            error_code = "b2b_api_access_denied"
            details: dict[str, str | int] = {"account_id": account_id, "reason_code": reason_code}
            if snapshot.plan_code == "none":
                error_code = "b2b_no_canonical_plan"
            elif reason_code == "feature_not_in_plan":
                error_code = "b2b_no_binding"
            elif reason_code == "binding_disabled":
                details["reason"] = "disabled_by_plan"
            elif reason_code == "billing_inactive":
                details["reason"] = "billing_inactive"
            else:
                details["reason"] = reason_code

            raise B2BApiAccessDeniedError(
                code=error_code,
                details=details,
            )

        if access.access_mode == "unlimited":
            return B2BApiEntitlementResult(path="canonical_unlimited")

        # access_mode == "quota" — consommer
        consumed_states: list[UsageState] = []
        for state in access.usage_states:
            quota_def = QuotaDefinition(
                quota_key=state.quota_key,
                quota_limit=state.quota_limit,
                period_unit=state.period_unit,
                period_value=state.period_value,
                reset_mode=state.reset_mode,
            )
            try:
                new_state = EnterpriseQuotaUsageService.consume(
                    db,
                    account_id=account_id,
                    feature_code=B2BApiEntitlementGate.FEATURE_CODE,
                    quota=quota_def,
                    amount=1,
                )
                consumed_states.append(new_state)
            except QuotaExhaustedError as exc:
                raise B2BApiQuotaExceededError(
                    code="b2b_api_quota_exceeded",
                    details={
                        "quota_key": exc.quota_key,
                        "used": str(exc.used),
                        "limit": str(exc.limit),
                    },
                ) from exc

        return B2BApiEntitlementResult(path="canonical_quota", usage_states=consumed_states)

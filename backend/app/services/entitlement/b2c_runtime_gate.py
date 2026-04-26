"""Factorise la logique commune des gates B2C runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from app.services.entitlement.effective_entitlement_gate_helpers import (
    map_b2c_reason_to_legacy,
    select_quota_usage_state,
)
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import QuotaDefinition, UsageState
from app.services.quota.usage_service import QuotaExhaustedError, QuotaUsageService


@dataclass(frozen=True)
class B2CAccessSnapshot:
    """Expose le resultat commun de resolution d acces B2C."""

    path: str
    plan_code: str
    variant_code: str | None
    usage_states: list[UsageState]


def resolve_b2c_access(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    denied_error_factory: Callable[[str, str, str, str | None], Exception],
    quota_error_factory: Callable[[str, int, int, datetime | None], Exception],
) -> B2CAccessSnapshot:
    """Resout l acces B2C et normalise les erreurs d acces ou de quota."""
    snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
        db,
        app_user_id=user_id,
    )
    access = snapshot.entitlements.get(feature_code)

    if not access or not access.granted:
        reason_code = access.reason_code if access else "subject_not_eligible"
        if reason_code == "quota_exhausted":
            exhausted_state = select_quota_usage_state(access)
            quota_key = exhausted_state.quota_key if exhausted_state else feature_code
            used = exhausted_state.used if exhausted_state else (access.quota_used if access else 0)
            limit = (
                exhausted_state.quota_limit
                if exhausted_state
                else (access.quota_limit if access else 0)
            )
            raise quota_error_factory(
                quota_key,
                used,
                limit,
                exhausted_state.window_end if exhausted_state else None,
            )

        raise denied_error_factory(
            map_b2c_reason_to_legacy(snapshot, access),
            snapshot.billing_status,
            snapshot.plan_code,
            reason_code,
        )

    path = "canonical_unlimited" if access.access_mode == "unlimited" else "canonical_quota"
    return B2CAccessSnapshot(
        path=path,
        plan_code=snapshot.plan_code,
        variant_code=access.variant_code,
        usage_states=access.usage_states,
    )


def consume_b2c_quota(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    usage_states: list[UsageState],
    quota_error_factory: Callable[[str, int, int, datetime | None], Exception],
    skip_quota_keys: set[str] | None = None,
) -> list[UsageState]:
    """Consomme les quotas applicables pour une feature B2C."""
    consumed_states: list[UsageState] = []
    skipped_keys = skip_quota_keys or set()

    for state in usage_states:
        if state.quota_key in skipped_keys:
            continue

        quota_definition = QuotaDefinition(
            quota_key=state.quota_key,
            quota_limit=state.quota_limit,
            period_unit=state.period_unit,
            period_value=state.period_value,
            reset_mode=state.reset_mode,
        )
        try:
            consumed_states.append(
                QuotaUsageService.consume(
                    db,
                    user_id=user_id,
                    feature_code=feature_code,
                    quota=quota_definition,
                    amount=1,
                )
            )
        except QuotaExhaustedError as exc:
            raise quota_error_factory(
                exc.quota_key,
                exc.used,
                exc.limit,
                state.window_end,
            ) from exc

    return consumed_states

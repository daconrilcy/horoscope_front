from __future__ import annotations

from app.services.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
    UsageState,
)


def map_b2c_reason_to_legacy(
    snapshot: EffectiveEntitlementsSnapshot,
    access: EffectiveFeatureAccess | None,
) -> str:
    reason_code = access.reason_code if access else "subject_not_eligible"
    if reason_code == "feature_not_in_plan":
        return "no_plan" if snapshot.plan_code == "none" else "canonical_no_binding"
    if reason_code == "binding_disabled":
        return "disabled_by_plan"
    return reason_code


def select_quota_usage_state(access: EffectiveFeatureAccess | None) -> UsageState | None:
    if access is None or not access.usage_states:
        return None

    exhausted_states = [state for state in access.usage_states if state.exhausted]
    if exhausted_states:
        return sorted(
            exhausted_states,
            key=lambda state: (state.quota_key, state.period_unit, state.period_value),
        )[0]

    matching_states = [
        state
        for state in access.usage_states
        if state.used == access.quota_used and state.quota_limit == access.quota_limit
    ]
    if matching_states:
        return sorted(
            matching_states,
            key=lambda state: (state.quota_key, state.period_unit, state.period_value),
        )[0]

    return sorted(
        access.usage_states,
        key=lambda state: (state.remaining, state.quota_key, state.period_unit, state.period_value),
    )[0]

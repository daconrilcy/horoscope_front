from __future__ import annotations

from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.services.canonical_entitlement.suppression.rule import (
    CanonicalEntitlementAlertSuppressionRuleService,
)


def _build_rule(
    rule_id: int,
    *,
    alert_kind: str = "sla_overdue",
    feature_code: str | None = None,
    plan_code: str | None = None,
    actor_type: str | None = None,
    is_active: bool = True,
) -> CanonicalEntitlementMutationAlertSuppressionRuleModel:
    return CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=rule_id,
        alert_kind=alert_kind,
        feature_code=feature_code,
        plan_code=plan_code,
        actor_type=actor_type,
        is_active=is_active,
        suppression_key=f"rule-{rule_id}",
        ops_comment=f"comment-{rule_id}",
    )


def _build_event(
    event_id: int,
    *,
    alert_kind: str = "sla_overdue",
    feature_code: str = "feature-a",
    plan_code: str = "premium",
    actor_type: str = "user",
) -> CanonicalEntitlementMutationAlertEventModel:
    return CanonicalEntitlementMutationAlertEventModel(
        id=event_id,
        audit_id=1,
        dedupe_key=f"dedupe-{event_id}",
        alert_kind=alert_kind,
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot=feature_code,
        plan_id_snapshot=1,
        plan_code_snapshot=plan_code,
        actor_type_snapshot=actor_type,
        actor_identifier_snapshot="user@test.com",
        age_seconds_snapshot=42,
        delivery_channel="webhook",
        delivery_status="failed",
        payload={"event_id": event_id},
    )


def test_match_event_returns_none_when_no_rule_matches() -> None:
    event = _build_event(1, feature_code="feature-x")
    rules = [_build_rule(1, feature_code="feature-a")]

    assert (
        CanonicalEntitlementAlertSuppressionRuleService.match_event(
            event,
            active_rules=rules,
        )
        is None
    )


def test_match_event_matches_on_alert_kind_only() -> None:
    event = _build_event(1)
    rules = [_build_rule(1)]

    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
        event,
        active_rules=rules,
    )

    assert match is not None
    assert match.rule_id == 1
    assert match.source == "rule"


def test_match_event_prefers_more_specific_rule() -> None:
    event = _build_event(1)
    rules = [
        _build_rule(1),
        _build_rule(2, feature_code="feature-a"),
        _build_rule(3, feature_code="feature-a", plan_code="premium"),
    ]

    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
        event,
        active_rules=rules,
    )

    assert match is not None
    assert match.rule_id == 3


def test_match_event_tie_breaks_on_lowest_rule_id() -> None:
    event = _build_event(1)
    rules = [
        _build_rule(10, feature_code="feature-a"),
        _build_rule(5, feature_code="feature-a"),
    ]

    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
        event,
        active_rules=rules,
    )

    assert match is not None
    assert match.rule_id == 5


def test_match_events_returns_mapping_by_alert_event_id() -> None:
    events = [
        _build_event(1, feature_code="feature-a"),
        _build_event(2, feature_code="feature-b"),
    ]
    rules = [_build_rule(1, feature_code="feature-a")]

    matches = CanonicalEntitlementAlertSuppressionRuleService.match_events(
        events,
        active_rules=rules,
    )

    assert list(matches) == [1]
    assert matches[1].rule_id == 1


def test_manual_handling_still_has_priority_over_rule() -> None:
    event = _build_event(1)
    rule_match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
        event,
        active_rules=[_build_rule(1)],
    )
    manual_handling = CanonicalEntitlementMutationAlertHandlingModel(
        alert_event_id=event.id,
        handling_status="resolved",
        handled_by_user_id=99,
        ops_comment="resolved manually",
    )

    assert rule_match is not None
    assert manual_handling.handling_status == "resolved"
    assert rule_match.rule_id == 1


def test_load_active_rules_excludes_inactive_rules(db_session) -> None:
    active_rule = _build_rule(1, is_active=True)
    inactive_rule = _build_rule(2, feature_code="feature-b", is_active=False)
    db_session.add_all([active_rule, inactive_rule])
    db_session.commit()

    rules = CanonicalEntitlementAlertSuppressionRuleService.load_active_rules(db_session)

    assert [rule.id for rule in rules] == [1]

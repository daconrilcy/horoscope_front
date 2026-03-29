import pytest
from unittest.mock import MagicMock
from app.services.canonical_entitlement_alert_suppression_rule_service import (
    CanonicalEntitlementAlertSuppressionRuleService,
    MatchedAlertSuppressionRule
)
from app.infra.db.models.canonical_entitlement_mutation_alert_suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel
)

def test_match_event_specificity_priority():
    # Setup rules with different specificities
    rule1 = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=1, alert_kind="audit_failed", feature_code=None, plan_code=None, actor_type=None
    )
    rule2 = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=2, alert_kind="audit_failed", feature_code="feat1", plan_code=None, actor_type=None
    )
    rule3 = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=3, alert_kind="audit_failed", feature_code="feat1", plan_code="plan1", actor_type=None
    )
    
    active_rules = [rule1, rule2, rule3]
    
    # Event that matches all 3
    event = CanonicalEntitlementMutationAlertEventModel(
        alert_kind="audit_failed",
        feature_code_snapshot="feat1",
        plan_code_snapshot="plan1",
        actor_type_snapshot="user"
    )
    
    # Should match rule3 (highest specificity)
    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(event, active_rules=active_rules)
    assert match is not None
    assert match.rule_id == 3

def test_match_event_tie_break_on_id():
    # Rules with same specificity
    rule10 = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=10, alert_kind="audit_failed", feature_code="feat1", plan_code=None, actor_type=None
    )
    rule5 = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=5, alert_kind="audit_failed", feature_code="feat1", plan_code=None, actor_type=None
    )
    
    active_rules = [rule10, rule5]
    
    event = CanonicalEntitlementMutationAlertEventModel(
        alert_kind="audit_failed",
        feature_code_snapshot="feat1",
        plan_code_snapshot="other",
        actor_type_snapshot="user"
    )
    
    # Should match rule5 (lowest id)
    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(event, active_rules=active_rules)
    assert match is not None
    assert match.rule_id == 5

def test_match_event_no_match():
    rule = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        id=1, alert_kind="audit_failed", feature_code="feat1", plan_code=None, actor_type=None
    )
    
    active_rules = [rule]
    
    event = CanonicalEntitlementMutationAlertEventModel(
        alert_kind="audit_failed",
        feature_code_snapshot="feat2", # Different
        plan_code_snapshot="plan1",
        actor_type_snapshot="user"
    )
    
    match = CanonicalEntitlementAlertSuppressionRuleService.match_event(event, active_rules=active_rules)
    assert match is None

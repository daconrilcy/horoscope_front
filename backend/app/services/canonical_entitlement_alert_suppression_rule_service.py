from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)

if TYPE_CHECKING:
    from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
        CanonicalEntitlementMutationAlertEventModel,
    )


@dataclass
class MatchedAlertSuppressionRule:
    rule_id: int
    suppression_key: str | None
    ops_comment: str | None
    source: str = "rule"


class CanonicalEntitlementAlertSuppressionRuleService:
    @staticmethod
    def load_active_rules(
        db: Session,
        *,
        alert_kind: Optional[str] = None,
    ) -> List[CanonicalEntitlementMutationAlertSuppressionRuleModel]:
        stmt = select(CanonicalEntitlementMutationAlertSuppressionRuleModel).where(
            CanonicalEntitlementMutationAlertSuppressionRuleModel.is_active == True
        )
        if alert_kind:
            stmt = stmt.where(
                CanonicalEntitlementMutationAlertSuppressionRuleModel.alert_kind == alert_kind
            )
        
        # We sort by specificity in the service logic, but we can also order by id here as a secondary sort
        stmt = stmt.order_by(CanonicalEntitlementMutationAlertSuppressionRuleModel.id.asc())
        
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def match_event(
        event: CanonicalEntitlementMutationAlertEventModel,
        *,
        active_rules: List[CanonicalEntitlementMutationAlertSuppressionRuleModel],
    ) -> Optional[MatchedAlertSuppressionRule]:
        # Filter rules by alert_kind first
        candidate_rules = [
            rule for rule in active_rules if rule.alert_kind == event.alert_kind
        ]
        
        best_rule: Optional[CanonicalEntitlementMutationAlertSuppressionRuleModel] = None
        best_score = -1

        for rule in candidate_rules:
            # Check criteria
            if rule.feature_code and rule.feature_code != event.feature_code_snapshot:
                continue
            if rule.plan_code and rule.plan_code != event.plan_code_snapshot:
                continue
            if rule.actor_type and rule.actor_type != event.actor_type_snapshot:
                continue
            
            # It matches. Calculate score.
            # alert_kind is always matched if we reach here.
            score = 0
            if rule.feature_code:
                score += 1
            if rule.plan_code:
                score += 1
            if rule.actor_type:
                score += 1
            
            # Specificity priority
            if score > best_score:
                best_score = score
                best_rule = rule
            elif score == best_score:
                # Tie-break on lowest id
                if best_rule is None or rule.id < best_rule.id:
                    best_rule = rule
        
        if best_rule:
            return MatchedAlertSuppressionRule(
                rule_id=best_rule.id,
                suppression_key=best_rule.suppression_key,
                ops_comment=best_rule.ops_comment,
            )
        
        return None

    @staticmethod
    def match_events(
        events: List[CanonicalEntitlementMutationAlertEventModel],
        *,
        active_rules: List[CanonicalEntitlementMutationAlertSuppressionRuleModel],
    ) -> Dict[int, MatchedAlertSuppressionRule]:
        results: Dict[int, MatchedAlertSuppressionRule] = {}
        for event in events:
            match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
                event, active_rules=active_rules
            )
            if match:
                results[event.id] = match
        return results

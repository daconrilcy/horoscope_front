# Service de résolution des règles de suppression entitlement mutation.
"""Expose la sélection canonique de la meilleure règle applicable à une alerte."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)

if TYPE_CHECKING:
    from app.infra.db.models.entitlement_mutation.alert.alert_event import (
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
        alert_kind: str | None = None,
    ) -> list[CanonicalEntitlementMutationAlertSuppressionRuleModel]:
        stmt = select(CanonicalEntitlementMutationAlertSuppressionRuleModel).where(
            CanonicalEntitlementMutationAlertSuppressionRuleModel.is_active.is_(True)
        )
        if alert_kind:
            stmt = stmt.where(
                CanonicalEntitlementMutationAlertSuppressionRuleModel.alert_kind == alert_kind
            )

        stmt = stmt.order_by(CanonicalEntitlementMutationAlertSuppressionRuleModel.id.asc())

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def match_event(
        event: CanonicalEntitlementMutationAlertEventModel,
        *,
        active_rules: list[CanonicalEntitlementMutationAlertSuppressionRuleModel],
    ) -> MatchedAlertSuppressionRule | None:
        candidate_rules = [rule for rule in active_rules if rule.alert_kind == event.alert_kind]

        best_rule: CanonicalEntitlementMutationAlertSuppressionRuleModel | None = None
        best_score = -1

        for rule in candidate_rules:
            if rule.feature_code and rule.feature_code != event.feature_code_snapshot:
                continue
            if rule.plan_code and rule.plan_code != event.plan_code_snapshot:
                continue
            if rule.actor_type and rule.actor_type != event.actor_type_snapshot:
                continue

            score = 0
            if rule.feature_code:
                score += 1
            if rule.plan_code:
                score += 1
            if rule.actor_type:
                score += 1

            if score > best_score:
                best_score = score
                best_rule = rule
            elif score == best_score:
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
        events: list[CanonicalEntitlementMutationAlertEventModel],
        *,
        active_rules: list[CanonicalEntitlementMutationAlertSuppressionRuleModel],
    ) -> dict[int, MatchedAlertSuppressionRule]:
        results: dict[int, MatchedAlertSuppressionRule] = {}
        for event in events:
            match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
                event, active_rules=active_rules
            )
            if match:
                results[event.id] = match
        return results

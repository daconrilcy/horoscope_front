# Service de matérialisation des suppressions effectives d'alertes.
"""Centralise l'écriture relationnelle des suppressions manuelles et issues des règles."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.services.canonical_entitlement.suppression.rule import (
    CanonicalEntitlementAlertSuppressionRuleService,
    MatchedAlertSuppressionRule,
)


class CanonicalEntitlementAlertSuppressionApplicationService:
    """Assure une trace canonique unique des suppressions effectivement appliquées."""

    @staticmethod
    def match_and_ensure_rule_application(
        db: Session,
        *,
        alert_event: CanonicalEntitlementMutationAlertEventModel,
        active_rules: list[CanonicalEntitlementMutationAlertSuppressionRuleModel],
        request_id: str | None = None,
        applied_at: datetime | None = None,
    ) -> MatchedAlertSuppressionRule | None:
        """Résout la règle applicable et matérialise sa trace relationnelle si nécessaire."""

        rule_match = CanonicalEntitlementAlertSuppressionRuleService.match_event(
            alert_event,
            active_rules=active_rules,
        )
        if rule_match is None:
            return None

        CanonicalEntitlementAlertSuppressionApplicationService.ensure_rule_application(
            db,
            alert_event=alert_event,
            rule_match=rule_match,
            request_id=request_id,
            applied_at=applied_at,
        )
        return rule_match

    @staticmethod
    def ensure_manual_application(
        db: Session,
        *,
        alert_event_id: int,
        suppression_key: str | None,
        ops_comment: str | None,
        handled_by_user_id: int | None,
        request_id: str | None = None,
        applied_at: datetime | None = None,
    ) -> CanonicalEntitlementMutationAlertSuppressionApplicationModel:
        """Crée une trace d'application manuelle pour un handling de suppression."""

        application = CanonicalEntitlementMutationAlertSuppressionApplicationModel(
            alert_event_id=alert_event_id,
            suppression_key=suppression_key,
            application_mode="manual",
            application_reason=ops_comment,
            applied_by_user_id=handled_by_user_id,
            request_id=request_id,
            applied_at=applied_at or datetime_provider.utcnow(),
        )
        db.add(application)
        db.flush()
        return application

    @staticmethod
    def ensure_rule_application(
        db: Session,
        *,
        alert_event: CanonicalEntitlementMutationAlertEventModel,
        rule_match: MatchedAlertSuppressionRule,
        request_id: str | None = None,
        applied_at: datetime | None = None,
    ) -> CanonicalEntitlementMutationAlertSuppressionApplicationModel:
        """Crée ou met à jour la trace d'application d'une règle pour une alerte donnée."""

        application = db.execute(
            select(CanonicalEntitlementMutationAlertSuppressionApplicationModel).where(
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.alert_event_id
                == alert_event.id,
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.suppression_rule_id
                == rule_match.rule_id,
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.application_mode
                == "rule",
            )
        ).scalar_one_or_none()

        effective_applied_at = applied_at or datetime_provider.utcnow()
        if application is None:
            application = CanonicalEntitlementMutationAlertSuppressionApplicationModel(
                alert_event_id=alert_event.id,
                suppression_rule_id=rule_match.rule_id,
                suppression_key=rule_match.suppression_key,
                application_mode="rule",
                application_reason=rule_match.ops_comment,
                request_id=request_id,
                applied_at=effective_applied_at,
            )
            db.add(application)
            db.flush()
            return application

        application.suppression_key = rule_match.suppression_key
        application.application_reason = rule_match.ops_comment
        application.request_id = request_id
        return application

    @staticmethod
    def apply_rule_to_matching_alerts(
        db: Session,
        *,
        rule: CanonicalEntitlementMutationAlertSuppressionRuleModel,
        request_id: str | None = None,
        applied_at: datetime | None = None,
    ) -> int:
        """Matérialise une trace pour chaque alerte effectivement supprimée par la règle."""

        if not rule.is_active:
            return 0

        alert_model = CanonicalEntitlementMutationAlertEventModel
        handling_model = CanonicalEntitlementMutationAlertHandlingModel
        query = select(alert_model).where(alert_model.alert_kind == rule.alert_kind)
        if rule.feature_code is not None:
            query = query.where(alert_model.feature_code_snapshot == rule.feature_code)
        if rule.plan_code is not None:
            query = query.where(alert_model.plan_code_snapshot == rule.plan_code)
        if rule.actor_type is not None:
            query = query.where(alert_model.actor_type_snapshot == rule.actor_type)
        query = query.where(
            ~select(handling_model.alert_event_id)
            .where(handling_model.alert_event_id == alert_model.id)
            .exists()
        )
        events = list(db.execute(query).scalars().all())
        applied_count = 0
        for event in events:
            CanonicalEntitlementAlertSuppressionApplicationService.ensure_rule_application(
                db,
                alert_event=event,
                rule_match=MatchedAlertSuppressionRule(
                    rule_id=rule.id,
                    suppression_key=rule.suppression_key,
                    ops_comment=rule.ops_comment,
                ),
                request_id=request_id,
                applied_at=applied_at,
            )
            applied_count += 1
        return applied_count

    @staticmethod
    def active_rule_application_event_ids_subquery():
        """Retourne la sous-requête des alertes couvertes par une suppression de règle active."""

        return (
            select(CanonicalEntitlementMutationAlertSuppressionApplicationModel.alert_event_id)
            .join(
                CanonicalEntitlementMutationAlertSuppressionRuleModel,
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.suppression_rule_id
                == CanonicalEntitlementMutationAlertSuppressionRuleModel.id,
            )
            .where(
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.application_mode
                == "rule",
                CanonicalEntitlementMutationAlertSuppressionRuleModel.is_active.is_(True),
            )
        )

    @staticmethod
    def load_active_rule_applications_by_event_ids(
        db: Session,
        *,
        event_ids: list[int],
    ) -> dict[int, CanonicalEntitlementMutationAlertSuppressionApplicationModel]:
        """Charge la dernière suppression de règle active connue par alerte."""

        if not event_ids:
            return {}

        applications = list(
            db.execute(
                select(CanonicalEntitlementMutationAlertSuppressionApplicationModel)
                .join(
                    CanonicalEntitlementMutationAlertSuppressionRuleModel,
                    CanonicalEntitlementMutationAlertSuppressionApplicationModel.suppression_rule_id
                    == CanonicalEntitlementMutationAlertSuppressionRuleModel.id,
                )
                .where(
                    CanonicalEntitlementMutationAlertSuppressionApplicationModel.alert_event_id.in_(
                        event_ids
                    ),
                    CanonicalEntitlementMutationAlertSuppressionApplicationModel.application_mode
                    == "rule",
                    CanonicalEntitlementMutationAlertSuppressionRuleModel.is_active.is_(True),
                )
                .order_by(
                    CanonicalEntitlementMutationAlertSuppressionApplicationModel.applied_at.desc(),
                    CanonicalEntitlementMutationAlertSuppressionApplicationModel.id.desc(),
                )
            )
            .scalars()
            .all()
        )

        latest_by_event_id: dict[
            int, CanonicalEntitlementMutationAlertSuppressionApplicationModel
        ] = {}
        for application in applications:
            latest_by_event_id.setdefault(application.alert_event_id, application)
        return latest_by_event_id

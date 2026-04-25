# Service d'émission initiale des alertes entitlement mutation.
"""Construit et persiste les alertes SLA tout en alimentant leur cycle de vie courant."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.services.canonical_entitlement.audit.audit_query import (
    CanonicalEntitlementMutationAuditQueryService,
)
from app.services.canonical_entitlement.audit.review_queue import (
    CanonicalEntitlementReviewQueueService,
    ReviewQueueRow,
)
from app.services.canonical_entitlement.shared.alert_delivery_runtime import (
    CanonicalEntitlementAlertDeliveryRuntime,
)
from app.services.canonical_entitlement.suppression.application import (
    CanonicalEntitlementAlertSuppressionApplicationService,
)
from app.services.canonical_entitlement.suppression.rule import (
    CanonicalEntitlementAlertSuppressionRuleService,
)

logger = logging.getLogger(__name__)


@dataclass
class AlertRunResult:
    """Résume une exécution d'émission des alertes SLA."""

    sql_count: int
    candidate_count: int
    emitted_count: int
    skipped_duplicate_count: int
    failed_count: int
    dry_run: bool


class CanonicalEntitlementAlertService:
    """Émet les alertes SLA initiales à partir de la review queue canonique."""

    @staticmethod
    def emit_sla_alerts(
        db: Session,
        *,
        now_utc: datetime | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        limit: int | None = None,
    ) -> AlertRunResult:
        if now_utc is None:
            now_utc = datetime_provider.utcnow()

        if not settings.ops_review_queue_alerts_enabled:
            logger.info("ops_review_queue_alerts_disabled")
            return AlertRunResult(0, 0, 0, 0, 0, dry_run)

        _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
            db,
            page=1,
            page_size=1,
        )
        max_sql_rows = max(settings.ops_review_queue_alert_max_candidates, limit or 0, 1)
        active_rules = CanonicalEntitlementAlertSuppressionRuleService.load_active_rules(db)

        # 1. Charger tous les candidats potentiels (SLA status is not None)
        # On ne filtre pas encore sur sla_status=overdue/due_soon via SQL pour réutiliser
        # le service read-only qui charge aussi les reviews et calcule le SLA.
        all_rows = CanonicalEntitlementReviewQueueService.build_review_queue_rows(
            db,
            now_utc=now_utc,
            max_sql_rows=max_sql_rows,
        )

        # 2. Filtrer les candidats
        candidates: list[ReviewQueueRow] = []
        for row in all_rows:
            # Filtrer sla_status in {"due_soon", "overdue"}
            if row.sla_status not in {"due_soon", "overdue"}:
                continue
            # Exclusion : effective_review_status in {"closed", "expected"}
            if row.effective_review_status in {"closed", "expected"}:
                continue
            candidates.append(row)

        if limit is not None:
            candidates = candidates[:limit]
        candidate_count = len(candidates)

        if candidate_count == 0:
            return AlertRunResult(sql_count, 0, 0, 0, 0, dry_run)

        # 3. Charger dedupe_keys existants en batch
        candidate_dedupe_keys = [
            CanonicalEntitlementAlertService._build_dedupe_key(row) for row in candidates
        ]
        existing_keys_result = db.execute(
            select(CanonicalEntitlementMutationAlertEventModel.dedupe_key).where(
                CanonicalEntitlementMutationAlertEventModel.dedupe_key.in_(candidate_dedupe_keys)
            )
        )
        existing_keys = {r[0] for r in existing_keys_result.all()}

        emitted_count = 0
        skipped_duplicate_count = 0
        failed_count = 0

        for row in candidates:
            dedupe_key = CanonicalEntitlementAlertService._build_dedupe_key(row)
            if dedupe_key in existing_keys:
                skipped_duplicate_count += 1
                continue

            if dry_run:
                emitted_count += 1
                continue

            # 4. Tentative d'émission (avec savepoint pour IntegrityError)
            try:
                with db.begin_nested():
                    # Créer l'event initial (pending delivery)
                    alert_kind = "sla_due_soon" if row.sla_status == "due_soon" else "sla_overdue"

                    payload = CanonicalEntitlementAlertService._build_payload(row, request_id)

                    event = CanonicalEntitlementMutationAlertEventModel(
                        audit_id=row.audit.id,
                        dedupe_key=dedupe_key,
                        alert_kind=alert_kind,
                        alert_status="open",
                        risk_level_snapshot=row.diff.risk_level,
                        review_status_snapshot=row.effective_review_status,
                        feature_code_snapshot=row.audit.feature_code,
                        plan_id_snapshot=row.audit.plan_id,
                        plan_code_snapshot=row.audit.plan_code_snapshot,
                        actor_type_snapshot=row.audit.actor_type,
                        actor_identifier_snapshot=row.audit.actor_identifier,
                        sla_target_seconds_snapshot=row.sla_target_seconds,
                        due_at_snapshot=row.due_at,
                        age_seconds_snapshot=row.age_seconds,
                        delivery_channel="log",  # Default, updated below
                        last_delivery_status="sent",  # Default, updated below
                        request_id=request_id,
                        payload=payload,
                        delivery_attempt_count=1,
                    )
                    db.add(event)
                    db.flush()
                    CanonicalEntitlementAlertSuppressionApplicationService.match_and_ensure_rule_application(
                        db,
                        alert_event=event,
                        active_rules=active_rules,
                        request_id=request_id,
                    )

                    # 5. Delivery
                    outcome = CanonicalEntitlementAlertDeliveryRuntime.deliver_payload(
                        payload,
                        log_message="ops_review_queue_alert_log_delivery",
                        delivered_at=now_utc,
                    )
                    CanonicalEntitlementAlertDeliveryRuntime.apply_delivery_state(
                        alert_event=event,
                        outcome=outcome,
                        attempt_number=1,
                        updated_at=now_utc,
                    )
                    if outcome.status == "sent":
                        emitted_count += 1
                    else:
                        failed_count += 1

            except IntegrityError:
                # Race condition handled
                skipped_duplicate_count += 1
                continue
            except Exception:
                logger.exception(
                    "ops_review_queue_alert_unexpected_error audit_id=%s", row.audit.id
                )
                failed_count += 1
                continue

        return AlertRunResult(
            sql_count=sql_count,
            candidate_count=candidate_count,
            emitted_count=emitted_count,
            skipped_duplicate_count=skipped_duplicate_count,
            failed_count=failed_count,
            dry_run=dry_run,
        )

    @staticmethod
    def _build_dedupe_key(row: ReviewQueueRow) -> str:
        status_str = row.effective_review_status or "none"
        return f"audit:{row.audit.id}:review:{status_str}:sla:{row.sla_status}"

    @staticmethod
    def _build_payload(row: ReviewQueueRow, request_id: str | None) -> dict[str, Any]:
        alert_kind = "sla_due_soon" if row.sla_status == "due_soon" else "sla_overdue"
        payload = {
            "alert_kind": alert_kind,
            "audit_id": row.audit.id,
            "feature_code": row.audit.feature_code,
            "plan_id": row.audit.plan_id,
            "plan_code": row.audit.plan_code_snapshot,
            "risk_level": row.diff.risk_level,
            "effective_review_status": row.effective_review_status,
            "sla_status": row.sla_status,
            "age_seconds": row.age_seconds,
            "age_hours": row.age_hours,
            "due_at": row.due_at.isoformat() if row.due_at else None,
            "actor_type": row.audit.actor_type,
            "actor_identifier": row.audit.actor_identifier,
            "request_id": request_id,
        }

        if settings.ops_review_queue_alert_base_url:
            base = settings.ops_review_queue_alert_base_url.rstrip("/")
            payload["queue_url"] = f"{base}/v1/ops/entitlements/mutation-audits/review-queue"
            payload["detail_url"] = f"{base}/v1/ops/entitlements/mutation-audits/{row.audit.id}"

        return payload

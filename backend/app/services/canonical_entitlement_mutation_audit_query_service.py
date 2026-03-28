from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)


class CanonicalEntitlementMutationAuditQueryService:
    @staticmethod
    def list_mutation_audits(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 20,
        plan_id: int | None = None,
        plan_code: str | None = None,
        feature_code: str | None = None,
        actor_type: str | None = None,
        actor_identifier: str | None = None,
        source_origin: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[CanonicalEntitlementMutationAuditModel], int]:
        q = select(CanonicalEntitlementMutationAuditModel)
        if plan_id is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.plan_id == plan_id)
        if plan_code is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.plan_code_snapshot == plan_code)
        if feature_code is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.feature_code == feature_code)
        if actor_type is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.actor_type == actor_type)
        if actor_identifier is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.actor_identifier == actor_identifier)
        if source_origin is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.source_origin == source_origin)
        if request_id is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.request_id == request_id)
        if date_from is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.occurred_at >= date_from)
        if date_to is not None:
            q = q.where(CanonicalEntitlementMutationAuditModel.occurred_at <= date_to)

        count_q = select(func.count()).select_from(q.subquery())
        total_count = db.scalar(count_q) or 0

        q = (
            q.order_by(
                CanonicalEntitlementMutationAuditModel.occurred_at.desc(),
                CanonicalEntitlementMutationAuditModel.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(db.scalars(q).all())
        return items, total_count

    @staticmethod
    def get_mutation_audit_by_id(
        db: Session, audit_id: int
    ) -> CanonicalEntitlementMutationAuditModel | None:
        return db.get(CanonicalEntitlementMutationAuditModel, audit_id)

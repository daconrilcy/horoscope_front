from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review_event import (
    CanonicalEntitlementMutationAuditReviewEventModel,
)


class AuditNotFoundError(Exception):
    def __init__(self, audit_id: int) -> None:
        self.audit_id = audit_id
        super().__init__(f"Audit {audit_id} not found")


class CanonicalEntitlementMutationAuditReviewService:
    @staticmethod
    def upsert_review(
        db: Session,
        *,
        audit_id: int,
        review_status: str,
        reviewed_by_user_id: int | None,
        review_comment: str | None,
        incident_key: str | None,
        request_id: str | None = None,
    ) -> CanonicalEntitlementMutationAuditReviewModel:
        audit = db.get(CanonicalEntitlementMutationAuditModel, audit_id)
        if audit is None:
            raise AuditNotFoundError(audit_id)

        now = datetime.now(timezone.utc)
        review = CanonicalEntitlementMutationAuditReviewService._get_review_by_audit_id(
            db, audit_id
        )

        is_creation = review is None
        previous_status = None if is_creation else review.review_status
        previous_comment = None if is_creation else review.review_comment
        previous_incident = None if is_creation else review.incident_key

        if is_creation:
            review = CanonicalEntitlementMutationAuditReviewModel(
                audit_id=audit_id,
                review_status=review_status,
                reviewed_by_user_id=reviewed_by_user_id,
                reviewed_at=now,
                review_comment=review_comment,
                incident_key=incident_key,
            )
            try:
                with db.begin_nested():
                    db.add(review)
                    db.flush()
            except IntegrityError:
                review = CanonicalEntitlementMutationAuditReviewService._get_review_by_audit_id(
                    db, audit_id
                )
                if review is None:
                    raise
                # Update attributes if concurrent insert happened
                review.review_status = review_status
                review.reviewed_by_user_id = reviewed_by_user_id
                review.reviewed_at = now
                review.review_comment = review_comment
                review.incident_key = incident_key
        else:
            # Detection no-op (uniquement sur update)
            is_noop = (
                previous_status == review_status
                and previous_comment == review_comment
                and previous_incident == incident_key
            )
            if is_noop:
                return review

            review.review_status = review_status
            review.reviewed_by_user_id = reviewed_by_user_id
            review.reviewed_at = now
            review.review_comment = review_comment
            review.incident_key = incident_key

        # INSERT événement (reached only if creation OR real change)
        event = CanonicalEntitlementMutationAuditReviewEventModel(
            audit_id=audit_id,
            previous_review_status=previous_status,
            new_review_status=review_status,
            previous_review_comment=previous_comment,
            new_review_comment=review_comment,
            previous_incident_key=previous_incident,
            new_incident_key=incident_key,
            reviewed_by_user_id=reviewed_by_user_id,
            occurred_at=now,
            request_id=request_id,
        )
        db.add(event)
        db.flush()
        return review

    @staticmethod
    def _get_review_by_audit_id(
        db: Session, audit_id: int
    ) -> CanonicalEntitlementMutationAuditReviewModel | None:
        result = db.execute(
            select(CanonicalEntitlementMutationAuditReviewModel).where(
                CanonicalEntitlementMutationAuditReviewModel.audit_id == audit_id
            )
        )
        return result.scalar_one_or_none()

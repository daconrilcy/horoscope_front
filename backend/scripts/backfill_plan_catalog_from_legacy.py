"""Backfill script to populate canonical plan catalog from legacy billing tables.

This script is idempotent and maps:
- billing_plans -> plan_catalog (B2C) + astrologer_chat quotas
- enterprise_billing_plans -> plan_catalog (B2B) + b2b_api_access quotas

Key guarantees:
- legacy DB is the source of truth for fields explicitly covered by the mapping spec
- manual canonical data is upgraded to migrated_* when a legacy match exists
- collisions on non-overridable origins are warned and not overwritten
- B2B included_monthly_units == 0 remains manual-review-required
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.enterprise_billing import EnterpriseBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.infra.db.session import SessionLocal
from app.services.canonical_entitlement.audit.mutation_service import (
    CanonicalEntitlementMutationService,
    CanonicalMutationContext,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


_BACKFILL_CONTEXT = CanonicalMutationContext(
    actor_type="script",
    actor_identifier="backfill_plan_catalog_from_legacy.py",
)


B2B_FEATURE_CODE = "b2b_api_access"
B2C_CHAT_FEATURE_CODE = "astrologer_chat"

SOURCE_BILLING = SourceOrigin.MIGRATED_FROM_BILLING_PLAN.value
SOURCE_ENTERPRISE = SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value
SOURCE_MANUAL = SourceOrigin.MANUAL.value


@dataclass
class BackfillReport:
    processed_b2c: int = 0
    processed_b2b: int = 0

    plans_created: int = 0
    plans_updated: int = 0
    plans_unchanged: int = 0
    plans_skipped: int = 0

    bindings_created: int = 0
    bindings_updated: int = 0
    bindings_unchanged: int = 0
    bindings_skipped: int = 0

    quotas_created: int = 0
    quotas_updated: int = 0
    quotas_deleted: int = 0
    quotas_unchanged: int = 0
    quotas_skipped: int = 0

    ignored_explicitly: list[str] = field(default_factory=list)
    non_migrated: list[str] = field(default_factory=list)
    manual_review_required: list[str] = field(default_factory=list)
    anomalies: list[str] = field(default_factory=list)
    unmatched_manual_plans: list[str] = field(default_factory=list)

    def add_ignored(self, item: str) -> None:
        if item not in self.ignored_explicitly:
            self.ignored_explicitly.append(item)

    def add_non_migrated(self, item: str) -> None:
        if item not in self.non_migrated:
            self.non_migrated.append(item)

    def add_manual_review(self, item: str) -> None:
        self.manual_review_required.append(item)

    def add_anomaly(self, item: str) -> None:
        self.anomalies.append(item)

    def add_unmatched_manual_plan(self, item: str) -> None:
        self.unmatched_manual_plans.append(item)


def ensure_b2b_feature(db: Session) -> FeatureCatalogModel:
    return _ensure_feature(
        db,
        feature_code=B2B_FEATURE_CODE,
        feature_name="B2B API Access",
        description="Accès volumétrique à l'API astrologique pour les comptes entreprise",
        is_metered=True,
    )


def ensure_b2c_chat_feature(db: Session) -> FeatureCatalogModel:
    return _ensure_feature(
        db,
        feature_code=B2C_CHAT_FEATURE_CODE,
        feature_name="Astrologer Chat",
        description="Messagerie avec un astrologue",
        is_metered=True,
    )


def _ensure_feature(
    db: Session,
    *,
    feature_code: str,
    feature_name: str,
    description: str,
    is_metered: bool,
) -> FeatureCatalogModel:
    feature = db.execute(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code)
    ).scalar_one_or_none()
    if feature is not None:
        return feature

    logger.info("Creating feature '%s'...", feature_code)
    feature = FeatureCatalogModel(
        feature_code=feature_code,
        feature_name=feature_name,
        description=description,
        is_metered=is_metered,
        is_active=True,
    )

    try:
        with db.begin_nested():
            db.add(feature)
            db.flush()
        return feature
    except IntegrityError:
        logger.info("Feature '%s' already exists, reusing existing row.", feature_code)
        return db.execute(
            select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == feature_code)
        ).scalar_one()


def _upsert_plan(
    db: Session,
    *,
    code: str,
    name: str,
    audience: Audience,
    source_type: str,
    source_id: int,
    is_active: bool,
    report: BackfillReport,
) -> PlanCatalogModel:
    plan = db.execute(
        select(PlanCatalogModel).where(PlanCatalogModel.plan_code == code)
    ).scalar_one_or_none()

    if plan is None:
        plan = PlanCatalogModel(
            plan_code=code,
            plan_name=name,
            audience=audience,
            source_type=source_type,
            source_id=source_id,
            is_active=is_active,
        )
        db.add(plan)
        report.plans_created += 1
        db.flush()
        return plan

    if plan.source_type not in {"manual", source_type}:
        msg = (
            f"Collision on plan '{code}': existing source_type='{plan.source_type}' "
            f"is not manual nor '{source_type}'. Skipping update."
        )
        logger.warning(msg)
        report.plans_skipped += 1
        report.add_anomaly(msg)
        return plan

    changed = (
        plan.plan_name != name
        or plan.audience != audience
        or plan.source_type != source_type
        or plan.source_id != source_id
        or plan.is_active != is_active
    )
    if changed:
        plan.plan_name = name
        plan.audience = audience
        plan.source_type = source_type
        plan.source_id = source_id
        plan.is_active = is_active
        report.plans_updated += 1
    else:
        report.plans_unchanged += 1

    db.flush()
    return plan


def _binding_snapshot(
    binding: PlanFeatureBindingModel | None,
) -> tuple[AccessMode, bool, str] | None:
    if binding is None:
        return None
    return (
        binding.access_mode,
        binding.is_enabled,
        str(binding.source_origin),
    )


def _quota_snapshot(
    quota: PlanFeatureQuotaModel | None,
) -> tuple[int, str] | None:
    if quota is None:
        return None
    return (
        quota.quota_limit,
        str(quota.source_origin),
    )


def _record_binding_report(
    report: BackfillReport,
    before: tuple[AccessMode, bool, str] | None,
    after: tuple[AccessMode, bool, str] | None,
) -> None:
    if before is None and after is not None:
        report.bindings_created += 1
    elif before is not None and after is not None and before != after:
        report.bindings_updated += 1
    elif before is not None and after is not None:
        report.bindings_unchanged += 1


def _record_quota_report(
    report: BackfillReport,
    *,
    before: tuple[int, str] | None,
    after: tuple[int, str] | None,
    deleted_count: int = 0,
) -> None:
    if before is None and after is not None:
        report.quotas_created += 1
    elif before is not None and after is not None and before != after:
        report.quotas_updated += 1
    elif before is not None and after is not None:
        report.quotas_unchanged += 1
    elif before is not None and after is None:
        report.quotas_deleted += max(deleted_count, 1)


def backfill_b2c_plans(db: Session, report: BackfillReport | None = None) -> None:
    report = report or BackfillReport()
    # Ensure chat feature exists (no change here)
    chat_feature = ensure_b2c_chat_feature(db)

    legacy_plans = db.execute(select(BillingPlanModel)).scalars().all()
    legacy_codes = {plan.code for plan in legacy_plans}

    for legacy in legacy_plans:
        report.processed_b2c += 1
        plan = _upsert_plan(
            db,
            code=legacy.code,
            name=legacy.display_name,
            audience=Audience.B2C,
            source_type=SOURCE_BILLING,
            source_id=legacy.id,
            is_active=legacy.is_active,
            report=report,
        )

        access_mode = AccessMode.QUOTA if legacy.daily_message_limit > 0 else AccessMode.DISABLED
        is_enabled = access_mode != AccessMode.DISABLED

        # Check existing binding for reporting purposes
        existing_binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == chat_feature.id,
            )
        )
        binding_before = _binding_snapshot(existing_binding)
        quota_before = None
        if existing_binding is not None:
            quota_before = _quota_snapshot(
                db.scalar(
                    select(PlanFeatureQuotaModel).where(
                        PlanFeatureQuotaModel.plan_feature_binding_id == existing_binding.id,
                        PlanFeatureQuotaModel.quota_key == "messages",
                        PlanFeatureQuotaModel.period_unit == PeriodUnit.DAY,
                        PlanFeatureQuotaModel.period_value == 1,
                        PlanFeatureQuotaModel.reset_mode == ResetMode.CALENDAR,
                    )
                )
            )
        existing_quota_count = (
            len(
                db.scalars(
                    select(PlanFeatureQuotaModel).where(
                        PlanFeatureQuotaModel.plan_feature_binding_id == existing_binding.id
                    )
                ).all()
            )
            if existing_binding is not None
            else 0
        )

        # Check collision before calling the service
        if existing_binding and existing_binding.source_origin not in {
            SOURCE_MANUAL,
            SOURCE_BILLING,
        }:
            msg = (
                f"Collision on binding plan_id={plan.id} feature_id={chat_feature.id}: "
                f"existing source_origin='{existing_binding.source_origin}'. Skipping."
            )
            logger.warning(msg)
            report.bindings_skipped += 1
            report.add_anomaly(msg)
            continue

        quotas = []
        if access_mode == AccessMode.QUOTA:
            quotas = [
                {
                    "quota_key": "messages",
                    "quota_limit": legacy.daily_message_limit,
                    "period_unit": PeriodUnit.DAY,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ]

        # Use the service for the final mutation
        CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
            db,
            plan=plan,
            feature_code=B2C_CHAT_FEATURE_CODE,
            is_enabled=is_enabled,
            access_mode=access_mode,
            quotas=quotas,
            source_origin=SourceOrigin.MIGRATED_FROM_BILLING_PLAN,
            mutation_context=_BACKFILL_CONTEXT,
        )

        updated_binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == chat_feature.id,
            )
        )
        assert updated_binding is not None
        binding_after = _binding_snapshot(updated_binding)
        quota_after = _quota_snapshot(
            db.scalar(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == updated_binding.id,
                    PlanFeatureQuotaModel.quota_key == "messages",
                    PlanFeatureQuotaModel.period_unit == PeriodUnit.DAY,
                    PlanFeatureQuotaModel.period_value == 1,
                    PlanFeatureQuotaModel.reset_mode == ResetMode.CALENDAR,
                )
            )
        )
        updated_quota_count = len(
            db.scalars(
                select(PlanFeatureQuotaModel).where(
                    PlanFeatureQuotaModel.plan_feature_binding_id == updated_binding.id
                )
            ).all()
        )

        _record_binding_report(report, binding_before, binding_after)
        _record_quota_report(
            report,
            before=quota_before,
            after=quota_after,
            deleted_count=max(existing_quota_count - updated_quota_count, 0),
        )
        if access_mode != AccessMode.QUOTA and quota_before is None and quota_after is None:
            report.quotas_unchanged += 1

        report.add_ignored("billing_plans.monthly_price_cents")
        report.add_ignored("billing_plans.currency")

    manual_plans = (
        db.execute(
            select(PlanCatalogModel).where(
                PlanCatalogModel.audience == Audience.B2C,
                PlanCatalogModel.source_type == "manual",
            )
        )
        .scalars()
        .all()
    )
    for manual_plan in manual_plans:
        if manual_plan.plan_code not in legacy_codes:
            msg = (
                f"B2C manual plan '{manual_plan.plan_code}' has no matching billing_plans.code; "
                "manual entry kept unchanged."
            )
            logger.info(msg)
            report.add_unmatched_manual_plan(msg)


def backfill_b2b_plans(db: Session, report: BackfillReport | None = None) -> None:
    report = report or BackfillReport()
    b2b_feature = ensure_b2b_feature(db)

    legacy_plans = db.execute(select(EnterpriseBillingPlanModel)).scalars().all()

    for legacy in legacy_plans:
        report.processed_b2b += 1
        plan = _upsert_plan(
            db,
            code=legacy.code,
            name=legacy.display_name,
            audience=Audience.B2B,
            source_type=SOURCE_ENTERPRISE,
            source_id=legacy.id,
            is_active=legacy.is_active,
            report=report,
        )

        # Check existing binding for reporting purposes
        existing_binding = db.scalar(
            select(PlanFeatureBindingModel).where(
                PlanFeatureBindingModel.plan_id == plan.id,
                PlanFeatureBindingModel.feature_id == b2b_feature.id,
            )
        )
        binding_before = _binding_snapshot(existing_binding)
        quota_before = None
        if existing_binding is not None:
            quota_before = _quota_snapshot(
                db.scalar(
                    select(PlanFeatureQuotaModel).where(
                        PlanFeatureQuotaModel.plan_feature_binding_id == existing_binding.id,
                        PlanFeatureQuotaModel.quota_key == "calls",
                        PlanFeatureQuotaModel.period_unit == PeriodUnit.MONTH,
                        PlanFeatureQuotaModel.period_value == 1,
                        PlanFeatureQuotaModel.reset_mode == ResetMode.CALENDAR,
                    )
                )
            )

        if legacy.included_monthly_units > 0:
            # Check collision before calling the service
            if existing_binding and existing_binding.source_origin not in {
                SOURCE_MANUAL,
                SOURCE_ENTERPRISE,
            }:
                msg = (
                    f"Collision on binding plan_id={plan.id} feature_id={b2b_feature.id}: "
                    f"existing source_origin='{existing_binding.source_origin}'. Skipping."
                )
                logger.warning(msg)
                report.bindings_skipped += 1
                report.add_anomaly(msg)
                continue

            quotas = [
                {
                    "quota_key": "calls",
                    "quota_limit": legacy.included_monthly_units,
                    "period_unit": PeriodUnit.MONTH,
                    "period_value": 1,
                    "reset_mode": ResetMode.CALENDAR,
                }
            ]

            # Use the service for mutation
            CanonicalEntitlementMutationService.upsert_plan_feature_configuration(
                db,
                plan=plan,
                feature_code=B2B_FEATURE_CODE,
                is_enabled=True,
                access_mode=AccessMode.QUOTA,
                quotas=quotas,
                source_origin=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN,
                mutation_context=_BACKFILL_CONTEXT,
            )

            updated_binding = db.scalar(
                select(PlanFeatureBindingModel).where(
                    PlanFeatureBindingModel.plan_id == plan.id,
                    PlanFeatureBindingModel.feature_id == b2b_feature.id,
                )
            )
            assert updated_binding is not None
            binding_after = _binding_snapshot(updated_binding)
            quota_after = _quota_snapshot(
                db.scalar(
                    select(PlanFeatureQuotaModel).where(
                        PlanFeatureQuotaModel.plan_feature_binding_id == updated_binding.id,
                        PlanFeatureQuotaModel.quota_key == "calls",
                        PlanFeatureQuotaModel.period_unit == PeriodUnit.MONTH,
                        PlanFeatureQuotaModel.period_value == 1,
                        PlanFeatureQuotaModel.reset_mode == ResetMode.CALENDAR,
                    )
                )
            )

            _record_binding_report(report, binding_before, binding_after)
            _record_quota_report(report, before=quota_before, after=quota_after)

        elif legacy.included_monthly_units == 0:
            msg = (
                f"enterprise_plan '{legacy.code}' (id={legacy.id}) -> included_monthly_units=0: "
                "manual-review-required as per spec."
            )
            logger.warning(msg)
            report.add_manual_review(msg)

            if existing_binding is not None and existing_binding.source_origin == SOURCE_ENTERPRISE:
                anomaly = (
                    f"enterprise_plan '{legacy.code}' (id={legacy.id}) still has migrated "
                    "b2b_api_access binding while included_monthly_units=0 is "
                    "manual-review-required."
                )
                logger.warning(anomaly)
                report.add_anomaly(anomaly)

        report.add_ignored("enterprise_billing_plans.monthly_fixed_cents")
        report.add_ignored("enterprise_billing_plans.overage_unit_price_cents")
        report.add_ignored("enterprise_billing_plans.currency")


def run_backfill() -> None:
    logger.info("=== BACKFILL PLAN CATALOG FROM LEGACY START ===")
    report = BackfillReport()

    with SessionLocal() as db:
        try:
            backfill_b2c_plans(db, report)
            backfill_b2b_plans(db, report)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Backfill failed: %s", exc)
            raise

    logger.info("B2C plans processed: %s", report.processed_b2c)
    logger.info("B2B plans processed: %s", report.processed_b2b)
    logger.info(
        "Plans: %s created, %s updated, %s unchanged, %s skipped",
        report.plans_created,
        report.plans_updated,
        report.plans_unchanged,
        report.plans_skipped,
    )
    logger.info(
        "Bindings: %s created, %s updated, %s unchanged, %s skipped",
        report.bindings_created,
        report.bindings_updated,
        report.bindings_unchanged,
        report.bindings_skipped,
    )
    logger.info(
        "Quotas: %s created, %s updated, %s deleted, %s unchanged, %s skipped",
        report.quotas_created,
        report.quotas_updated,
        report.quotas_deleted,
        report.quotas_unchanged,
        report.quotas_skipped,
    )
    logger.info(
        "Ignored explicitly (%s): %s",
        len(report.ignored_explicitly),
        ", ".join(report.ignored_explicitly) or "none",
    )
    logger.info(
        "Non-migrated at this stage (%s): %s",
        len(report.non_migrated),
        ", ".join(report.non_migrated) or "none",
    )
    logger.info("Manual review required (%s)", len(report.manual_review_required))
    for item in report.manual_review_required:
        logger.warning("  MANUAL REVIEW: %s", item)

    logger.info("Unmatched manual plans kept as manual (%s)", len(report.unmatched_manual_plans))
    for item in report.unmatched_manual_plans:
        logger.info("  %s", item)

    logger.info("Anomalies (%s)", len(report.anomalies))
    for item in report.anomalies:
        logger.warning("  ANOMALY: %s", item)

    logger.info("=== BACKFILL COMPLETED ===")


if __name__ == "__main__":
    run_backfill()

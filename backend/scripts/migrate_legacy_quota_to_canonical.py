"""
Migration one-shot : user_daily_quota_usages → feature_usage_counters pour astrologer_chat.

Le script résout le quota canonique courant de chaque user :
- basic (day/calendar) → migration 1:1 par fenêtre journalière
- premium (month/calendar) → agrégation des lignes daily dans la fenêtre mensuelle courante
- free / trial (DISABLED) → skip silencieux
- aucun binding canonique → skip + log WARNING

Usage:
    python backend/scripts/migrate_legacy_quota_to_canonical.py
    python backend/scripts/migrate_legacy_quota_to_canonical.py --dry-run
    python backend/scripts/migrate_legacy_quota_to_canonical.py --days 30
"""
import argparse
import logging
import sys
from datetime import UTC, datetime, timedelta
from collections import defaultdict

from sqlalchemy import select
from app.infra.db.session import SessionLocal
from app.infra.db.models.billing import UserDailyQuotaUsageModel
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel, FeatureUsageCounterModel,
    PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
)
from app.services.billing_service import BillingService
from app.services.quota_window_resolver import QuotaWindowResolver

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FEATURE_CODE = "astrologer_chat"
QUOTA_KEY = "messages"


def _resolve_canonical_quota(db, user_id: int):
    """Retourne PlanFeatureQuotaModel ou None si pas de binding actif."""
    subscription = BillingService.get_subscription_status(db, user_id=user_id)
    if not subscription.plan:
        return None
    plan = db.scalar(
        select(PlanCatalogModel)
        .where(PlanCatalogModel.plan_code == subscription.plan.code).limit(1)
    )
    feature = db.scalar(
        select(FeatureCatalogModel)
        .where(FeatureCatalogModel.feature_code == FEATURE_CODE).limit(1)
    )
    if not plan or not feature:
        return None
    binding = db.scalar(
        select(PlanFeatureBindingModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            PlanFeatureBindingModel.feature_id == feature.id,
        ).limit(1)
    )
    if not binding or not binding.is_enabled or binding.access_mode.value == "disabled":
        return None  # DISABLED (free, trial) → skip
    return db.scalar(
        select(PlanFeatureQuotaModel)
        .where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
            PlanFeatureQuotaModel.quota_key == QUOTA_KEY,
        ).limit(1)
    )


def _upsert_counter(db, *, user_id, window_start, window_end,
                    period_unit, period_value, reset_mode, used_count, dry_run):
    existing = db.scalar(
        select(FeatureUsageCounterModel).where(
            FeatureUsageCounterModel.user_id == user_id,
            FeatureUsageCounterModel.feature_code == FEATURE_CODE,
            FeatureUsageCounterModel.quota_key == QUOTA_KEY,
            FeatureUsageCounterModel.period_unit == period_unit,
            FeatureUsageCounterModel.period_value == period_value,
            FeatureUsageCounterModel.reset_mode == reset_mode,
            FeatureUsageCounterModel.window_start == window_start,
        )
    )
    if dry_run:
        logger.info(
            "DRY RUN: Would upsert user %d: %d messages for window starting %s",
            user_id, used_count, window_start
        )
        return
    if existing:
        if used_count > existing.used_count:
            existing.used_count = used_count
            logger.info("Updated counter for user %d: %d messages", user_id, used_count)
    else:
        db.add(FeatureUsageCounterModel(
            user_id=user_id, feature_code=FEATURE_CODE, quota_key=QUOTA_KEY,
            period_unit=period_unit, period_value=period_value, reset_mode=reset_mode,
            window_start=window_start, window_end=window_end, used_count=used_count,
        ))
        logger.info("Created counter for user %d: %d messages", user_id, used_count)


def migrate(days: int = 1, dry_run: bool = False) -> dict:
    today = datetime.now(UTC).date()
    cutoff = today - timedelta(days=days - 1)
    ref_dt = datetime.now(UTC)
    stats = {"processed": 0, "created_or_updated": 0, "skipped_disabled": 0, "anomalies": 0}

    with SessionLocal() as db:
        # Charger toutes les lignes legacy concernées, regroupées par user
        rows = db.scalars(
            select(UserDailyQuotaUsageModel)
            .where(UserDailyQuotaUsageModel.quota_date >= cutoff)
            .where(UserDailyQuotaUsageModel.used_count > 0)
            .order_by(UserDailyQuotaUsageModel.user_id, UserDailyQuotaUsageModel.quota_date)
        ).all()

        if not rows:
            logger.info("No legacy quota usage found since %s.", cutoff)
            return stats

        by_user = defaultdict(list)
        for row in rows:
            by_user[row.user_id].append(row)

        for user_id, user_rows in by_user.items():
            quota_model = _resolve_canonical_quota(db, user_id)

            if quota_model is None:
                # Distinguer DISABLED (binding existe mais disabled) de no-binding
                logger.warning("user %d: no active canonical quota for %s — skipping", user_id, FEATURE_CODE)
                stats["skipped_disabled"] += len(user_rows)
                continue

            period_unit = quota_model.period_unit.value
            period_value = quota_model.period_value
            reset_mode = quota_model.reset_mode.value

            if period_unit == "day":
                # Migration 1:1 par fenêtre journalière
                for row in user_rows:
                    window_start = datetime.combine(row.quota_date, datetime.min.time(), tzinfo=UTC)
                    window_end = window_start + timedelta(days=1)
                    _upsert_counter(
                        db, user_id=user_id,
                        window_start=window_start, window_end=window_end,
                        period_unit=period_unit, period_value=period_value,
                        reset_mode=reset_mode, used_count=row.used_count, dry_run=dry_run,
                    )
                    stats["created_or_updated"] += 1
            elif period_unit == "month":
                # Agréger les lignes legacy dans la fenêtre mensuelle courante
                window = QuotaWindowResolver.compute_window(
                    period_unit, period_value, reset_mode, ref_dt
                )
                total_used = sum(r.used_count for r in user_rows)
                _upsert_counter(
                    db, user_id=user_id,
                    window_start=window.window_start, window_end=window.window_end,
                    period_unit=period_unit, period_value=period_value,
                    reset_mode=reset_mode, used_count=total_used, dry_run=dry_run,
                )
                stats["created_or_updated"] += 1
            else:
                logger.warning(
                    "user %d: unsupported period_unit '%s' for %s — skipping",
                    user_id, period_unit, FEATURE_CODE
                )
                stats["anomalies"] += 1
                continue

            stats["processed"] += len(user_rows)

        if not dry_run:
            db.commit()

    logger.info(
        "Migration %s: %d lignes traitées, %d entrées canoniques upsertées, "
        "%d skips (disabled/no-binding), %d anomalies",
        "(DRY RUN) " if dry_run else "",
        stats["processed"], stats["created_or_updated"],
        stats["skipped_disabled"], stats["anomalies"],
    )
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate legacy chat quota to canonical system.")
    parser.add_argument("--days", type=int, default=1, help="Number of days to migrate (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Do not commit changes")
    args = parser.parse_args()

    migrate(days=args.days, dry_run=args.dry_run)

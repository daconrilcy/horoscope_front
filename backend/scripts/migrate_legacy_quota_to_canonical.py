"""
Migration one-shot : user_daily_quota_usages -> feature_usage_counters pour astrologer_chat.

Le script résout le quota canonique courant de chaque user :
- basic (day/calendar) -> migration 1:1 par fenêtre journalière
- premium (month/calendar) -> agrégation des lignes daily dans la fenêtre mensuelle courante
- free / trial (DISABLED) -> skip silencieux
- aucun binding canonique -> skip + log WARNING

Usage:
    python backend/scripts/migrate_legacy_quota_to_canonical.py
    python backend/scripts/migrate_legacy_quota_to_canonical.py --dry-run
    python backend/scripts/migrate_legacy_quota_to_canonical.py --days 30
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.billing import UserDailyQuotaUsageModel
from app.infra.db.models.product_entitlements import (
    FeatureCatalogModel,
    FeatureUsageCounterModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
)
from app.infra.db.session import SessionLocal
from app.services.billing.service import BillingService
from app.services.quota_window_resolver import QuotaWindow, QuotaWindowResolver

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FEATURE_CODE = "astrologer_chat"
QUOTA_KEY = "messages"

ResolutionStatus = Literal["quota", "disabled", "no_binding", "missing_catalog"]


@dataclass(frozen=True)
class CanonicalQuotaResolution:
    status: ResolutionStatus
    quota_model: PlanFeatureQuotaModel | None = None


def _resolve_canonical_quota(db: Session, user_id: int) -> CanonicalQuotaResolution:
    """Retourne le quota canonique courant et la raison d'un éventuel skip."""
    subscription = BillingService.get_subscription_status(db, user_id=user_id)
    if not subscription.plan:
        return CanonicalQuotaResolution(status="missing_catalog")

    plan = db.scalar(
        select(PlanCatalogModel)
        .where(PlanCatalogModel.plan_code == subscription.plan.code)
        .limit(1)
    )
    feature = db.scalar(
        select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == FEATURE_CODE).limit(1)
    )
    if not plan or not feature:
        return CanonicalQuotaResolution(status="missing_catalog")

    binding = db.scalar(
        select(PlanFeatureBindingModel)
        .where(
            PlanFeatureBindingModel.plan_id == plan.id,
            PlanFeatureBindingModel.feature_id == feature.id,
        )
        .limit(1)
    )
    if not binding:
        return CanonicalQuotaResolution(status="no_binding")
    if not binding.is_enabled or binding.access_mode.value == "disabled":
        return CanonicalQuotaResolution(status="disabled")

    quota_model = db.scalar(
        select(PlanFeatureQuotaModel)
        .where(
            PlanFeatureQuotaModel.plan_feature_binding_id == binding.id,
            PlanFeatureQuotaModel.quota_key == QUOTA_KEY,
        )
        .limit(1)
    )
    if quota_model is None:
        return CanonicalQuotaResolution(status="no_binding")

    return CanonicalQuotaResolution(status="quota", quota_model=quota_model)


def _resolve_row_cutoff(*, today: date, ref_dt: datetime, days: int | None) -> date:
    if days is not None:
        return today - timedelta(days=days - 1)

    current_month_window = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)
    return current_month_window.window_start.date()


def _upsert_counter(
    db: Session,
    *,
    user_id: int,
    window_start: datetime,
    window_end: datetime | None,
    period_unit: str,
    period_value: int,
    reset_mode: str,
    used_count: int,
    dry_run: bool,
) -> bool:
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
            "DRY RUN: would upsert user %d: %d messages for window starting %s",
            user_id,
            used_count,
            window_start.isoformat(),
        )
        return True

    if existing:
        if used_count > existing.used_count:
            existing.used_count = used_count
            logger.info("Updated counter for user %d: %d messages", user_id, used_count)
            return True
        return False

    db.add(
        FeatureUsageCounterModel(
            user_id=user_id,
            feature_code=FEATURE_CODE,
            quota_key=QUOTA_KEY,
            period_unit=period_unit,
            period_value=period_value,
            reset_mode=reset_mode,
            window_start=window_start,
            window_end=window_end,
            used_count=used_count,
        )
    )
    logger.info("Created counter for user %d: %d messages", user_id, used_count)
    return True


def _filter_rows_for_window(
    rows: list[UserDailyQuotaUsageModel],
    *,
    window: QuotaWindow,
    days: int | None,
    ref_date: date,
) -> list[UserDailyQuotaUsageModel]:
    filtered = [
        row
        for row in rows
        if row.quota_date >= window.window_start.date()
        and (window.window_end is None or row.quota_date < window.window_end.date())
    ]
    if days is None:
        return filtered

    cutoff = ref_date - timedelta(days=days - 1)
    return [row for row in filtered if row.quota_date >= cutoff]


def migrate(days: int | None = None, dry_run: bool = False) -> dict[str, int]:
    today = datetime_provider.utcnow().date()
    ref_dt = datetime_provider.utcnow()
    cutoff = _resolve_row_cutoff(today=today, ref_dt=ref_dt, days=days)
    stats = {"processed": 0, "created_or_updated": 0, "skipped_disabled": 0, "anomalies": 0}

    with SessionLocal() as db:
        rows = db.scalars(
            select(UserDailyQuotaUsageModel)
            .where(UserDailyQuotaUsageModel.quota_date >= cutoff)
            .where(UserDailyQuotaUsageModel.used_count > 0)
            .order_by(UserDailyQuotaUsageModel.user_id, UserDailyQuotaUsageModel.quota_date)
        ).all()

        if not rows:
            logger.info("No legacy quota usage found since %s.", cutoff)
            return stats

        by_user: dict[int, list[UserDailyQuotaUsageModel]] = defaultdict(list)
        for row in rows:
            by_user[row.user_id].append(row)

        for user_id, user_rows in by_user.items():
            stats["processed"] += len(user_rows)
            resolution = _resolve_canonical_quota(db, user_id)

            if resolution.status == "disabled":
                stats["skipped_disabled"] += len(user_rows)
                continue

            if resolution.status == "no_binding":
                logger.warning(
                    "user %d: no canonical binding for %s, skipping migration",
                    user_id,
                    FEATURE_CODE,
                )
                stats["anomalies"] += 1
                continue

            if resolution.status == "missing_catalog":
                logger.warning(
                    "user %d: canonical plan/catalog missing for %s, skipping migration",
                    user_id,
                    FEATURE_CODE,
                )
                stats["anomalies"] += 1
                continue

            quota_model = resolution.quota_model
            if quota_model is None:
                logger.warning(
                    "user %d: canonical quota missing for %s, skipping migration",
                    user_id,
                    FEATURE_CODE,
                )
                stats["anomalies"] += 1
                continue

            period_unit = quota_model.period_unit.value
            period_value = quota_model.period_value
            reset_mode = quota_model.reset_mode.value
            active_window = QuotaWindowResolver.compute_window(
                period_unit, period_value, reset_mode, ref_dt
            )
            scoped_rows = _filter_rows_for_window(
                user_rows,
                window=active_window,
                days=days,
                ref_date=today,
            )

            if not scoped_rows:
                continue

            if period_unit == "day":
                for row in scoped_rows:
                    window_start = datetime.combine(row.quota_date, datetime.min.time(), tzinfo=UTC)
                    window_end = window_start + timedelta(days=1)
                    changed = _upsert_counter(
                        db,
                        user_id=user_id,
                        window_start=window_start,
                        window_end=window_end,
                        period_unit=period_unit,
                        period_value=period_value,
                        reset_mode=reset_mode,
                        used_count=row.used_count,
                        dry_run=dry_run,
                    )
                    if changed:
                        stats["created_or_updated"] += 1
            elif period_unit == "month":
                total_used = sum(row.used_count for row in scoped_rows)
                changed = _upsert_counter(
                    db,
                    user_id=user_id,
                    window_start=active_window.window_start,
                    window_end=active_window.window_end,
                    period_unit=period_unit,
                    period_value=period_value,
                    reset_mode=reset_mode,
                    used_count=total_used,
                    dry_run=dry_run,
                )
                if changed:
                    stats["created_or_updated"] += 1
            else:
                logger.warning(
                    "user %d: unsupported period_unit '%s' for %s, skipping",
                    user_id,
                    period_unit,
                    FEATURE_CODE,
                )
                stats["anomalies"] += 1

        if not dry_run:
            db.commit()

    logger.info(
        "Migration %s: %d lignes legacy traitées, %d entrées canoniques créées/mises à jour, "
        "%d skips (disabled), %d anomalies",
        "(DRY RUN) " if dry_run else "",
        stats["processed"],
        stats["created_or_updated"],
        stats["skipped_disabled"],
        stats["anomalies"],
    )
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate legacy chat quota to canonical system.")
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Nombre de jours à migrer; absent = fenêtre active canonique uniquement",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not commit changes")
    args = parser.parse_args()

    migrate(days=args.days, dry_run=args.dry_run)

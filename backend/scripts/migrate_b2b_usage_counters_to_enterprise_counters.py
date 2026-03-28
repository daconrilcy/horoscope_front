import argparse
import logging
import os
import sys
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.session import SessionLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def migrate_counters(dry_run: bool = False) -> None:
    db: Session = SessionLocal()
    try:
        # 1. Fetch all B2B API access counters from legacy table
        legacy_counters = (
            db.execute(
                select(FeatureUsageCounterModel).where(
                    FeatureUsageCounterModel.feature_code == "b2b_api_access"
                )
            )
            .scalars()
            .all()
        )

        logger.info(
            "category=scan mode=%s found=%s feature_code=%s",
            "dry-run" if dry_run else "live",
            len(legacy_counters),
            "b2b_api_access",
        )

        stats = {
            "migrated": 0,
            "already_present": 0,
            "skipped_no_account": 0,
            "skipped_multiple_accounts": 0,
            "anomalies": 0,
        }

        for legacy in legacy_counters:
            try:
                # 2. Resolve enterprise_account_id via admin_user_id
                accounts = (
                    db.execute(
                        select(EnterpriseAccountModel).where(
                            EnterpriseAccountModel.admin_user_id == legacy.user_id
                        )
                    )
                    .scalars()
                    .all()
                )

                if not accounts:
                    logger.warning(
                        "category=skipped_no_account legacy_counter_id=%s user_id=%s",
                        legacy.id,
                        legacy.user_id,
                    )
                    stats["skipped_no_account"] += 1
                    continue

                if len(accounts) > 1:
                    logger.error(
                        (
                            "category=skipped_multiple_accounts "
                            "legacy_counter_id=%s user_id=%s count=%s"
                        ),
                        legacy.id,
                        legacy.user_id,
                        len(accounts),
                    )
                    stats["skipped_multiple_accounts"] += 1
                    continue

                account = accounts[0]

                # 3. Check if counter already exists in new table
                existing = db.execute(
                    select(EnterpriseFeatureUsageCounterModel).where(
                        EnterpriseFeatureUsageCounterModel.enterprise_account_id == account.id,
                        EnterpriseFeatureUsageCounterModel.feature_code == legacy.feature_code,
                        EnterpriseFeatureUsageCounterModel.quota_key == legacy.quota_key,
                        EnterpriseFeatureUsageCounterModel.period_unit == legacy.period_unit,
                        EnterpriseFeatureUsageCounterModel.period_value == legacy.period_value,
                        EnterpriseFeatureUsageCounterModel.reset_mode == legacy.reset_mode,
                        EnterpriseFeatureUsageCounterModel.window_start == legacy.window_start,
                    )
                ).scalar_one_none()

                if existing:
                    # Idempotent update: max of used_count
                    if legacy.used_count > existing.used_count:
                        if not dry_run:
                            logger.info(
                                (
                                    "category=migrated action=update "
                                    "account_id=%s legacy_counter_id=%s "
                                    "used_count_before=%s used_count_after=%s"
                                ),
                                account.id,
                                legacy.id,
                                existing.used_count,
                                legacy.used_count,
                            )
                            existing.used_count = legacy.used_count
                            existing.updated_at = datetime.now(timezone.utc)
                            stats["migrated"] += 1
                        else:
                            logger.info(
                                (
                                    "category=migrated action=update mode=dry-run "
                                    "account_id=%s legacy_counter_id=%s "
                                    "used_count_before=%s used_count_after=%s"
                                ),
                                account.id,
                                legacy.id,
                                existing.used_count,
                                legacy.used_count,
                            )
                            stats["migrated"] += 1
                    else:
                        logger.info(
                            (
                                "category=already_present account_id=%s "
                                "legacy_counter_id=%s used_count_existing=%s "
                                "used_count_legacy=%s"
                            ),
                            account.id,
                            legacy.id,
                            existing.used_count,
                            legacy.used_count,
                        )
                        stats["already_present"] += 1
                    continue

                # 4. Create new counter
                new_counter = EnterpriseFeatureUsageCounterModel(
                    enterprise_account_id=account.id,
                    feature_code=legacy.feature_code,
                    quota_key=legacy.quota_key,
                    period_unit=legacy.period_unit,
                    period_value=legacy.period_value,
                    reset_mode=legacy.reset_mode,
                    window_start=legacy.window_start,
                    window_end=legacy.window_end,
                    used_count=legacy.used_count,
                    created_at=legacy.created_at,
                    updated_at=legacy.updated_at,
                )

                if not dry_run:
                    db.add(new_counter)
                    logger.info(
                        (
                            "category=migrated action=insert "
                            "account_id=%s legacy_counter_id=%s used_count=%s"
                        ),
                        account.id,
                        legacy.id,
                        legacy.used_count,
                    )
                    stats["migrated"] += 1
                else:
                    logger.info(
                        (
                            "category=migrated action=insert mode=dry-run "
                            "account_id=%s legacy_counter_id=%s used_count=%s"
                        ),
                        account.id,
                        legacy.id,
                        legacy.used_count,
                    )
                    stats["migrated"] += 1

            except Exception:
                logger.exception(
                    "category=anomalies legacy_counter_id=%s user_id=%s",
                    legacy.id,
                    legacy.user_id,
                )
                stats["anomalies"] += 1

        if not dry_run:
            db.commit()
            logger.info("category=summary status=committed stats=%s", stats)
        else:
            logger.info("category=summary status=dry-run stats=%s", stats)

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate B2B usage counters to enterprise counters table"
    )
    parser.add_argument("--dry-run", action="store_true", help="Run without committing changes")
    args = parser.parse_args()

    migrate_counters(dry_run=args.dry_run)

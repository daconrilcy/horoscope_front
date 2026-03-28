#!/usr/bin/env python
"""
Vérification de la migration B2B usage counters (Story 61.25/61.26).
Compare feature_usage_counters vs enterprise_feature_usage_counters pour b2b_api_access.
Vérifie row_count ET sum(used_count) — un count seul ne suffit pas (l'upsert peut consolider).

Usage:
    python scripts/verify_b2b_usage_migration.py
    python scripts/verify_b2b_usage_migration.py --verbose
Exit codes: 0 = OK, 1 = MISMATCH
"""

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func, select

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_feature_usage_counters import EnterpriseFeatureUsageCounterModel
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.session import SessionLocal

FEATURE_CODE = "b2b_api_access"


class AggregateKey(NamedTuple):
    enterprise_account_id: int
    feature_code: str
    quota_key: str
    window_start: datetime


@dataclass(frozen=True)
class AggregateMismatch:
    key: AggregateKey
    old_used_count: int
    new_used_count: int


@dataclass(frozen=True)
class VerificationReport:
    old_row_count: int
    old_used_sum: int
    new_row_count: int
    new_used_sum: int
    unmatched_user_ids: set[int]
    multi_account_user_ids: set[int]
    unmatched_used_sum: int
    aggregate_mismatches: list[AggregateMismatch]

    @property
    def expected_new_used_sum(self) -> int:
        return self.old_used_sum - self.unmatched_used_sum

    @property
    def is_ok(self) -> bool:
        return self.new_used_sum >= self.expected_new_used_sum and not self.aggregate_mismatches


def _load_aggregate_mismatches(
    db,
    *,
    mapped_user_ids: set[int],
) -> list[AggregateMismatch]:
    account_by_user_id = {
        row.admin_user_id: row.id
        for row in db.execute(
            select(EnterpriseAccountModel.id, EnterpriseAccountModel.admin_user_id).where(
                EnterpriseAccountModel.admin_user_id.in_(mapped_user_ids)
            )
        ).all()
        if row.admin_user_id is not None
    }

    old_aggregates: dict[AggregateKey, int] = {}
    for row in db.execute(
        select(
            FeatureUsageCounterModel.user_id,
            FeatureUsageCounterModel.feature_code,
            FeatureUsageCounterModel.quota_key,
            FeatureUsageCounterModel.window_start,
            func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0).label("used_count"),
        )
        .where(
            FeatureUsageCounterModel.feature_code == FEATURE_CODE,
            FeatureUsageCounterModel.user_id.in_(mapped_user_ids),
        )
        .group_by(
            FeatureUsageCounterModel.user_id,
            FeatureUsageCounterModel.feature_code,
            FeatureUsageCounterModel.quota_key,
            FeatureUsageCounterModel.window_start,
        )
    ).all():
        enterprise_account_id = account_by_user_id.get(row.user_id)
        if enterprise_account_id is None:
            continue
        key = AggregateKey(
            enterprise_account_id=enterprise_account_id,
            feature_code=row.feature_code,
            quota_key=row.quota_key,
            window_start=row.window_start,
        )
        old_aggregates[key] = int(row.used_count or 0)

    new_aggregates = {
        AggregateKey(
            enterprise_account_id=row.enterprise_account_id,
            feature_code=row.feature_code,
            quota_key=row.quota_key,
            window_start=row.window_start,
        ): int(row.used_count or 0)
        for row in db.execute(
            select(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id,
                EnterpriseFeatureUsageCounterModel.feature_code,
                EnterpriseFeatureUsageCounterModel.quota_key,
                EnterpriseFeatureUsageCounterModel.window_start,
                func.coalesce(func.sum(EnterpriseFeatureUsageCounterModel.used_count), 0).label(
                    "used_count"
                ),
            )
            .where(EnterpriseFeatureUsageCounterModel.feature_code == FEATURE_CODE)
            .group_by(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id,
                EnterpriseFeatureUsageCounterModel.feature_code,
                EnterpriseFeatureUsageCounterModel.quota_key,
                EnterpriseFeatureUsageCounterModel.window_start,
            )
        ).all()
    }

    mismatches: list[AggregateMismatch] = []
    for key in sorted(set(old_aggregates) | set(new_aggregates)):
        old_used_count = old_aggregates.get(key, 0)
        new_used_count = new_aggregates.get(key, 0)
        if old_used_count != new_used_count:
            mismatches.append(
                AggregateMismatch(
                    key=key,
                    old_used_count=old_used_count,
                    new_used_count=new_used_count,
                )
            )
    return mismatches


def build_verification_report(db) -> VerificationReport:
    old_row_count = (
        db.scalar(
            select(func.count())
            .select_from(FeatureUsageCounterModel)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
        )
        or 0
    )
    old_used_sum = (
        db.scalar(
            select(func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0)).where(
                FeatureUsageCounterModel.feature_code == FEATURE_CODE
            )
        )
        or 0
    )

    new_row_count = (
        db.scalar(
            select(func.count())
            .select_from(EnterpriseFeatureUsageCounterModel)
            .where(EnterpriseFeatureUsageCounterModel.feature_code == FEATURE_CODE)
        )
        or 0
    )
    new_used_sum = (
        db.scalar(
            select(func.coalesce(func.sum(EnterpriseFeatureUsageCounterModel.used_count), 0)).where(
                EnterpriseFeatureUsageCounterModel.feature_code == FEATURE_CODE
            )
        )
        or 0
    )

    # Détecter les user_id sans account enterprise (non-migrables → ne comptent pas comme MISMATCH)
    old_user_ids = set(
        row[0]
        for row in db.execute(
            select(FeatureUsageCounterModel.user_id)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
            .distinct()
        ).all()
    )

    if not old_user_ids:
        return VerificationReport(
            old_row_count=old_row_count,
            old_used_sum=old_used_sum,
            new_row_count=new_row_count,
            new_used_sum=new_used_sum,
            unmatched_user_ids=set(),
            multi_account_user_ids=set(),
            unmatched_used_sum=0,
            aggregate_mismatches=[],
        )

    # Détecter les user_ids avec comptes multiples (non-migrables)
    multi_account_user_ids = set()
    for user_id in old_user_ids:
        count = db.scalar(
            select(func.count())
            .select_from(EnterpriseAccountModel)
            .where(EnterpriseAccountModel.admin_user_id == user_id)
        )
        if (count or 0) > 1:
            multi_account_user_ids.add(user_id)

    mapped_user_ids = set(
        row[0]
        for row in db.execute(
            select(EnterpriseAccountModel.admin_user_id).where(
                EnterpriseAccountModel.admin_user_id.in_(old_user_ids),
                EnterpriseAccountModel.admin_user_id.notin_(multi_account_user_ids),
            )
        ).all()
    )
    unmatched_user_ids = old_user_ids - mapped_user_ids

    # used_count des lignes non-migrables (user sans account ou multi-accounts)
    unmatched_used_sum = 0
    if unmatched_user_ids:
        unmatched_used_sum = (
            db.scalar(
                select(func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0)).where(
                    FeatureUsageCounterModel.feature_code == FEATURE_CODE,
                    FeatureUsageCounterModel.user_id.in_(unmatched_user_ids),
                )
            )
            or 0
        )

    aggregate_mismatches = _load_aggregate_mismatches(
        db,
        mapped_user_ids=mapped_user_ids,
    )

    return VerificationReport(
        old_row_count=old_row_count,
        old_used_sum=old_used_sum,
        new_row_count=new_row_count,
        new_used_sum=new_used_sum,
        unmatched_user_ids=unmatched_user_ids,
        multi_account_user_ids=multi_account_user_ids,
        unmatched_used_sum=unmatched_used_sum,
        aggregate_mismatches=aggregate_mismatches,
    )


def run_verification(db, verbose: bool) -> bool:
    """Retourne True si la migration est cohérente, False si MISMATCH."""
    report = build_verification_report(db)

    if report.old_row_count == 0:
        print("✅ Aucun compteur legacy B2B trouvé — migration vide (OK).")
        return True

    print(f"old_row_count : {report.old_row_count}")
    print(f"old_used_sum  : {report.old_used_sum}")
    print(f"new_row_count : {report.new_row_count}")
    print(f"new_used_sum  : {report.new_used_sum}")
    print(
        f"delta_rows    : {report.new_row_count - report.old_row_count:+d}  "
        "(upsert peut consolider → négatif acceptable)"
    )
    print(f"delta_used    : {report.new_used_sum - report.old_used_sum:+d}")
    print(f"unmatched_user_count: {len(report.unmatched_user_ids)}")
    print(
        "  - skipped_no_account      : "
        f"{len(report.unmatched_user_ids - report.multi_account_user_ids)}"
    )
    print(f"  - skipped_multiple_account: {len(report.multi_account_user_ids)}")
    print(f"unmatched_used_sum   : {report.unmatched_used_sum}")
    print(f"expected_new_used_sum: {report.expected_new_used_sum}")
    print(f"aggregate_mismatch_count: {len(report.aggregate_mismatches)}")

    if verbose and report.unmatched_user_ids:
        no_account = report.unmatched_user_ids - report.multi_account_user_ids
        if no_account:
            print(f"  → user_ids sans account enterprise: {sorted(no_account)}")
        if report.multi_account_user_ids:
            print(f"  → user_ids avec comptes multiples: {sorted(report.multi_account_user_ids)}")

    if verbose and report.aggregate_mismatches:
        print("Détail des écarts par clé métier (enterprise_account_id, quota_key, window_start):")
        for mismatch in report.aggregate_mismatches:
            print(
                "  - "
                f"account_id={mismatch.key.enterprise_account_id} "
                f"quota_key={mismatch.key.quota_key} "
                f"window_start={mismatch.key.window_start.isoformat()} "
                f"old={mismatch.old_used_count} "
                f"new={mismatch.new_used_count}"
            )

    if report.is_ok:
        print("✅ OK — migration cohérente (used_count couvert)")
        return True

    if report.aggregate_mismatches:
        print("❌ MISMATCH — écarts détectés sur les agrégats métier migrés.")
        return False

    gap = report.expected_new_used_sum - report.new_used_sum
    print(f"❌ MISMATCH — {gap} unité(s) manquante(s) dans enterprise_feature_usage_counters")
    return False


def main(verbose: bool) -> None:
    with SessionLocal() as db:
        ok = run_verification(db, verbose=verbose)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    main(verbose=args.verbose)

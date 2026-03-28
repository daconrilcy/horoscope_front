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

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func, select

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_feature_usage_counters import EnterpriseFeatureUsageCounterModel
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.session import SessionLocal

FEATURE_CODE = "b2b_api_access"


def run_verification(db, verbose: bool) -> bool:
    """Retourne True si la migration est cohérente, False si MISMATCH."""
    old_row_count = db.scalar(
        select(func.count()).select_from(FeatureUsageCounterModel)
        .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
    ) or 0
    old_used_sum = db.scalar(
        select(func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0))
        .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
    ) or 0

    new_row_count = db.scalar(
        select(func.count()).select_from(EnterpriseFeatureUsageCounterModel)
        .where(EnterpriseFeatureUsageCounterModel.feature_code == FEATURE_CODE)
    ) or 0
    new_used_sum = db.scalar(
        select(func.coalesce(func.sum(EnterpriseFeatureUsageCounterModel.used_count), 0))
        .where(EnterpriseFeatureUsageCounterModel.feature_code == FEATURE_CODE)
    ) or 0

    # Détecter les user_id sans account enterprise (non-migrables → ne comptent pas comme MISMATCH)
    old_user_ids = set(
        row[0] for row in db.execute(
            select(FeatureUsageCounterModel.user_id)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
            .distinct()
        ).all()
    )
    
    if not old_user_ids:
        # Nothing to migrate or verify
        print("✅ Aucun compteur legacy B2B trouvé — migration vide (OK).")
        return True

    # Détecter les user_ids avec comptes multiples (non-migrables)
    multi_account_user_ids = set()
    for user_id in old_user_ids:
        count = db.scalar(
            select(func.count()).select_from(EnterpriseAccountModel)
            .where(EnterpriseAccountModel.admin_user_id == user_id)
        )
        if count > 1:
            multi_account_user_ids.add(user_id)

    mapped_user_ids = set(
        row[0] for row in db.execute(
            select(EnterpriseAccountModel.admin_user_id)
            .where(
                EnterpriseAccountModel.admin_user_id.in_(old_user_ids),
                EnterpriseAccountModel.admin_user_id.notin_(multi_account_user_ids)
            )
        ).all()
    )
    unmatched_user_ids = old_user_ids - mapped_user_ids

    # used_count des lignes non-migrables (user sans account ou multi-accounts)
    unmatched_used_sum = 0
    if unmatched_user_ids:
        unmatched_used_sum = db.scalar(
            select(func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0))
            .where(
                FeatureUsageCounterModel.feature_code == FEATURE_CODE,
                FeatureUsageCounterModel.user_id.in_(unmatched_user_ids),
            )
        ) or 0

    expected_used_sum = old_used_sum - unmatched_used_sum

    print(f"old_row_count : {old_row_count}")
    print(f"old_used_sum  : {old_used_sum}")
    print(f"new_row_count : {new_row_count}")
    print(f"new_used_sum  : {new_used_sum}")
    print(
        f"delta_rows    : {new_row_count - old_row_count:+d}  "
        "(upsert peut consolider → négatif acceptable)"
    )
    print(f"delta_used    : {new_used_sum - old_used_sum:+d}")
    print(f"unmatched_user_count (non-migrables): {len(unmatched_user_ids)}")
    print(f"  - skipped_no_account      : {len(unmatched_user_ids - multi_account_user_ids)}")
    print(f"  - skipped_multiple_account: {len(multi_account_user_ids)}")
    print(f"unmatched_used_sum   : {unmatched_used_sum}")
    print(f"expected_new_used_sum: {expected_used_sum}")

    if verbose and unmatched_user_ids:
        no_account = unmatched_user_ids - multi_account_user_ids
        if no_account:
            print(f"  → user_ids sans account enterprise: {sorted(no_account)}")
        if multi_account_user_ids:
            print(f"  → user_ids avec comptes multiples: {sorted(multi_account_user_ids)}")

    if new_used_sum >= expected_used_sum:
        print("✅ OK — migration cohérente (used_count couvert)")
        return True
    else:
        gap = expected_used_sum - new_used_sum
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

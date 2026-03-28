#!/usr/bin/env python
"""
Archivage/purge des anciens compteurs B2B dans feature_usage_counters (Story 61.26).
Supprime les lignes feature_code='b2b_api_access' une fois la migration 61.25 validée.

GARDE-FOU : refuse la purge si verify_b2b_usage_migration retourne MISMATCH, sauf --force.

Usage:
    python scripts/archive_b2b_legacy_usage_counters.py --dry-run
    python scripts/archive_b2b_legacy_usage_counters.py
    python scripts/archive_b2b_legacy_usage_counters.py --force
    # Note: --force bypass le garde-fou (usage exceptionnel)
"""
import argparse
import os
import sys

# Add backend to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import delete, func, select

from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.session import SessionLocal

# Réutilise la logique de vérification du script dédié
from scripts.verify_b2b_usage_migration import run_verification

FEATURE_CODE = "b2b_api_access"


def main(dry_run: bool, force: bool) -> None:
    with SessionLocal() as db:
        # Garde-fou : vérification de la cohérence de la migration
        if not force:
            print("--- Vérification cohérence migration ---")
            ok = run_verification(db, verbose=False)
            if not ok:
                print(
                    "❌ ABORT — vérification migration incomplète.\n"
                    "   Relancer verify_b2b_usage_migration.py pour diagnostiquer,\n"
                    "   ou utiliser --force si le mismatch est intentionnel."
                )
                sys.exit(1)
            print("--- Vérification OK — purge autorisée ---")
        else:
            print("⚠️  --force activé : garde-fou de vérification ignoré.")

        legacy_count = db.scalar(
            select(func.count()).select_from(FeatureUsageCounterModel)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
        ) or 0

        if legacy_count == 0:
            print("✅ Aucune ligne legacy B2B à purger — idempotent no-op.")
            return

        print(
            f"Lignes à purger dans feature_usage_counters "
            f"(feature_code='{FEATURE_CODE}'): {legacy_count}"
        )

        if dry_run:
            print("🟡 DRY-RUN — aucune modification effectuée.")
            return

        db.execute(
            delete(FeatureUsageCounterModel)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
        )
        db.commit()
        print(f"✅ {legacy_count} ligne(s) purgée(s) de feature_usage_counters.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Bypass garde-fou de vérification")
    args = parser.parse_args()
    main(dry_run=args.dry_run, force=args.force)

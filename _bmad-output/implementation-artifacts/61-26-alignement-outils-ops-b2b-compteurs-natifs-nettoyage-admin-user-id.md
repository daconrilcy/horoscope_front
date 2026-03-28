# Story 61.26 : Alignement des outils ops B2B sur les compteurs natifs entreprise + nettoyage des reliquats admin_user_id

Status: done

## Story

En tant que développeur backend,
je veux nettoyer les derniers reliquats du compromis `admin_user_id` dans les outils ops B2B (audit, repair, scripts de migration) et fournir un script de vérification + archivage des anciens compteurs B2B dans `feature_usage_counters`,
afin que l'écosystème ops B2B soit entièrement aligné sur `enterprise_account_id` / `enterprise_feature_usage_counters` et que plus aucun artefact de code, doc ou script ne laisse penser que `admin_user_id` est un prérequis quota.

## Acceptance Criteria

### AC 1 — Nettoyage du Literal `reason` dans `B2BAuditEntry`

1. `"admin_user_id_missing"` est retiré du `Literal` dans `B2BAuditEntry.reason` (`backend/app/services/b2b_audit_service.py`). Aucun chemin de code ne peut désormais produire ce `reason`.
2. Le champ `admin_user_id_present: bool` reste présent dans `B2BAuditEntry` — c'est une métadonnée d'intégrité (ownership), pas un motif de blocage quota.
3. Le test unitaire `test_audit_admin_user_id_missing` est **remplacé** par un test `test_audit_admin_user_id_absent_does_not_block_canonical_resolution` qui vérifie : un compte avec plan canonique + binding valide et `admin_user_id=None` sort en `resolution_source ∈ {"canonical_quota", "canonical_unlimited", "canonical_disabled"}` — jamais en `"settings_fallback"` pour cette raison. Le champ `admin_user_id_present=False` est présent dans l'entrée mais n'affecte pas la `resolution_source`.

### AC 2 — Nettoyage du Literal `recommended_action` dans `RepairBlockerEntry`

4. `"set_admin_user"` est retiré du `Literal` dans `RepairBlockerEntry.recommended_action` (`backend/app/services/b2b_entitlement_repair_service.py`). `run_auto_repair()` n'insère plus aucun blocker avec cette action.
5. `recommended_action` ne conserve que les valeurs réellement produites par `run_auto_repair()` : `"classify_zero_units"` et `"schema_constraint_violation"`.
6. Un commentaire explicite dans `run_auto_repair()` indique : *"L'absence d'`admin_user_id` n'est plus un blocker quota depuis 61.25. Elle n'alimente jamais `remaining_blockers`."* Ce commentaire sert de garde-fou explicite pour tout futur développeur qui lirait ce code.

### AC 3 — Requalification de `set_admin_user` (ownership, pas quota)

6. L'endpoint `POST /v1/ops/b2b/entitlements/repair/set-admin-user` reste fonctionnel (non supprimé) mais est documenté comme un outil de gestion d'**ownership/authentification** du compte enterprise, sans lien avec la consommation quota.
7. La docstring ou le commentaire dans `b2b_entitlement_repair.py` et dans `B2BEntitlementRepairService.set_admin_user()` précise explicitement : *"Cet endpoint gère l'ownership du compte (admin_user_id). Il n'est pas un prérequis à la consommation ou à la lecture de quota B2B depuis 61.25."*

### AC 4 — Script de vérification de la migration historique

8. Script `backend/scripts/verify_b2b_usage_migration.py` créé, qui :
   - Compare pour `feature_code='b2b_api_access'` : `row_count` ET `sum(used_count)` entre les deux tables
   - Agrège par clé métier `(enterprise_account_id, feature_code, quota_key, window_start)` pour détecter des écarts de valeur (pas seulement de volume)
   - Détecte les `user_id` présents dans l'ancienne table mais sans compte enterprise correspondant (`skipped_no_account`) — ces lignes sont normalement non-migrables et ne constituent pas un MISMATCH
   - Imprime un rapport : `old_row_count`, `old_used_sum`, `new_row_count`, `new_used_sum`, `delta_rows`, `delta_used`, `unmatched_user_count` avec conclusion `OK` ou `MISMATCH`
   - La conclusion est `OK` si `new_used_sum >= old_used_sum - sum(used_count des lignes unmatched)` — l'upsert peut avoir consolidé des lignes, donc `new_row_count < old_row_count` est acceptable si `used_sum` est cohérent
9. Le script supporte `--verbose` pour afficher le détail des écarts par `(enterprise_account_id, quota_key, window_start)`.
9bis. Le script retourne exit code `0` si OK, `1` si MISMATCH — utilisable en CI ou en runbook conditionnel.

### AC 5 — Script d'archivage/purge des anciens compteurs B2B

10. Script `backend/scripts/archive_b2b_legacy_usage_counters.py` créé, qui :
    - **Préalable obligatoire** : appelle `verify_b2b_usage_migration` (ou reproduit sa logique) et refuse la purge si le résultat est MISMATCH — sauf flag `--force` explicite passé en ligne de commande
    - En mode `--dry-run` : loggue le nombre de lignes qui seraient supprimées, sans rien modifier
    - En mode réel (vérification OK) : supprime les lignes `feature_code='b2b_api_access'` dans `feature_usage_counters`
    - Supporte `--dry-run` et `--force` (bypass du garde-fou, à usage exceptionnel documenté)
11. Le script est idempotent : relance sans erreur si les lignes ont déjà été purgées (no-op avec message explicite).
12. Message d'erreur explicite si la vérification échoue : `"❌ ABORT — vérification migration incomplète. Relancer verify_b2b_usage_migration.py ou utiliser --force si intentionnel."`

### AC 6 — Labeling du script de migration one-shot

13. `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py` est annoté en tête de fichier avec un commentaire explicite :
    ```python
    # ONE-SHOT HISTORICAL MIGRATION — Story 61.25
    # Ce script ne doit être exécuté qu'une seule fois, avant le déploiement du runtime 61.25.
    # Il est conservé comme référence historique. Ne pas relancer en production sans validation.
    ```

### AC 7 — Aucun service ops B2B ne lit `feature_usage_counters` pour `b2b_api_access`

14. `B2BAuditService`, `B2BEntitlementRepairService`, `B2BBillingService`, `B2BReconciliationService`, `B2BApiEntitlementGate`, `B2BCanonicalUsageSummaryService` n'importent pas et ne lisent pas `FeatureUsageCounterModel` pour `feature_code='b2b_api_access'`.

### AC 8 — Mise à jour de la documentation canonique

15. `backend/docs/entitlements-canonical-platform.md` mis à jour :
    - Ajoute une section **"Outils ops B2B — Alignement post-61.26"** qui documente :
      - `GET /v1/ops/b2b/entitlements/audit` lit exclusivement `enterprise_feature_usage_counters`
      - `POST /v1/ops/b2b/entitlements/repair/set-admin-user` est un outil d'ownership/auth, hors périmètre quota
      - `admin_user_id` : ownership du compte uniquement, plus aucun chemin quota/usage B2B n'en dépend
      - Scripts de migration archivés + scripts de vérification et cleanup disponibles
    - Met à jour la table "Invariants" pour refléter l'état post-61.26

### AC 9 — Tests alignés

16. `backend/app/tests/unit/test_b2b_audit_service.py` : supprime `test_audit_admin_user_id_missing` (ou le remplace par un test vérifiant que `admin_user_id_present=False` ne produit PAS `reason="admin_user_id_missing"`).
17. `backend/app/tests/unit/test_b2b_entitlement_repair_service.py` : `test_set_admin_user_valid` et `test_set_admin_user_already_set` restent, mais leur portée est documentée comme "ownership/auth, pas quota".
18. Suite complète B2B (audit, repair, astrology, usage, billing, reconciliation) passe sans modification métier.

## Tasks / Subtasks

- [x] **Nettoyer `B2BAuditEntry.reason` Literal** (AC: 1)
  - [x] Retirer `"admin_user_id_missing"` du `Literal` dans `B2BAuditEntry.reason` (`b2b_audit_service.py` L.44-52)
  - [x] Vérifier qu'aucun chemin dans `_audit_account()` ne produit ce `reason` (déjà le cas post-61.25)
  - [x] Remplacer `test_audit_admin_user_id_missing` par `test_audit_admin_user_id_absent_does_not_block_canonical_resolution` : compte avec `admin_user_id=None` + plan canonique + binding valide → `resolution_source` canonique, jamais `"settings_fallback"`

- [x] **Nettoyer `RepairBlockerEntry.recommended_action` Literal** (AC: 2)
  - [x] Retirer `"set_admin_user"` du `Literal` (`b2b_entitlement_repair_service.py` L.47)
  - [x] Conserver `"classify_zero_units"` et `"schema_constraint_violation"`
  - [x] Ajouter commentaire dans `run_auto_repair()` : "L'absence d'admin_user_id n'est plus un blocker quota — ne jamais ajouter de RepairBlockerEntry pour cette raison"

- [x] **Requalifier `set_admin_user` comme outil d'ownership** (AC: 3)
  - [x] Ajouter docstring/commentaire dans `B2BEntitlementRepairService.set_admin_user()` explicitant que c'est de l'ownership, pas du quota
  - [x] Ajouter commentaire sur l'endpoint `POST /repair/set-admin-user` dans `b2b_entitlement_repair.py`

- [x] **Créer `verify_b2b_usage_migration.py`** (AC: 4)
  - [x] Comparer `row_count` ET `sum(used_count)` entre les deux tables pour `b2b_api_access`
  - [x] Agréger par clé métier `(enterprise_account_id, quota_key, window_start)` pour détecter des écarts de valeur
  - [x] Détecter les `user_id` sans account correspondant (non-MISMATCH, juste info)
  - [x] Rapport complet : `old_row_count`, `old_used_sum`, `new_row_count`, `new_used_sum`, `delta_used`, `unmatched_user_count`
  - [x] Exit code `0` si OK, `1` si MISMATCH ; support `--verbose`

- [x] **Créer `archive_b2b_legacy_usage_counters.py`** (AC: 5)
  - [x] Préalable : appeler la logique de vérification — abort si MISMATCH (sauf `--force`)
  - [x] `--dry-run` : logguer sans supprimer
  - [x] Mode réel : supprimer les lignes `feature_code='b2b_api_access'` dans `feature_usage_counters`
  - [x] Idempotent (no-op avec message si déjà vide)
  - [x] Support `--force` pour bypass du garde-fou (usage exceptionnel)

- [x] **Labeler le script de migration one-shot** (AC: 6)
  - [x] Ajouter le commentaire "ONE-SHOT HISTORICAL MIGRATION" en tête de `migrate_b2b_usage_counters_to_enterprise_counters.py`

- [x] **Vérifier AC 7 — aucun import B2B parasite** (AC: 7)
  - [x] `ruff check` + grep sur les services B2B pour confirmer l'absence de `FeatureUsageCounterModel` dans les flux ops B2B

- [x] **Mettre à jour la documentation** (AC: 8)
  - [x] Ajouter section "Outils ops B2B — Alignement post-61.26" dans `entitlements-canonical-platform.md`
  - [x] Mettre à jour table des invariants

- [x] **Suite de non-régression** (AC: 9)
  - [x] `ruff check` sur tous les fichiers modifiés
  - [x] Suite pytest B2B complète

## Dev Notes

### Contexte post-61.25 — Ce qui est déjà fait

Après 61.25, les flux runtime B2B sont **entièrement** sur `enterprise_feature_usage_counters` :
- `B2BApiEntitlementGate.check_and_consume()` → `EnterpriseQuotaUsageService.consume()`
- `B2BCanonicalUsageSummaryService.get_summary()` → `EnterpriseQuotaUsageService.get_usage()`
- `B2BBillingService._consumed_units_for_period()` → lecture directe `EnterpriseFeatureUsageCounterModel`
- `B2BReconciliationService._usage_by_period()` → lecture directe `EnterpriseFeatureUsageCounterModel`
- `B2BAuditService._audit_account()` → `EnterpriseQuotaUsageService.get_usage()` (L.393-398)

**Ce qui reste à nettoyer (61.26) :**
1. `B2BAuditEntry.reason` Literal contient encore `"admin_user_id_missing"` (L.45) — code mort
2. `RepairBlockerEntry.recommended_action` Literal contient encore `"set_admin_user"` (L.47) — code mort
3. Scripts de migration sans labeling, scripts de vérification/cleanup manquants
4. Documentation ops non mise à jour

---

### Diff essentiel — `B2BAuditEntry.reason` (AC 1)

**Avant** (`b2b_audit_service.py` L.44-52) :
```python
reason: Literal[
    "admin_user_id_missing",   # ← SUPPRIMER
    "no_canonical_plan",
    "no_binding",
    "disabled_by_plan",
    "unlimited_access",
    "quota_binding_active",
    "manual_review_required",
]
```

**Après** :
```python
reason: Literal[
    "no_canonical_plan",
    "no_binding",
    "disabled_by_plan",
    "unlimited_access",
    "quota_binding_active",
    "manual_review_required",
]
```

> ⚠️ Aucun chemin dans `_audit_account()` ne produit `"admin_user_id_missing"` post-61.25. Ce Literal est du code mort pur — safe à retirer.

---

### Diff essentiel — `RepairBlockerEntry.recommended_action` (AC 2)

**Avant** (`b2b_entitlement_repair_service.py` L.46-48) :
```python
recommended_action: Literal[
    "set_admin_user", "classify_zero_units", "schema_constraint_violation"
]
```

**Après** :
```python
recommended_action: Literal[
    "classify_zero_units", "schema_constraint_violation"
]
```

> `run_auto_repair()` ne produit jamais `"set_admin_user"` depuis 61.25. Le retirer du Literal clarifie le contrat API.

**Ajouter également** un commentaire dans `run_auto_repair()` juste après la boucle `for account in all_accounts:`, au niveau où les blockers sont évalués :

```python
# NOTE: L'absence d'admin_user_id (account.admin_user_id is None) n'est JAMAIS
# un motif de remaining_blockers depuis Story 61.25.
# Les quotas B2B sont indexés par enterprise_account_id — admin_user_id est hors périmètre quota.
```

---

### Requalification `set_admin_user` (AC 3)

L'endpoint **reste fonctionnel**. Ajouter uniquement un commentaire :

```python
# OWNERSHIP/AUTH UNIQUEMENT — pas un prérequis quota depuis Story 61.25
# Cet endpoint permet d'associer un utilisateur administrateur à un compte enterprise.
# Il N'est PAS un prérequis à la consommation ou lecture de quota B2B.
# Les quotas B2B sont indexés par enterprise_account_id (enterprise_feature_usage_counters).
@classmethod
def set_admin_user(cls, db: Session, *, account_id: int, user_id: int) -> dict:
    ...
```

Même commentaire sur la route dans `b2b_entitlement_repair.py` au-dessus du `@router.post("/set-admin-user")`.

---

### Script `verify_b2b_usage_migration.py` — Template

```python
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
import sys
from sqlalchemy import select, func
from app.infra.db.database import SessionLocal
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.infra.db.models.enterprise_feature_usage_counters import EnterpriseFeatureUsageCounterModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel

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
        row.user_id for row in db.execute(
            select(FeatureUsageCounterModel.user_id)
            .where(FeatureUsageCounterModel.feature_code == FEATURE_CODE)
            .distinct()
        ).all()
    )
    mapped_user_ids = set(
        row.admin_user_id for row in db.execute(
            select(EnterpriseAccountModel.admin_user_id)
            .where(EnterpriseAccountModel.admin_user_id.in_(old_user_ids))
        ).all()
        if row.admin_user_id is not None
    )
    unmatched_user_ids = old_user_ids - mapped_user_ids

    # used_count des lignes non-migrables (user sans account)
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
    print(f"delta_rows    : {new_row_count - old_row_count:+d}  (upsert peut consolider → négatif acceptable)")
    print(f"delta_used    : {new_used_sum - old_used_sum:+d}")
    print(f"unmatched_user_count (skipped_no_account): {len(unmatched_user_ids)}")
    print(f"unmatched_used_sum   : {unmatched_used_sum}")
    print(f"expected_new_used_sum: {expected_used_sum}")

    if verbose and unmatched_user_ids:
        print(f"  → user_ids sans account enterprise: {sorted(unmatched_user_ids)}")

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
```

---

### Script `archive_b2b_legacy_usage_counters.py` — Template

```python
#!/usr/bin/env python
"""
Archivage/purge des anciens compteurs B2B dans feature_usage_counters (Story 61.26).
Supprime les lignes feature_code='b2b_api_access' une fois la migration 61.25 validée.

GARDE-FOU : refuse la purge si verify_b2b_usage_migration retourne MISMATCH, sauf --force.

Usage:
    python scripts/archive_b2b_legacy_usage_counters.py --dry-run
    python scripts/archive_b2b_legacy_usage_counters.py
    python scripts/archive_b2b_legacy_usage_counters.py --force  # bypass garde-fou (usage exceptionnel)
"""
import argparse
import sys
from sqlalchemy import select, func, delete
from app.infra.db.database import SessionLocal
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel

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

        print(f"Lignes à purger dans feature_usage_counters (feature_code='{FEATURE_CODE}'): {legacy_count}")

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
```

> **Décision d'architecture** : purge simple (DELETE) sans table d'archive. Les données historiques ont été migrées vers `enterprise_feature_usage_counters` en 61.25 ; la table `feature_usage_counters` continue d'exister pour le B2C. Le garde-fou `run_verification()` est importé depuis `verify_b2b_usage_migration.py` pour éviter la duplication de logique — s'assurer que les deux scripts sont dans le même module `scripts/` et que `__init__.py` existe.

---

### Commandes de validation

```powershell
# Activer venv
.\.venv\Scripts\Activate.ps1

# Lint sur les fichiers modifiés
cd backend && ruff check `
  app/services/b2b_audit_service.py `
  app/services/b2b_entitlement_repair_service.py `
  app/api/v1/routers/b2b_entitlement_repair.py `
  scripts/verify_b2b_usage_migration.py `
  scripts/archive_b2b_legacy_usage_counters.py `
  scripts/migrate_b2b_usage_counters_to_enterprise_counters.py

# Suite B2B complète
cd backend && pytest -q `
  app/tests/unit/test_b2b_audit_service.py `
  app/tests/unit/test_b2b_entitlement_repair_service.py `
  app/tests/unit/test_b2b_api_entitlement_gate.py `
  app/tests/unit/test_b2b_billing_service.py `
  app/tests/unit/test_b2b_reconciliation_service.py `
  app/tests/integration/test_b2b_astrology_api.py `
  app/tests/integration/test_b2b_usage_api.py `
  app/tests/integration/test_b2b_billing_api.py `
  app/tests/integration/test_b2b_reconciliation_api.py `
  app/tests/integration/test_b2b_api_entitlements.py `
  app/tests/integration/test_b2b_entitlements_audit.py `
  app/tests/integration/test_b2b_entitlement_repair.py `
  -v
```

---

### Runbook de déploiement prod (AC 5)

Exécuter **après** validation de 61.25 en production :

```bash
# Étape 1 — Vérification complète (row_count + used_count)
python scripts/verify_b2b_usage_migration.py --verbose
# Doit afficher ✅ OK — migration cohérente (used_count couvert)
# Si MISMATCH : investiguer avant toute purge (exit code 1)

# Étape 2 — Dry-run archivage (inclut re-vérification automatique)
python scripts/archive_b2b_legacy_usage_counters.py --dry-run
# Affiche le nombre de lignes qui seraient purgées

# Étape 3 — Archivage réel (seulement si étape 1 OK — le script le vérifie aussi)
python scripts/archive_b2b_legacy_usage_counters.py
# ✅ N lignes purgées de feature_usage_counters
```

---

### Invariants forts après 61.26

| Flux | Table | Service | `admin_user_id` |
|---|---|---|---|
| B2B runtime (gate, summary, billing, reco, audit) | `enterprise_feature_usage_counters` | `EnterpriseQuotaUsageService` | Non impliqué |
| B2C runtime (chat, natal, consultations) | `feature_usage_counters` | `QuotaUsageService` | N/A |
| Ownership/auth compte enterprise | `enterprise_accounts.admin_user_id` | `set_admin_user()` | Ownership seulement |

**Après 61.26, `admin_user_id` n'apparaît plus dans aucun Literal ou chemin de décision quota B2B.**

---

### Hors périmètre

- Ne pas modifier le schéma de `enterprise_accounts` (garder `admin_user_id` column)
- Ne pas supprimer `feature_usage_counters` (B2C l'utilise activement)
- Ne pas modifier `QuotaUsageService` ni les flux B2C
- Ne pas modifier les endpoints API publics ni les contrats API

### Project Structure Notes

**Nouveaux fichiers :**
- `backend/scripts/verify_b2b_usage_migration.py`
- `backend/scripts/archive_b2b_legacy_usage_counters.py`
- `backend/app/tests/unit/test_b2b_usage_migration_scripts.py`

**Fichiers modifiés :**
- `backend/app/services/b2b_audit_service.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/api/v1/routers/b2b_entitlement_repair.py`
- `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py`
- `backend/app/tests/unit/test_b2b_audit_service.py`
- `backend/docs/entitlements-canonical-platform.md`

### References

- [Source: backend/app/services/b2b_audit_service.py#L44-52]
- [Source: backend/app/services/b2b_entitlement_repair_service.py#L46-48]
- [Source: backend/app/services/b2b_entitlement_repair_service.py#L313]
- [Source: backend/app/api/v1/routers/b2b_entitlement_repair.py#L192]
- [Source: backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py]
- [Source: backend/app/tests/unit/test_b2b_audit_service.py#L29]
- [Source: backend/docs/entitlements-canonical-platform.md]
- [Source: backend/app/infra/db/models/enterprise_feature_usage_counters.py]
- [Source: backend/app/services/enterprise_quota_usage_service.py]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

### Completion Notes List
- Nettoyage des Literals `B2BAuditEntry.reason` et `RepairBlockerEntry.recommended_action` pour retirer `admin_user_id_missing` et `set_admin_user`.
- Requalification de l'endpoint `set-admin-user` comme outil d'ownership.
- Création de `verify_b2b_usage_migration.py` pour valider la cohérence de la migration (sum des `used_count`).
- Création de `archive_b2b_legacy_usage_counters.py` avec garde-fou de vérification automatique.
- Mise à jour de la documentation d'architecture pour refléter l'indépendance du quota vis-à-vis de l'`admin_user_id`.
- Test unitaire ajouté pour vérifier que l'absence d'`admin_user_id` ne bloque pas la résolution canonique.
- Revue Codex post-implémentation : la vérification de migration compare désormais les agrégats par clé métier `(enterprise_account_id, feature_code, quota_key, window_start)` et signale les compensations de delta.
- Revue Codex post-implémentation : le message d'abort du script d'archivage est aligné sur l'AC, et la documentation ne prétend plus qu'une purge a déjà été exécutée.

### File List
**Nouveaux fichiers :**
- `backend/scripts/verify_b2b_usage_migration.py`
- `backend/scripts/archive_b2b_legacy_usage_counters.py`
- `backend/app/tests/unit/test_b2b_usage_migration_scripts.py`

**Fichiers modifiés :**
- `backend/app/services/b2b_audit_service.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/api/v1/routers/b2b_entitlement_repair.py`
- `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py`
- `backend/app/tests/unit/test_b2b_audit_service.py`
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py`
- `backend/docs/entitlements-canonical-platform.md`

### Change Log
- 2026-03-28 : Story implémentée. Alignement des outils ops B2B sur les compteurs natifs et nettoyage des reliquats `admin_user_id`.
- 2026-03-28 : Revue Codex. Correction de la vérification par agrégats métier, alignement du message d'abort du script d'archivage, ajout de tests unitaires scripts, et correction documentaire sur la purge legacy.

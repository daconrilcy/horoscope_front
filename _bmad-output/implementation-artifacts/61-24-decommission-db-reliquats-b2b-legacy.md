# Story 61.24 : Décommission DB des reliquats B2B legacy

Status: done

## Story

En tant que développeur backend,
je veux migrer les services de facturation et de réconciliation B2B vers `feature_usage_counters` comme source de vérité canonique pour la lecture historique d'usage, puis supprimer la table `enterprise_daily_usages` et son modèle ORM via une migration Alembic,
afin que le schéma de base de données reflète la réalité applicative et ne contienne plus aucune table orpheline du système d'usage B2B legacy.

## Acceptance Criteria

### AC 1 — Migration des services consommateurs vers feature_usage_counters

1. `b2b_billing_service.py` : la méthode `_consumed_units_for_period()` est remplacée par une lecture directe sur `feature_usage_counters` comme source de vérité canonique, éventuellement au travers d'un helper dédié. Elle doit :
   - Résoudre l'`admin_user_id` de l'`EnterpriseAccountModel` correspondant à `account_id`
   - Interroger `feature_usage_counters` avec `user_id = admin_user_id`, `feature_code = "b2b_api_access"`, et `window_start >= period_start_utc` ET `window_start < next_month_start_utc` (fenêtre exclusive, convention ci-dessous)
   - Sommer `used_count` sur les lignes correspondantes
   - Ne plus importer ni référencer `EnterpriseDailyUsageModel`
   - **Ne pas** passer par `resolve_b2b_canonical_plan()` ni reconstruire une `QuotaDefinition` à partir du plan courant (le plan peut avoir changé depuis la période facturée)

2. `b2b_reconciliation_service.py` : la méthode `_usage_by_period()` est remplacée par une lecture directe sur `feature_usage_counters`. Elle doit :
   - Pour chaque `account_id` distinct (issu des cycles de facturation), résoudre son `admin_user_id`
   - Interroger `feature_usage_counters` avec les mêmes critères fenêtrés
   - Construire le même `dict[tuple[account_id, month_start, month_end], {"usage_units": int, "usage_rows": int}]` qu'actuellement
   - Ne plus importer ni référencer `EnterpriseDailyUsageModel`

### AC 2 — Convention de fenêtrage canonique

3. Dans `b2b_billing_service.py` et `b2b_reconciliation_service.py`, la fenêtre mensuelle est exprimée en **UTC datetimes** avec convention **inclusive/exclusive** :
   - `window_start` = premier jour du mois à 00:00:00 UTC (inclus)
   - `window_end` = premier jour du mois suivant à 00:00:00 UTC (exclu)
   - Le filtre SQL est : `window_start >= :month_start AND window_start < :next_month_start`
   - Aucune logique héritée du type `usage_date <= period_end` (convention legacy inclusive/inclusive sur des `Date`)

### AC 3 — Suppression du modèle ORM

4. Le fichier `backend/app/infra/db/models/enterprise_usage.py` est supprimé du dépôt.
5. Tous les imports de `EnterpriseDailyUsageModel` ou `from app.infra.db.models.enterprise_usage` sont retirés de tout le codebase Python opérationnel.

### AC 4 — Migration Alembic destructive

6. Une nouvelle migration Alembic est créée dans `backend/migrations/versions/` avec :
   - `down_revision` pointant vers la dernière migration existante (vérifier avec `alembic heads`)
   - `upgrade()` : suppression des index, puis `op.drop_table("enterprise_daily_usages")`
   - `downgrade()` : reconstruction complète de la table — migration réversible
7. La migration est chaînée correctement dans la séquence Alembic.

### AC 5 — Nettoyage des tests

8. Aucun test ne seed ni ne lit `EnterpriseDailyUsageModel` ou `enterprise_daily_usages`.
9. Les tests de billing (`test_b2b_billing_service.py`, `test_b2b_billing_api.py`) sont mis à jour pour seeder directement `feature_usage_counters` (insertion SQL directe ou via `QuotaUsageService.increment()`).
10. Les tests de réconciliation (`test_b2b_reconciliation_service.py`, `test_b2b_reconciliation_api.py`) idem.
11. Les autres tests qui importent `EnterpriseDailyUsageModel` pour le cleanup (`test_b2b_api_entitlements.py`, `test_b2b_usage_api.py`, `test_b2b_astrology_api.py`, `test_b2b_editorial_api.py`, `test_load_smoke_critical_flows.py`) sont nettoyés de cette référence.

### AC 6 — Vérification grep repo-wide

12. Un grep sur `backend/app/` et `backend/scripts/` retourne **zéro résultat** pour :
    - `EnterpriseDailyUsageModel`
    - `enterprise_daily_usages`
    - `from app.infra.db.models.enterprise_usage`
    Seule exception autorisée : la migration de création `20260220_0013` et la nouvelle migration de suppression (dans `backend/migrations/versions/`).

### AC 7 — Mise à jour de la documentation canonique

13. `backend/docs/entitlements-canonical-platform.md` est mis à jour pour acter que le legacy B2B a été supprimé jusqu'au niveau DB en story 61.24.

### AC 8 — Non-régression des suites canoniques

14. `pytest -q app/tests/integration/test_b2b_usage_api.py -v` — vert.
15. `pytest -q app/tests/integration/test_b2b_astrology_api.py -v` — vert.
16. `pytest -q app/tests/integration/test_b2b_entitlements_audit.py app/tests/integration/test_b2b_entitlement_repair.py app/tests/integration/test_b2b_api_entitlements.py app/tests/unit/test_b2b_api_entitlement_gate.py -v` — vert.
17. `pytest -q app/tests/integration/test_b2b_billing_api.py app/tests/unit/test_b2b_billing_service.py -v` — vert.
18. `pytest -q app/tests/integration/test_b2b_reconciliation_api.py app/tests/unit/test_b2b_reconciliation_service.py -v` — vert.
19. `pytest -q app/tests/integration/test_b2b_editorial_api.py -v` — vert.

## Tasks / Subtasks

- [x] **Audit de confirmation schéma** (précondition)
  - [x] Confirmer que `enterprise_usage.py` ne contient que `EnterpriseDailyUsageModel` (aucun modèle monthly séparé)
  - [x] Identifier la dernière migration Alembic (`alembic heads` ou dernier fichier dans `migrations/versions/`)
  - [x] Vérifier qu'aucune FK d'une autre table ne pointe vers `enterprise_daily_usages`

- [x] **Migrer `b2b_billing_service.py`** (AC: 1, 2)
  - [x] Dans `_consumed_units_for_period()`, remplacer le `SELECT SUM(used_count)` sur `enterprise_daily_usages` par une requête sur `feature_usage_counters` avec la convention de fenêtrage UTC exclusive
  - [x] Résoudre `admin_user_id` depuis `EnterpriseAccountModel` (ne pas passer par le plan courant)
  - [x] Supprimer l'import de `EnterpriseDailyUsageModel`

- [x] **Migrer `b2b_reconciliation_service.py`** (AC: 1, 2)
  - [x] Dans `_usage_by_period()`, remplacer la lecture de `enterprise_daily_usages` par une lecture canonique sur `feature_usage_counters`
  - [x] Supprimer l'import de `EnterpriseDailyUsageModel`

- [x] **Mettre à jour les tests de billing** (AC: 5)
  - [x] `test_b2b_billing_service.py` : réécrire `_seed_usage()` pour insérer dans `feature_usage_counters`
  - [x] `test_b2b_billing_api.py` : idem si applicable

- [x] **Mettre à jour les tests de réconciliation** (AC: 5)
  - [x] `test_b2b_reconciliation_service.py` : réécrire le seed usage vers `feature_usage_counters`
  - [x] `test_b2b_reconciliation_api.py` : idem

- [x] **Nettoyer les autres tests** (AC: 5)
  - [x] `test_b2b_api_entitlements.py` : supprimer import + référence dans `_cleanup_tables()`
  - [x] `test_b2b_usage_api.py` : supprimer import + références
  - [x] `test_b2b_astrology_api.py` : supprimer import + références
  - [x] `test_b2b_editorial_api.py` : supprimer import si présent
  - [x] `test_load_smoke_critical_flows.py` : supprimer import si présent

- [x] **Supprimer le modèle ORM** (AC: 3)
  - [x] `git rm backend/app/infra/db/models/enterprise_usage.py`
  - [x] Retirer l'import dans `backend/app/infra/db/models/__init__.py`

- [x] **Créer la migration Alembic de suppression** (AC: 4)
  - [x] Identifier le `down_revision` (`alembic heads`)
  - [x] Créer le fichier avec `upgrade()` → drop index + drop table, `downgrade()` → create table + index complets
  - [x] Nommer la migration : `20260327_0054_drop_enterprise_daily_usages.py`

- [x] **Vérification grep finale** (AC: 6)
  - [x] `grep -rn "EnterpriseDailyUsageModel\|enterprise_daily_usages" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__` → vide
  - [x] `grep -rn "from app.infra.db.models.enterprise_usage" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__` → vide

- [x] **Mettre à jour la documentation** (AC: 7)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Suite de non-régression complète** (AC: 8)
  - [x] Lancer tous les tests listés dans AC 8

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp (orchestrator)

### Debug Log References

### Completion Notes List

### File List
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/enterprise_usage.py` (supprimé)
- `backend/app/services/b2b_billing_service.py`
- `backend/app/services/b2b_reconciliation_service.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/app/tests/integration/test_b2b_billing_api.py`
- `backend/app/tests/unit/test_b2b_reconciliation_service.py`
- `backend/app/tests/integration/test_b2b_reconciliation_api.py`
- `backend/app/tests/integration/test_b2b_api_entitlements.py`
- `backend/app/tests/integration/test_b2b_usage_api.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `backend/app/tests/integration/test_b2b_editorial_api.py`
- `backend/app/tests/integration/test_load_smoke_critical_flows.py`
- `backend/migrations/versions/20260327_0054_drop_enterprise_daily_usages.py`
- `backend/docs/entitlements-canonical-platform.md`

### Change Log
- 2026-03-27 : Story créée. Audit schéma : seule table legacy = `enterprise_daily_usages`. Deux consommateurs actifs : `_consumed_units_for_period()` et `_usage_by_period()`. Bug latent confirmé (0 écritures depuis 61.21).
- 2026-03-27 : Corrections v2 appliquées : (1) billing/reco lisent directement `feature_usage_counters` sans passer par le plan courant ; (2) convention fenêtrage UTC exclusive documentée ; (3) `QuotaUsageService.get_usage()` retiré comme chemin principal pour billing/reco ; (4) chemins grep corrigés vers `backend/app/tests/`.
- 2026-03-27 : Story mise à jour (Done). Migration Alembic renommée et revision ID corrigée. Nettoyage final validé.

### Status
done

# Story 61.23 : Nettoyage final — suppression de B2BUsageService et des settings legacy

Status: done

## Story

En tant que développeur backend,
je veux supprimer définitivement `b2b_usage_service.py`, ses tests unitaires et les trois settings legacy `b2b_daily_usage_limit`, `b2b_monthly_usage_limit`, `b2b_usage_limit_mode`, ainsi que toutes leurs références résiduelles dans le code, les docs et les tests,
afin que le codebase ne contienne plus aucune trace opérationnelle du système de quota B2B legacy et que tout lecteur comprenne sans ambiguïté que `feature_usage_counters` via `QuotaUsageService` est l'unique source de vérité runtime.

## Acceptance Criteria

### AC 1 — Suppression des fichiers legacy

1. `backend/app/services/b2b_usage_service.py` est supprimé du dépôt.
2. `backend/app/tests/unit/test_b2b_usage_service.py` est supprimé du dépôt.

### AC 2 — Suppression des settings legacy

3. Les trois attributs suivants sont retirés de `app/core/config.py` (classe `Settings.__init__`) :
   - `self.b2b_daily_usage_limit`
   - `self.b2b_monthly_usage_limit`
   - `self.b2b_usage_limit_mode`
   L'annotation `# legacy unused since story 61.22` et les 4 lignes associées (lignes 219-224 actuelles) sont supprimées intégralement.

### AC 3 — Stabilisation et nettoyage de b2b_billing_service.py

4. Deux constantes de module sont ajoutées en tête de `b2b_billing_service.py`, avant toute classe :
   ```python
   DEFAULT_B2B_INCLUDED_MONTHLY_UNITS = 10000  # valeur historique B2B_MONTHLY_USAGE_LIMIT
   DEFAULT_B2B_LIMIT_MODE = "block"             # valeur historique B2B_USAGE_LIMIT_MODE
   ```
5. La ligne `included_monthly_units=settings.b2b_monthly_usage_limit` (ligne 149 actuelle) dans `_get_or_create_default_plan()` est remplacée par `included_monthly_units=DEFAULT_B2B_INCLUDED_MONTHLY_UNITS`.
6. Le bloc `limit_mode = settings.b2b_usage_limit_mode if … else "block"` (lignes 341-344 actuelles) est remplacée par `limit_mode = DEFAULT_B2B_LIMIT_MODE`. La variable `limit_mode` reste utilisée telle quelle sur la ligne suivante (`overage_applied`).
7. **Décision de comportement (tranchée) :** le mode overage legacy disparaît du chemin d'exécution par défaut. `overage_applied` sera désormais toujours `False` dans la clôture de cycle par défaut. Ce comportement est assumé et documenté.

### AC 4 — Réécriture de test_b2b_billing_close_cycle_calculates_fixed_and_variable

8. Les deux `monkeypatch.setattr` (lignes 77-78 actuelles) sont supprimés.
9. Le test est réécrit pour refléter le comportement stabilisé : `limit_mode = DEFAULT_B2B_LIMIT_MODE = "block"` → `overage_applied` est toujours `False`. Le test valide le **calcul fixe** (fixed_amount) et le calcul variable (billable_units × unit_price) en créant un plan billing avec `included_monthly_units=2` directement dans le setup du test — ce plan prévaut sur le plan par défaut via `_resolve_active_plan_for_account()`. L'assertion `overage_applied is True` est **supprimée** (ce comportement legacy ne doit plus être testé).
   - Concrètement : créer un `EnterpriseBillingPlanModel` avec `included_monthly_units=2` et `overage_unit_price_cents=X` et l'associer au compte via `EnterpriseAccountBillingPlanModel` avant d'appeler `close_cycle`. `used_count=5` donne alors `billable_units=3`, `variable_amount=3*X`.

### AC 5 — Nettoyage de la documentation canonique

7. La ligne 57 de `backend/docs/entitlements-canonical-platform.md` qui décrit le "Fallback Settings (Legacy)" via `B2BUsageService` est supprimée ou remplacée par une note historique indiquant que le fallback a été retiré en story 61.23.

### AC 6 — Nettoyage du script backfill

8. Les trois appels `report.add_non_migrated("settings.b2b_daily_usage_limit")`, `report.add_non_migrated("settings.b2b_monthly_usage_limit")`, `report.add_non_migrated("settings.b2b_usage_limit_mode")` (lignes 473-475 de `backend/scripts/backfill_plan_catalog_from_legacy.py`) sont supprimés. Ces settings n'existent plus — les laisser générerait un rapport mensonger.

### AC 7 — Vérification par grep (périmètre strict)

10. Un grep ciblé sur `backend/app/`, `backend/tests/` et `backend/scripts/` retourne **zéro résultat** pour chacun des quatre termes :
    - `B2BUsageService`
    - `b2b_daily_usage_limit`
    - `b2b_monthly_usage_limit`
    - `b2b_usage_limit_mode`
    Commandes exactes (voir section validation) : `grep -rn … backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__` → vide.
    Les seules références autorisées résident dans `_bmad-output/` (artefacts BMAD) et dans les fichiers `.md` historiques hors `backend/`. Aucune exception dans du code Python opérationnel.

### AC 8 — Non-régression des suites canoniques

10. `pytest -q app/tests/integration/test_b2b_usage_api.py -v` — vert (contrat canonique 61.22 inchangé).
11. `pytest -q app/tests/integration/test_b2b_astrology_api.py -v` — vert.
12. `pytest -q app/tests/integration/test_b2b_entitlements_audit.py app/tests/integration/test_b2b_entitlement_repair.py app/tests/integration/test_b2b_api_entitlements.py app/tests/unit/test_b2b_api_entitlement_gate.py -v` — vert.
13. `pytest -q app/tests/integration/test_b2b_billing_api.py app/tests/unit/test_b2b_billing_service.py -v` — vert (après nettoyage des monkeypatches).
14. Aucune migration Alembic destructive n'est créée dans cette story (les tables `b2b_daily_usage` restent en place).

## Tasks / Subtasks

- [x] **Supprimer b2b_usage_service.py** (AC: 1)
  - [x] `git rm backend/app/services/b2b_usage_service.py`

- [x] **Supprimer test_b2b_usage_service.py** (AC: 1)
  - [x] `git rm backend/app/tests/unit/test_b2b_usage_service.py`

- [x] **Nettoyer app/core/config.py** (AC: 2)
  - [x] Supprimer le commentaire `# legacy unused since story 61.22` et les 4 lignes de settings (219-224 actuelles)
  - [x] Vérifier qu'aucun autre endroit dans `config.py` ne référence ces settings

- [x] **Stabiliser b2b_billing_service.py** (AC: 3)
  - [x] Ajouter `DEFAULT_B2B_INCLUDED_MONTHLY_UNITS = 10000` et `DEFAULT_B2B_LIMIT_MODE = "block"` en tête de fichier (avant toute classe)
  - [x] Remplacer `settings.b2b_monthly_usage_limit` ligne 149 par `DEFAULT_B2B_INCLUDED_MONTHLY_UNITS`
  - [x] Remplacer le bloc `limit_mode = settings.b2b_usage_limit_mode if … else "block"` par `limit_mode = DEFAULT_B2B_LIMIT_MODE`
  - [x] Supprimer l'import de `settings` si plus utilisé dans ce fichier (`grep -n "settings\." backend/app/services/b2b_billing_service.py`)

- [x] **Réécrire test_b2b_billing_close_cycle_calculates_fixed_and_variable** (AC: 4)
  - [x] Supprimer les deux `monkeypatch.setattr` (lignes 77-78)
  - [x] Créer un `EnterpriseBillingPlanModel` avec `included_monthly_units=2` dans le setup du test et l'associer au compte via `EnterpriseAccountBillingPlanModel`
  - [x] Supprimer toute assertion sur `overage_applied is True` (comportement legacy retiré)
  - [x] Vérifier que fixed_amount et variable_amount sont corrects avec le nouveau plan

- [x] **Mettre à jour backend/docs/entitlements-canonical-platform.md** (AC: 5)
  - [x] Supprimer ou réécrire la ligne décrivant le "Fallback Settings (Legacy)"

- [x] **Nettoyer backfill_plan_catalog_from_legacy.py** (AC: 6)
  - [x] Supprimer les 3 appels `report.add_non_migrated` pour les settings legacy

- [x] **Vérification grep finale** (AC: 7)
  - [x] `grep -rn "B2BUsageService" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__` → vide
  - [x] `grep -rn "b2b_daily_usage_limit\|b2b_monthly_usage_limit\|b2b_usage_limit_mode" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__` → vide

- [x] **Lancer la suite de non-régression complète** (AC: 8)
  - [x] `cd backend && pytest -q app/tests/integration/test_b2b_usage_api.py app/tests/integration/test_b2b_astrology_api.py app/tests/integration/test_b2b_entitlements_audit.py app/tests/integration/test_b2b_entitlement_repair.py app/tests/integration/test_b2b_api_entitlements.py app/tests/unit/test_b2b_api_entitlement_gate.py app/tests/integration/test_b2b_billing_api.py app/tests/unit/test_b2b_billing_service.py -v`

## Dev Notes

### État actuel du codebase (après 61.22)

**Fichiers à supprimer entièrement :**
- `backend/app/services/b2b_usage_service.py` — porte déjà l'annotation `ZERO CONSUMERS` depuis 61.22, aucun consumer en production
- `backend/app/tests/unit/test_b2b_usage_service.py` — teste uniquement `B2BUsageService` (unité pure, pas de dépendance DB), devient orphelin

**Fichiers à modifier :**
- `backend/app/core/config.py` — lignes 219-224 (annotation + 3 settings + validation du mode)
- `backend/app/services/b2b_billing_service.py` — 2 références résiduelles aux settings
- `backend/app/tests/unit/test_b2b_billing_service.py` — 2 monkeypatches sur les settings
- `backend/docs/entitlements-canonical-platform.md` — 1 ligne de fallback legacy
- `backend/scripts/backfill_plan_catalog_from_legacy.py` — 3 lignes add_non_migrated

**Fichiers NON touchés (hors scope 61.23) :**
- Tout le reste du périmètre B2B canonique (gate, resolver, astrology, billing API…)
- Tables DB `b2b_daily_usage` — pas de migration Alembic dans cette story

### Décision tranchée : comportement billing et réécriture du test

**`b2b_billing_service.py`** — le mode overage legacy est retiré du chemin d'exécution par défaut. Les deux constantes ajoutées en tête de fichier figent le comportement :

```python
DEFAULT_B2B_INCLUDED_MONTHLY_UNITS = 10000  # valeur historique B2B_MONTHLY_USAGE_LIMIT
DEFAULT_B2B_LIMIT_MODE = "block"             # valeur historique B2B_USAGE_LIMIT_MODE
```

Avec `DEFAULT_B2B_LIMIT_MODE = "block"`, `overage_applied` sera toujours `False` dans la clôture de cycle. C'est le comportement assumé.

**`test_b2b_billing_close_cycle_calculates_fixed_and_variable`** (ligne 72 actuelle) — réécriture requise :

Le test ne peut plus patcher `settings` pour obtenir `included_monthly_units=2` et `mode=overage`. La nouvelle approche :

```python
def test_b2b_billing_close_cycle_calculates_fixed_and_variable() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()
    # Créer un plan avec 2 unités incluses et l'associer au compte
    with SessionLocal() as db:
        plan = EnterpriseBillingPlanModel(
            code="b2b_test_plan",
            display_name="Test Plan",
            monthly_fixed_cents=5000,
            included_monthly_units=2,
            overage_unit_price_cents=2,
            currency="EUR",
            is_active=True,
        )
        db.add(plan)
        db.flush()
        db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=account_id, plan_id=plan.id))
        db.commit()

    usage_day = date(2026, 2, 15)
    _seed_usage(account_id, credential_id, usage_day, used_count=5)
    # used=5, included=2 → billable=3, variable=6 cents, fixed=5000 → total=5006
    # overage_applied=False (DEFAULT_B2B_LIMIT_MODE="block")
    with SessionLocal() as db:
        cycle = B2BBillingService.close_cycle(db, account_id=account_id, ...)
        db.commit()
    assert cycle.snapshot["billable_units"] == 3
    assert cycle.snapshot["variable_amount_cents"] == 6
    assert cycle.snapshot["overage_applied"] is False  # block mode
```

L'assertion `overage_applied is True` est supprimée — ce comportement legacy n'existe plus dans le code par défaut.

### Vérification de l'import `settings` dans b2b_billing_service.py

Après remplacement des deux références, vérifier si `settings` est encore utilisé ailleurs dans le fichier :
```bash
grep -n "settings\." backend/app/services/b2b_billing_service.py
```
Si vide → supprimer l'import `from app.core.config import settings` (ou équivalent) en tête de fichier.

### Périmètre exact de la suppression dans config.py

Lignes actuelles 219-224 :
```python
        # legacy unused since story 61.22
        self.b2b_daily_usage_limit = int(os.getenv("B2B_DAILY_USAGE_LIMIT", "500"))
        self.b2b_monthly_usage_limit = int(os.getenv("B2B_MONTHLY_USAGE_LIMIT", "10000"))
        self.b2b_usage_limit_mode = os.getenv("B2B_USAGE_LIMIT_MODE", "block").strip().lower()
        if self.b2b_usage_limit_mode not in {"block", "overage"}:
            self.b2b_usage_limit_mode = "block"
```
→ Supprimer ces 6 lignes **intégralement** (commentaire + 3 attributs + validation).

### Mise à jour de la doc canonique

Dans `backend/docs/entitlements-canonical-platform.md`, la section "Priorité de Résolution B2B" (ligne 57 actuelle) :

**Avant :**
```
2. **Fallback Settings (Legacy)** : Si aucun binding canonique n'est trouvé, le flux historique via `B2BUsageService` et les settings `b2b_*` continue de s'appliquer.
```

**Après : Supprimer entièrement ce point 2 (le fallback n'existe plus). La section ne liste plus qu'un seul niveau de priorité : le système canonique.

### Invariant DB : pas de migration Alembic

Les tables `b2b_daily_usage` et `b2b_monthly_usage` (utilisées par `B2BUsageService`) **restent en place** dans la DB. Aucun `op.drop_table` ni `ALTER TABLE` dans cette story. Le cleanup DB est réservé à une story 61.24/61.25 après stabilisation en production.

### Commandes de validation

```bash
# Activer le venv
.\.venv\Scripts\Activate.ps1

# 1. Vérification grep (périmètre strict : app/ et scripts/ uniquement)
grep -rn "B2BUsageService" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__
# → attendu : aucun résultat

grep -rn "b2b_daily_usage_limit\|b2b_monthly_usage_limit\|b2b_usage_limit_mode" backend/app/ backend/scripts/ --include="*.py" | grep -v __pycache__
# → attendu : aucun résultat

# 2. Lint
cd backend && ruff check app/core/config.py app/services/b2b_billing_service.py app/tests/unit/test_b2b_billing_service.py

# 3. Suite de non-régression B2B complète
cd backend && pytest -q \
  app/tests/integration/test_b2b_usage_api.py \
  app/tests/integration/test_b2b_astrology_api.py \
  app/tests/integration/test_b2b_entitlements_audit.py \
  app/tests/integration/test_b2b_entitlement_repair.py \
  app/tests/integration/test_b2b_api_entitlements.py \
  app/tests/unit/test_b2b_api_entitlement_gate.py \
  app/tests/integration/test_b2b_billing_api.py \
  app/tests/unit/test_b2b_billing_service.py \
  -v
```

### Project Structure Notes

**Fichiers supprimés :**
- `backend/app/services/b2b_usage_service.py`
- `backend/app/tests/unit/test_b2b_usage_service.py`

**Fichiers modifiés :**
- `backend/app/core/config.py`
- `backend/app/services/b2b_billing_service.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/scripts/backfill_plan_catalog_from_legacy.py`

**Fichiers NON modifiés (hors scope) :**
- `backend/app/api/v1/routers/b2b_usage.py` — déjà migré en 61.22
- `backend/app/services/b2b_canonical_usage_service.py` — créé en 61.22, aucune modification
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/services/b2b_canonical_plan_resolver.py`
- `backend/app/services/quota_usage_service.py`
- `backend/app/tests/integration/test_b2b_usage_api.py` — déjà migré en 61.22
- `backend/app/tests/integration/test_b2b_astrology_api.py` — déjà migré en 61.22

### References

- [Source: backend/app/services/b2b_usage_service.py] — fichier à supprimer (ZERO CONSUMERS depuis 61.22)
- [Source: backend/app/tests/unit/test_b2b_usage_service.py] — fichier à supprimer
- [Source: backend/app/core/config.py#L219-224] — bloc legacy à supprimer entièrement
- [Source: backend/app/services/b2b_billing_service.py#L149,341-344] — 2 références aux settings à hardcoder
- [Source: backend/app/tests/unit/test_b2b_billing_service.py#L77-78] — monkeypatches à supprimer, test à adapter
- [Source: backend/docs/entitlements-canonical-platform.md#L57] — fallback legacy à retirer de la doc
- [Source: backend/scripts/backfill_plan_catalog_from_legacy.py#L473-475] — 3 lignes add_non_migrated à supprimer
- [Source: _bmad-output/implementation-artifacts/61-22-migration-usage-summary-canonique-retrait-final-b2busageservice.md] — story précédente, état du codebase post-61.22

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-001

### Debug Log References

### Completion Notes List
- Legacy B2B files removed and verified.
- `backend/app/core/config.py` cleaned of legacy B2B settings.
- `backend/app/services/b2b_billing_service.py` stabilized with hardcoded defaults.
- `backend/app/tests/unit/test_b2b_billing_service.py` updated to use explicit plan creation instead of monkeypatches.
- `backend/docs/entitlements-canonical-platform.md` documentation updated.
- `backend/scripts/backfill_plan_catalog_from_legacy.py` cleaned up.
- Full B2B non-regression test suite passed (58 tests).

### File List
- `backend/app/services/b2b_usage_service.py` (deleted)
- `backend/app/tests/unit/test_b2b_usage_service.py` (deleted)
- `backend/app/core/config.py`
- `backend/app/services/b2b_billing_service.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/docs/entitlements-canonical-platform.md`
- `backend/scripts/backfill_plan_catalog_from_legacy.py`

### Change Log
- 2026-03-27: Final cleanup of B2B legacy components. Removed unused services, settings, and updated related tests and docs.

### Status
review

# Story 61.25 : Compteurs canoniques B2B natifs via `enterprise_feature_usage_counters`

Status: ready-for-dev

## Story

En tant que développeur backend,
je veux introduire un stockage canonique natif des usages B2B indexé par `enterprise_account_id` au lieu du contournement actuel par `admin_user_id`,
afin que le modèle de données reflète correctement l'identité métier des comptes entreprise, que les compteurs ne dépendent plus d'un utilisateur administrateur particulier, et que le runtime B2B repose sur une source de vérité canonique proprement séparée du B2C.

## Acceptance Criteria

### AC 1 — Nouveau modèle DB natif B2B

1. Une nouvelle table `enterprise_feature_usage_counters` est créée via Alembic avec les colonnes suivantes :
   - `id` PK autoincrement
   - `enterprise_account_id` FK vers `enterprise_accounts.id` NOT NULL
   - `feature_code` String(64) NOT NULL
   - `quota_key` String(64) NOT NULL
   - `period_unit` String/Enum NOT NULL
   - `period_value` Integer NOT NULL
   - `reset_mode` String/Enum NOT NULL
   - `window_start` DateTime(timezone=True) NOT NULL
   - `window_end` DateTime(timezone=True) nullable
   - `used_count` Integer >= 0 NOT NULL (default=0)
   - `created_at`, `updated_at` DateTime(timezone=True)

2. Contrainte d'unicité métier :
   `UniqueConstraint("enterprise_account_id", "feature_code", "quota_key", "period_unit", "period_value", "reset_mode", "window_start", name="uq_enterprise_feature_usage_counters_composite")`

3. Index créés sur `(enterprise_account_id, feature_code, window_start)`, `enterprise_account_id`, `feature_code`.

4. Mêmes `CheckConstraint` que `feature_usage_counters` : `period_value >= 1`, `used_count >= 0`, `period_unit` valide, `reset_mode` valide, `window_end` requis sauf lifetime.

### AC 2 — Nouveau service canonique B2B `EnterpriseQuotaUsageService`

5. `EnterpriseQuotaUsageService` créé dans `backend/app/services/enterprise_quota_usage_service.py` avec :
   - `get_usage(db, *, account_id, feature_code, quota, ref_dt=None) -> UsageState`
   - `consume(db, *, account_id, feature_code, quota, amount=1, ref_dt=None) -> UsageState`
   - `_find_or_create_counter(db, *, account_id, feature_code, quota, window) -> EnterpriseFeatureUsageCounterModel`

6. Même sémantique que `QuotaUsageService` : `QuotaWindowResolver.compute_window()`, lecture idempotente, `SELECT FOR UPDATE` + savepoint `IntegrityError` recovery, `QuotaExhaustedError` si dépassement.

7. `EnterpriseQuotaUsageService` ne dépend **jamais** de `admin_user_id`.

8. Réutilise : `QuotaDefinition`, `UsageState` (depuis `entitlement_types`), `QuotaExhaustedError` (depuis `quota_usage_service`), `QuotaWindowResolver`.

### AC 3 — Migration des flux runtime B2B vers `enterprise_account_id`

9. **`B2BApiEntitlementGate.check_and_consume()`** :
   - Remplace `QuotaUsageService.consume(db, user_id=admin_user_id, ...)` par `EnterpriseQuotaUsageService.consume(db, account_id=account_id, ...)`
   - **Supprime le bloc `if not account or account.admin_user_id is None`** comme motif de blocage. Seule vérification conservée : le compte doit exister. L'absence de `admin_user_id` n'est plus un `403 b2b_account_not_configured` quota.
   - Supprime la résolution de `admin_user_id` et l'import de `QuotaUsageService`.

10. **`B2BCanonicalUsageSummaryService.get_summary()`** :
    - Remplace `QuotaUsageService.get_usage(db, user_id=admin_user_id, ...)` par `EnterpriseQuotaUsageService.get_usage(db, account_id=account_id, ...)`
    - Supprime le bloc `if not account or account.admin_user_id is None` comme motif de blocage quota.
    - Supprime l'import de `QuotaUsageService`.

11. **`B2BBillingService._consumed_units_for_period()`** :
    - Remplace la lecture `FeatureUsageCounterModel` filtrée par `admin_user_id` par une lecture `EnterpriseFeatureUsageCounterModel` filtrée par `enterprise_account_id == account_id`.
    - Supprime la résolution de `account.admin_user_id` dans cette méthode.
    - Nettoie les imports devenus inutiles (`FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode` si non utilisés ailleurs).

12. **`B2BReconciliationService._usage_by_period()`** :
    - Remplace la résolution `user_to_account` + lecture `FeatureUsageCounterModel.user_id.in_(...)` par une lecture directe `EnterpriseFeatureUsageCounterModel.enterprise_account_id.in_(account_ids)`.
    - Conserve la structure du dict retourné `dict[tuple[int, date, date], {"usage_units": int, "usage_rows": int}]`.
    - Supprime les imports `FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode`.

13. Après cette migration, **aucun flux runtime B2B ne lit ni n'écrit de compteur B2B dans `feature_usage_counters`**.

### AC 4 — Alignement de l'outillage ops (audit + repair)

14. **`B2BAuditService._audit_account()`** (`backend/app/services/b2b_audit_service.py`) :
    - Supprime le bloc `if not admin_user_id_present:` → `return B2BAuditEntry(resolution_source="settings_fallback", reason="admin_user_id_missing")` (L.243-260 du fichier actuel). L'absence de `admin_user_id` ne produit plus un `settings_fallback` dans le chemin quota.
    - Remplace `QuotaUsageService.get_usage(db, user_id=account.admin_user_id, ...)` (L.412-416) par `EnterpriseQuotaUsageService.get_usage(db, account_id=account.id, ...)`.
    - Le champ `admin_user_id_present: bool` dans `B2BAuditEntry` **peut rester** comme métadonnée d'intégrité (information sur la complétude du compte) mais **ne conditionne plus** la `resolution_source`.
    - Le Literal `reason` peut conserver `"admin_user_id_missing"` comme valeur possible pour la métadonnée d'intégrité (s'il reste utile) mais **ne doit plus apparaître** comme motif de blocage `settings_fallback`.

15. **`B2BEntitlementRepairService.run_auto_repair()`** (`backend/app/services/b2b_entitlement_repair_service.py`) :
    - Supprime le bloc `if audit_entry.reason == "admin_user_id_missing":` → `report.remaining_blockers.append(RepairBlockerEntry(..., recommended_action="set_admin_user"))` (L.155-164). Ce cas ne doit plus être traité comme un blocker quota.
    - `set_admin_user()` reste fonctionnel pour la gestion d'ownership/authentification du compte, mais n'est plus présenté comme prérequis à la consommation quota.

16. Après cette migration, un compte B2B actif avec plan canonique + binding valide peut consommer et lire son quota même si `admin_user_id` est null.

### AC 5 — Migration des données historiques

17. Script `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py` :
    - Lit `feature_usage_counters` filtrant `feature_code="b2b_api_access"`
    - Résout `enterprise_account_id` via `EnterpriseAccountModel.admin_user_id == row.user_id`
    - Upsert dans `enterprise_feature_usage_counters` par clé métier composite ; en cas de conflit : `used_count = max(existing.used_count, migrated.used_count)`
    - Supporte `--dry-run`

18. Le script loggue **distinctement** les catégories suivantes :
    - `migrated` : ligne copiée avec succès
    - `already_present` : ligne déjà présente (upsert no-op)
    - `skipped_no_account` : `user_id` sans `EnterpriseAccountModel.admin_user_id` correspondant — logguée comme anomalie explicite, non silencieuse
    - `skipped_multiple_accounts` : `user_id` mappé à plusieurs comptes (ne devrait pas arriver, `admin_user_id` est `unique`, mais guard explicite)
    - `anomalies` : toute autre erreur inattendue avec stacktrace

19. La migration est idempotente : relance sans doublon ni perte.

### AC 6 — Séquence de déploiement en production

20. La bascule prod **respecte l'ordre suivant sans exception** :

    1. **Alembic `upgrade`** : création de `enterprise_feature_usage_counters`
    2. **Migration historique** : exécution du script en `--dry-run` puis en mode réel
    3. **Validation des volumes** : comparer le count `enterprise_feature_usage_counters` avec le count `feature_usage_counters WHERE feature_code='b2b_api_access'`
    4. **Déploiement du runtime** : déployer le code qui lit/écrit la nouvelle table

    **Aucun déploiement du code runtime (étape 4) ne doit précéder l'exécution de la migration historique (étape 2-3).** Sinon billing/reconciliation/usage summary liront zéro pendant la fenêtre entre création de table et migration.

21. La story documente ces étapes dans les Dev Notes et dans le changelog de déploiement.

### AC 7 — Bascule franche

22. Pas de double écriture runtime : migration historique **puis** runtime B2B sur nouvelle table uniquement.
23. `feature_usage_counters` continue d'exister pour le B2C sans modification.
24. `QuotaUsageService` continue d'être utilisé pour le B2C uniquement.

### AC 8 — Tests et non-régression

25. Tests unitaires `backend/app/tests/unit/test_enterprise_quota_usage_service.py` : [x]
    - [x] `get_usage` compteur absent → `used=0`
    - [x] `get_usage` compteur existant
    - [x] `consume` initiale → compteur créé
    - [x] `consume` jusqu'au quota → `QuotaExhaustedError`
    - [x] Pattern find-or-create (atomicité)
    - [x] Fenêtre mensuelle UTC correcte

26. Tests d'intégration adaptés :
    - `test_b2b_billing_service.py`, `test_b2b_billing_api.py` : `_seed_usage()` → `EnterpriseFeatureUsageCounterModel` par `enterprise_account_id`
    - `test_b2b_reconciliation_service.py`, `test_b2b_reconciliation_api.py` : idem
    - `test_b2b_astrology_api.py`, `test_b2b_usage_api.py` : idem
    - Vérification explicite qu'aucune écriture B2B runtime n'apparaît dans `feature_usage_counters`

27. Tests d'intégration audit/repair : vérifier qu'un compte sans `admin_user_id` mais avec plan canonique valide passe en `canonical_quota` ou `canonical_unlimited` (et non plus `settings_fallback`).

28. Les suites B2C existantes passent sans modification métier.

### AC 9 — Nettoyage et documentation

29. `B2BApiEntitlementGate`, `B2BCanonicalUsageSummaryService`, `B2BAuditService`, `b2b_billing_service.py`, `b2b_reconciliation_service.py` et `b2b_entitlement_repair_service.py` n'utilisent plus `admin_user_id` comme clé de quota/usage.

30. `backend/docs/entitlements-canonical-platform.md` est mis à jour pour :
    - Documenter la séparation B2C (`feature_usage_counters`) / B2B (`enterprise_feature_usage_counters`)
    - Acter la suppression du compromis `user_id = admin_user_id` en 61.25
    - Indiquer que `admin_user_id` reste pour l'ownership/auth du compte mais n'est plus prérequis quota

## Tasks / Subtasks

- [x] **Créer le modèle ORM B2B natif** (AC: 1)
  - [x] Créer `backend/app/infra/db/models/enterprise_feature_usage_counters.py` avec `EnterpriseFeatureUsageCounterModel`
  - [x] Reprendre la structure de `FeatureUsageCounterModel`, remplacer `user_id` FK→`users.id` par `enterprise_account_id` FK→`enterprise_accounts.id`
  - [x] Déclarer `CheckConstraint`, `UniqueConstraint` et `Index` (noms préfixés `enterprise_fuc_`)
  - [x] Enregistrer dans `backend/app/infra/db/models/__init__.py`

- [x] **Créer la migration Alembic** (AC: 1)
  - [x] `down_revision = "20260327_0054"`
  - [x] Nommer : `20260327_0055_create_enterprise_feature_usage_counters.py`
  - [x] `upgrade()` : create_table + index + FK + contraintes
  - [x] `downgrade()` : drop_table propre

- [x] **Créer `EnterpriseQuotaUsageService`** (AC: 2)
  - [x] Créer `backend/app/services/enterprise_quota_usage_service.py`
  - [x] Implémenter `get_usage`, `consume`, `_find_or_create_counter`
  - [x] Pattern `SELECT FOR UPDATE` + savepoint `IntegrityError` (voir `quota_usage_service.py` L.125-172)

- [x] **Créer le script de migration des données** (AC: 5)
  - [x] Créer `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py`
  - [x] Lire `feature_usage_counters` WHERE `feature_code="b2b_api_access"`
  - [x] Résoudre `enterprise_account_id` via `admin_user_id`
  - [x] Upsert idempotent avec logging 5 catégories distinctes
  - [x] Support `--dry-run`

- [x] **Migrer `B2BApiEntitlementGate`** (AC: 3, 4)
  - [x] Supprimer le bloc `if not account or account.admin_user_id is None` comme motif de blocage quota
  - [x] Remplacer `QuotaUsageService.consume(user_id=admin_user_id)` par `EnterpriseQuotaUsageService.consume(account_id=account_id)`
  - [x] Supprimer l'import `QuotaUsageService`

- [x] **Migrer `B2BCanonicalUsageSummaryService`** (AC: 3, 4)
  - [x] Supprimer le bloc `admin_user_id is None` comme motif de blocage quota
  - [x] Remplacer `QuotaUsageService.get_usage(user_id=admin_user_id)` par `EnterpriseQuotaUsageService.get_usage(account_id=account_id)`
  - [x] Supprimer l'import `QuotaUsageService`

- [x] **Migrer `B2BAuditService`** (AC: 4)
  - [x] Supprimer le bloc `if not admin_user_id_present: return B2BAuditEntry(reason="admin_user_id_missing")` (L.243-260)
  - [x] Remplacer `QuotaUsageService.get_usage(db, user_id=account.admin_user_id)` par `EnterpriseQuotaUsageService.get_usage(account_id=account.id)` (L.412-416)
  - [x] Conserver `admin_user_id_present` comme métadonnée d'intégrité dans `B2BAuditEntry` mais ne plus en faire une condition de `resolution_source`

- [x] **Migrer `B2BEntitlementRepairService`** (AC: 4)
  - [x] Supprimer le bloc `if audit_entry.reason == "admin_user_id_missing"` → blocker (L.155-164)
  - [x] `set_admin_user()` reste fonctionnel mais n'est plus un prérequis quota

- [x] **Migrer `b2b_billing_service.py`** (AC: 3)
  - [x] Dans `_consumed_units_for_period()` : lire `EnterpriseFeatureUsageCounterModel` par `enterprise_account_id`
  - [x] Supprimer résolution `admin_user_id` et imports `FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode`

- [x] **Migrer `b2b_reconciliation_service.py`** (AC: 3)
  - [x] Remplacer résolution `user_to_account` par lecture directe `enterprise_account_id.in_(...)`
  - [x] Supprimer imports `FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode`

- [x] **Adapter les tests de billing** (AC: 8)
  - [x] `test_b2b_billing_service.py` : `_seed_usage()` → `EnterpriseFeatureUsageCounterModel` par `enterprise_account_id`
  - [x] `test_b2b_billing_api.py` : idem

- [x] **Adapter les tests de réconciliation et intégration** (AC: 8)
  - [x] `test_b2b_reconciliation_service.py`, `test_b2b_reconciliation_api.py` : idem
  - [x] `test_b2b_astrology_api.py`, `test_b2b_usage_api.py` : idem
  - [x] Ajouter assertion que `feature_usage_counters` ne reçoit pas d'écriture B2B runtime

- [x] **Adapter les tests audit/repair** (AC: 8)
  - [x] `test_b2b_entitlements_audit.py` : vérifier qu'un compte sans `admin_user_id` mais avec plan valide passe en `canonical_quota`/`canonical_unlimited`
  - [x] `test_b2b_entitlement_repair.py` : idem, blocker `admin_user_id_missing` ne doit plus apparaître

- [x] **Mettre à jour la documentation** (AC: 9)
  - [x] `backend/docs/entitlements-canonical-platform.md`

- [x] **Suite de non-régression complète**
  - [x] `ruff check` sur tous les fichiers modifiés
  - [x] Lancer la suite pytest complète B2B

## Dev Notes

### Décision d'architecture

Table dédiée `enterprise_feature_usage_counters` (pas de modification de `feature_usage_counters`). Séparation nette B2C / B2B. Pas de table polymorphe ambiguë.

---

### Pattern `EnterpriseQuotaUsageService` — Guide précis

Copier/adapter depuis `backend/app/services/quota_usage_service.py` en remplaçant :
- `user_id: int` → `account_id: int`
- `FeatureUsageCounterModel` → `EnterpriseFeatureUsageCounterModel`
- `FeatureUsageCounterModel.user_id == user_id` → `EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id`

```python
from app.infra.db.models.enterprise_feature_usage_counters import EnterpriseFeatureUsageCounterModel
from app.services.entitlement_types import QuotaDefinition, UsageState
from app.services.quota_usage_service import QuotaExhaustedError  # réutiliser, ne pas recréer
from app.services.quota_window_resolver import QuotaWindowResolver

class EnterpriseQuotaUsageService:
    @staticmethod
    def get_usage(db, *, account_id: int, feature_code: str, quota: QuotaDefinition, ref_dt=None) -> UsageState:
        ...  # même logique que QuotaUsageService.get_usage

    @staticmethod
    def consume(db, *, account_id: int, feature_code: str, quota: QuotaDefinition, amount: int = 1, ref_dt=None) -> UsageState:
        ...  # même logique que QuotaUsageService.consume

    @staticmethod
    def _find_or_create_counter(db, *, account_id, feature_code, quota, window):
        # Pattern exact : quota_usage_service.py L.125-172
        # SELECT FOR UPDATE + with db.begin_nested() + IntegrityError recovery
        ...
```

---

### Migration `B2BApiEntitlementGate` — Diff essentiel

**Avant** (L.63-77 + L.142-148) :
```python
account = db.scalar(select(EnterpriseAccountModel).where(...))
if not account or account.admin_user_id is None:  # ← SUPPRIMER le check admin_user_id
    raise B2BApiAccessDeniedError(code="b2b_account_not_configured", ...)
admin_user_id = account.admin_user_id
...
state = QuotaUsageService.consume(db, user_id=admin_user_id, ...)
```

**Après** :
```python
account = db.scalar(select(EnterpriseAccountModel).where(...))
if not account:  # seule vérification d'existence
    raise B2BApiAccessDeniedError(code="b2b_account_not_configured", ...)
# admin_user_id plus nécessaire ici
...
state = EnterpriseQuotaUsageService.consume(db, account_id=account_id, ...)
```

---

### Migration `B2BAuditService` — Diff essentiel

**Avant** (L.241-260) — early return sur `admin_user_id_missing` :
```python
admin_user_id_present = account.admin_user_id is not None
if not admin_user_id_present:
    return B2BAuditEntry(
        resolution_source="settings_fallback",
        reason="admin_user_id_missing",
        ...
    )
```

**Après** — ne plus interrompre le chemin quota. Conserver le field `admin_user_id_present` pour la métadonnée :
```python
admin_user_id_present = account.admin_user_id is not None
# Ne pas faire de return early ici — continuer vers le plan canonique
# admin_user_id_present reste disponible pour l'afficher dans l'entrée d'audit
```

**Avant** (L.412-416) :
```python
usage_state = QuotaUsageService.get_usage(
    db,
    user_id=account.admin_user_id,
    ...
)
```

**Après** :
```python
usage_state = EnterpriseQuotaUsageService.get_usage(
    db,
    account_id=account.id,
    ...
)
```

---

### Migration `B2BEntitlementRepairService` — Diff essentiel

**Avant** (L.155-164) :
```python
if audit_entry.reason == "admin_user_id_missing":
    report.remaining_blockers.append(
        RepairBlockerEntry(..., recommended_action="set_admin_user")
    )
    continue
```

**Après** : supprimer ce bloc. `set_admin_user()` reste disponible via l'endpoint existant pour la gestion d'ownership, mais n'est plus un prérequis quota dans `run_auto_repair`.

---

### Migration `b2b_billing_service._consumed_units_for_period()` — Diff essentiel

**Avant** — résolution `admin_user_id` + lecture `FeatureUsageCounterModel` :
```python
account = db.scalar(select(EnterpriseAccountModel).where(...))
if not account or account.admin_user_id is None:
    return 0
value = db.scalar(
    select(func.coalesce(func.sum(FeatureUsageCounterModel.used_count), 0)).where(
        FeatureUsageCounterModel.user_id == account.admin_user_id,
        FeatureUsageCounterModel.feature_code == "b2b_api_access",
        FeatureUsageCounterModel.period_unit == PeriodUnit.MONTH,
        FeatureUsageCounterModel.reset_mode == ResetMode.CALENDAR,
        FeatureUsageCounterModel.window_start >= month_start_utc,
        FeatureUsageCounterModel.window_start < next_month_utc,
    )
)
```

**Après** — lecture directe par `enterprise_account_id` :
```python
value = db.scalar(
    select(func.coalesce(func.sum(EnterpriseFeatureUsageCounterModel.used_count), 0)).where(
        EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id,
        EnterpriseFeatureUsageCounterModel.feature_code == "b2b_api_access",
        EnterpriseFeatureUsageCounterModel.window_start >= month_start_utc,
        EnterpriseFeatureUsageCounterModel.window_start < next_month_utc,
    )
)
```

**⚠️ Conserver la convention UTC exclusive** : `window_start >= month_start`, `window_start < next_month`. Identique à 61.24.

---

### Migration `b2b_reconciliation_service._usage_by_period()` — Diff essentiel

**Avant** : résolution `user_to_account` + `FeatureUsageCounterModel.user_id.in_(user_ids)`.

**Après** :
```python
# 1. Collecter les account_ids
account_ids_query = select(EnterpriseAccountModel.id)
if account_id is not None:
    account_ids_query = account_ids_query.where(EnterpriseAccountModel.id == account_id)
account_ids = [row.id for row in db.execute(account_ids_query).all()]

if not account_ids:
    return {}

# 2. Lire enterprise_feature_usage_counters directement
counter_query = select(
    EnterpriseFeatureUsageCounterModel.enterprise_account_id,
    EnterpriseFeatureUsageCounterModel.window_start,
    EnterpriseFeatureUsageCounterModel.used_count,
).where(
    EnterpriseFeatureUsageCounterModel.enterprise_account_id.in_(account_ids),
    EnterpriseFeatureUsageCounterModel.feature_code == "b2b_api_access",
)
# ... filtres période UTC exclusifs identiques à 61.24
```

Le dict retourné reste `dict[tuple[int, date, date], {"usage_units": int, "usage_rows": int}]`. Aucun changement dans `list_issues()`.

---

### Pattern seed canonique pour les tests

```python
from app.infra.db.models.enterprise_feature_usage_counters import EnterpriseFeatureUsageCounterModel

def _seed_b2b_usage(account_id: int, usage_date, used_count: int) -> None:
    with SessionLocal() as db:
        window_start = datetime(usage_date.year, usage_date.month, 1, tzinfo=timezone.utc)
        if usage_date.month == 12:
            window_end = datetime(usage_date.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            window_end = datetime(usage_date.year, usage_date.month + 1, 1, tzinfo=timezone.utc)
        db.add(EnterpriseFeatureUsageCounterModel(
            enterprise_account_id=account_id,  # ← directement, sans admin_user_id
            feature_code="b2b_api_access",
            quota_key="b2b_api_access_monthly",
            period_unit="month",
            period_value=1,
            reset_mode="calendar",
            window_start=window_start,
            window_end=window_end,
            used_count=used_count,
        ))
        db.commit()
```

---

### Migration Alembic — Template prêt à copier

```python
"""create enterprise_feature_usage_counters

Revision ID: 20260327_0055
Revises: 20260327_0054
Create Date: 2026-03-27
"""
import sqlalchemy as sa
from alembic import op

revision = "20260327_0055"
down_revision = "20260327_0054"

def upgrade() -> None:
    op.create_table(
        "enterprise_feature_usage_counters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("feature_code", sa.String(64), nullable=False),
        sa.Column("quota_key", sa.String(64), nullable=False),
        sa.Column("period_unit", sa.String(16), nullable=False),
        sa.Column("period_value", sa.Integer(), nullable=False),
        sa.Column("reset_mode", sa.String(16), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("period_value >= 1", name="ck_enterprise_fuc_period_value_positive"),
        sa.CheckConstraint("used_count >= 0", name="ck_enterprise_fuc_used_count_non_negative"),
        sa.CheckConstraint(
            "LOWER(period_unit) IN ('day', 'week', 'month', 'year', 'lifetime')",
            name="ck_enterprise_fuc_period_unit_valid",
        ),
        sa.CheckConstraint(
            "LOWER(reset_mode) IN ('calendar', 'rolling', 'lifetime')",
            name="ck_enterprise_fuc_reset_mode_valid",
        ),
        sa.CheckConstraint(
            "LOWER(period_unit) = 'lifetime' OR window_end IS NOT NULL",
            name="ck_enterprise_fuc_window_end_required",
        ),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id", "feature_code", "quota_key",
            "period_unit", "period_value", "reset_mode", "window_start",
            name="uq_enterprise_feature_usage_counters_composite",
        ),
    )
    op.create_index("ix_enterprise_fuc_account_id", "enterprise_feature_usage_counters", ["enterprise_account_id"])
    op.create_index("ix_enterprise_fuc_feature_code", "enterprise_feature_usage_counters", ["feature_code"])
    op.create_index(
        "ix_enterprise_fuc_account_feature_window",
        "enterprise_feature_usage_counters",
        ["enterprise_account_id", "feature_code", "window_start"],
    )

def downgrade() -> None:
    op.drop_index("ix_enterprise_fuc_account_feature_window", table_name="enterprise_feature_usage_counters")
    op.drop_index("ix_enterprise_fuc_feature_code", table_name="enterprise_feature_usage_counters")
    op.drop_index("ix_enterprise_fuc_account_id", table_name="enterprise_feature_usage_counters")
    op.drop_table("enterprise_feature_usage_counters")
```

---

### Runbook de déploiement prod (AC 6)

```bash
# ÉTAPE 1 — Migration Alembic (création table)
cd backend && alembic upgrade head
# Vérifier que enterprise_feature_usage_counters existe et est vide

# ÉTAPE 2 — Dry-run migration historique
python scripts/migrate_b2b_usage_counters_to_enterprise_counters.py --dry-run
# Inspecter les logs : migrated, already_present, skipped_no_account, skipped_multiple_accounts, anomalies

# ÉTAPE 3 — Migration historique réelle
python scripts/migrate_b2b_usage_counters_to_enterprise_counters.py
# Relancer autant de fois que nécessaire (idempotent)

# ÉTAPE 4 — Validation des volumes
# SELECT COUNT(*) FROM enterprise_feature_usage_counters;
# SELECT COUNT(*) FROM feature_usage_counters WHERE feature_code='b2b_api_access';
# Les deux counts doivent être cohérents (+ anomalies skippées)

# ÉTAPE 5 — Déploiement du code runtime
# Seulement après validation étape 4
```

---

### Commandes de validation

```bash
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check \
  app/services/enterprise_quota_usage_service.py \
  app/services/b2b_api_entitlement_gate.py \
  app/services/b2b_canonical_usage_service.py \
  app/services/b2b_audit_service.py \
  app/services/b2b_entitlement_repair_service.py \
  app/services/b2b_billing_service.py \
  app/services/b2b_reconciliation_service.py

# Suite B2B complète
cd backend && pytest -q \
  app/tests/unit/test_enterprise_quota_usage_service.py \
  app/tests/unit/test_b2b_api_entitlement_gate.py \
  app/tests/unit/test_b2b_billing_service.py \
  app/tests/unit/test_b2b_reconciliation_service.py \
  app/tests/integration/test_b2b_astrology_api.py \
  app/tests/integration/test_b2b_usage_api.py \
  app/tests/integration/test_b2b_billing_api.py \
  app/tests/integration/test_b2b_reconciliation_api.py \
  app/tests/integration/test_b2b_api_entitlements.py \
  app/tests/integration/test_b2b_entitlements_audit.py \
  app/tests/integration/test_b2b_entitlement_repair.py \
  -v
```

---

### Invariants forts après 61.25

| Flux | Table | Service |
|---|---|---|
| B2B runtime (gate, summary, billing, reco, audit) | `enterprise_feature_usage_counters` | `EnterpriseQuotaUsageService` |
| B2C runtime (chat, natal, consultations) | `feature_usage_counters` | `QuotaUsageService` |

**`admin_user_id` : ownership/auth du compte uniquement. Plus aucun chemin quota/usage B2B n'en dépend.**

---

### Hors périmètre

- Ne pas modifier `QuotaUsageService` ni `feature_usage_counters`
- Ne pas supprimer `admin_user_id` de `EnterpriseAccountModel`
- Ne pas modifier les endpoints publics ni les contrats API
- Ne pas fusionner B2C et B2B dans une table unique

### Project Structure Notes

**Nouveaux fichiers :**
- `backend/app/infra/db/models/enterprise_feature_usage_counters.py`
- `backend/app/services/enterprise_quota_usage_service.py`
- `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py`
- `backend/app/tests/unit/test_enterprise_quota_usage_service.py`
- `backend/migrations/versions/20260327_0055_create_enterprise_feature_usage_counters.py`

**Fichiers modifiés :**
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/services/b2b_canonical_usage_service.py`
- `backend/app/services/b2b_audit_service.py` — supprimer early-return `admin_user_id_missing`, migrer `QuotaUsageService.get_usage`
- `backend/app/services/b2b_entitlement_repair_service.py` — supprimer blocker `admin_user_id_missing`
- `backend/app/services/b2b_billing_service.py`
- `backend/app/services/b2b_reconciliation_service.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/app/tests/integration/test_b2b_billing_api.py`
- `backend/app/tests/unit/test_b2b_reconciliation_service.py`
- `backend/app/tests/integration/test_b2b_reconciliation_api.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `backend/app/tests/integration/test_b2b_usage_api.py`
- `backend/app/tests/integration/test_b2b_entitlements_audit.py`
- `backend/app/tests/integration/test_b2b_entitlement_repair.py`
- `backend/docs/entitlements-canonical-platform.md`

### References

- [Source: backend/app/services/quota_usage_service.py] — pattern exact pour `EnterpriseQuotaUsageService`
- [Source: backend/app/infra/db/models/product_entitlements.py#L217-280] — `FeatureUsageCounterModel` (structure source)
- [Source: backend/app/services/b2b_api_entitlement_gate.py#L62-77] — bloc `admin_user_id` à supprimer du chemin quota
- [Source: backend/app/services/b2b_api_entitlement_gate.py#L142-148] — `QuotaUsageService.consume` à migrer
- [Source: backend/app/services/b2b_canonical_usage_service.py#L113-129] — `QuotaUsageService.get_usage` à migrer
- [Source: backend/app/services/b2b_audit_service.py#L243-260] — early-return `admin_user_id_missing` à supprimer
- [Source: backend/app/services/b2b_audit_service.py#L412-416] — `QuotaUsageService.get_usage(user_id=admin_user_id)` à migrer
- [Source: backend/app/services/b2b_entitlement_repair_service.py#L155-164] — blocker `admin_user_id_missing` à supprimer
- [Source: backend/app/services/b2b_billing_service.py#L231-263] — `_consumed_units_for_period` à migrer
- [Source: backend/app/services/b2b_reconciliation_service.py#L292-359] — `_usage_by_period` à migrer
- [Source: backend/app/tests/unit/test_b2b_billing_service.py#L62-90] — `_seed_usage()` à migrer
- [Source: backend/migrations/versions/20260327_0054_drop_enterprise_daily_usages.py] — dernière migration (`down_revision` cible)
- [Source: backend/app/infra/db/models/enterprise_account.py] — `admin_user_id` reste mais n'est plus clé quota

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

**Nouveaux fichiers :**
- `backend/app/infra/db/models/enterprise_feature_usage_counters.py`
- `backend/app/services/enterprise_quota_usage_service.py`
- `backend/scripts/migrate_b2b_usage_counters_to_enterprise_counters.py`
- `backend/app/tests/unit/test_enterprise_quota_usage_service.py`
- `backend/migrations/versions/20260327_0055_create_enterprise_feature_usage_counters.py`

**Fichiers modifiés :**
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/services/b2b_canonical_usage_service.py`
- `backend/app/services/b2b_audit_service.py`
- `backend/app/services/b2b_entitlement_repair_service.py`
- `backend/app/services/b2b_billing_service.py`
- `backend/app/services/b2b_reconciliation_service.py`
- `backend/app/tests/unit/test_b2b_billing_service.py`
- `backend/app/tests/integration/test_b2b_billing_api.py`
- `backend/app/tests/unit/test_b2b_reconciliation_service.py`
- `backend/app/tests/integration/test_b2b_reconciliation_api.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `backend/app/tests/integration/test_b2b_usage_api.py`
- `backend/app/tests/integration/test_b2b_entitlements_audit.py`
- `backend/app/tests/integration/test_b2b_entitlement_repair.py`
- `backend/app/tests/unit/test_b2b_entitlement_repair_service.py`
- `backend/docs/entitlements-canonical-platform.md`

### Change Log
- 2026-03-27 : Story créée. Analyse codebase post-61.24.
- 2026-03-27 : v2 — 4 corrections intégrées : (1) suppression `admin_user_id` du chemin quota dans gate/summary/audit ; (2) migration `B2BAuditService` (early-return + `QuotaUsageService`) et `B2BEntitlementRepairService` (blocker) ; (3) runbook de déploiement prod ordonné ; (4) logging migration 5 catégories distinctes (`migrated`, `already_present`, `skipped_no_account`, `skipped_multiple_accounts`, `anomalies`).
- 2026-03-27 : Implémentation complète de la story 61.25.
- 2026-03-27 : Code Review effectuée et corrections de lint/tests appliquées.

### Status
done

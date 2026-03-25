# Story 61.10 : QuotaWindowResolver + QuotaUsageService — moteur de fenêtres et consommation réelle

## Tasks / Subtasks

- [x] **Créer `entitlement_types.py`** — module tiers, **première étape obligatoire** (AC: 20, 21, 25)
  - [x] Créer `backend/app/services/entitlement_types.py`
  - [x] Y déplacer `QuotaDefinition` (dataclass frozen=True) depuis `entitlement_service.py`
  - [x] Y déplacer `FeatureEntitlement` (dataclass mutable) depuis `entitlement_service.py`
  - [x] Ajouter les champs `usage_states: list[UsageState]` et `quota_exhausted: bool` à `FeatureEntitlement`
  - [x] Mettre à jour `entitlement_service.py` pour importer depuis `entitlement_types`
  - [x] Vérifier que tous les tests existants passent après refactoring des imports

- [x] **Créer `QuotaWindowResolver`** dans `backend/app/services/quota_window_resolver.py` (AC: 1-8)
  - [x] Implémenter `compute_window(period_unit, period_value, reset_mode, ref_dt) → QuotaWindow`
  - [x] Normaliser `ref_dt` en UTC en début de méthode : `ref_dt = ref_dt.astimezone(timezone.utc)` ; lever `ValueError` si naïf
  - [x] Lever `ValueError` si `reset_mode=rolling`
  - [x] Cas `lifetime` : `window_start = datetime(1970, 1, 1, tzinfo=UTC)`, `window_end = None`
  - [x] Cas `calendar/day` : slot = `days_since_epoch // period_value` depuis UNIX_EPOCH ; `window_end = window_start + timedelta(days=period_value)`
  - [x] Cas `calendar/week` : slot depuis WEEK_ANCHOR (1969-12-29) ; `window_end = window_start + timedelta(weeks=period_value)`
  - [x] Cas `calendar/month` : `slot = (year*12 + month - 1) // period_value` ; utiliser l'algorithme divmod pour window_start et window_end
  - [x] Cas `calendar/year` : `slot = year // period_value` ; `window_start = datetime(slot*N, 1, 1, UTC)`, `window_end = datetime((slot+1)*N, 1, 1, UTC)`
  - [x] Vérifier l'invariant trimestre : `period_unit=month, period_value=3` → slots Jan/Apr/Jul/Oct
  - [x] Toutes les datetimes retournées ont `tzinfo=timezone.utc`

- [x] **Créer `QuotaUsageService`** dans `backend/app/services/quota_usage_service.py` (AC: 9-19)
  - [x] Importer `QuotaDefinition` depuis `app.services.entitlement_types` (pas depuis `entitlement_service`)
  - [x] Définir `QuotaExhaustedError` avec attributs `quota_key`, `used`, `limit`, `feature_code`
  - [x] Définir `UsageState` dataclass (frozen=True) avec tous les champs du contrat
  - [x] Implémenter `get_usage(db, *, user_id, feature_code, quota, ref_dt=None) → UsageState`
    - [x] `ref_dt = datetime.now(UTC)` si None
    - [x] Appeler `QuotaWindowResolver.compute_window(quota.period_unit, quota.period_value, quota.reset_mode, ref_dt)`
    - [x] `db.scalar(select(...).where(...).limit(1))` sans `with_for_update` (lecture pure)
    - [x] Si absent → `UsageState(used=0, remaining=quota_limit, exhausted=False, ...)`
  - [x] Implémenter `consume(db, *, user_id, feature_code, quota, amount=1, ref_dt=None) → UsageState`
    - [x] Lever `ValueError("amount must be >= 1")` si `amount <= 0`
    - [x] Calculer fenêtre via `QuotaWindowResolver`
    - [x] Appeler `_find_or_create_counter(db, ...)` (pattern atomique)
    - [x] Vérifier dépassement avant modification : `if counter.used_count + amount > quota.quota_limit → raise QuotaExhaustedError`
    - [x] `counter.used_count += amount` + `db.flush()`
    - [x] Retourner `UsageState` post-consommation avec tous les champs
  - [x] Implémenter `_find_or_create_counter` (voir patron dans Dev Notes)

- [x] **Enrichir `EntitlementService`** dans `backend/app/services/entitlement_service.py` (AC: 20-24)
  - [x] Importer `QuotaUsageService` depuis `app.services.quota_usage_service`
  - [x] S'assurer que `QuotaDefinition` et `FeatureEntitlement` sont importés depuis `entitlement_types`
  - [x] Dans la branche `access_mode=QUOTA` et `is_billing_active=True` :
    - [x] Calculer `usage_states = [QuotaUsageService.get_usage(db, user_id=user_id, feature_code=feature_code, quota=q) for q in quotas]`
    - [x] `quota_exhausted = any(s.exhausted for s in usage_states)`
    - [x] `final_access = not quota_exhausted`
  - [x] Dans toutes les autres branches (billing_inactive, no_plan, unlimited, disabled, legacy_fallback) : `usage_states=[]`, `quota_exhausted=False`
  - [x] Ne pas appeler `consume` dans `get_feature_entitlement`
  - [x] Ne pas modifier les guards `no_plan` / `billing_inactive` / `_legacy_fallback`

- [x] **Tests unitaires `QuotaWindowResolver`** dans `backend/app/tests/unit/test_quota_window_resolver.py` (AC: 1-8)
  - [x] `test_day_calendar_period_1` : ref_dt = 2026-03-15 14:30 UTC → window [2026-03-15 00:00, 2026-03-16 00:00)
  - [x] `test_week_calendar_period_1` : ref_dt = 2026-03-18 (mercredi) → window [2026-03-16 lundi, 2026-03-23 lundi)
  - [x] `test_month_calendar_period_1` : ref_dt = 2026-03-15 → window [2026-03-01, 2026-04-01)
  - [x] `test_year_calendar_period_1` : ref_dt = 2026-03-15 → window [2026-01-01, 2027-01-01)
  - [x] `test_lifetime` : window_start = 1970-01-01 UTC, window_end = None
  - [x] `test_day_calendar_period_2` : deux ref_dt dans le même slot de 2 jours → même window_start
  - [x] `test_week_calendar_period_2` : period_value=2 → fenêtre 14 jours, deux ref_dt dans le même slot → même window_start
  - [x] `test_month_calendar_period_3_q1` : ref_dt=2026-01-15 → window [2026-01-01, 2026-04-01) (trimestre Q1)
  - [x] `test_month_calendar_period_3_q2` : ref_dt=2026-05-10 → window [2026-04-01, 2026-07-01) (trimestre Q2)
  - [x] `test_month_calendar_period_3_invariant` : ref_dt=2026-03-31 et ref_dt=2026-01-01 → même window_start (même trimestre)
  - [x] `test_border_midnight` : ref_dt = 2026-03-15 23:59:59.999999 UTC → même fenêtre day que 2026-03-15 00:00 UTC
  - [x] `test_border_next_day` : ref_dt = 2026-03-16 00:00:00 UTC → fenêtre différente
  - [x] `test_end_of_month` : ref_dt = 2026-01-31 → window_end = 2026-02-01 (pas de crash)
  - [x] `test_ref_dt_paris_converted_to_utc` : ref_dt = 2026-03-15 01:00 Europe/Paris (= 2026-03-15 00:00 UTC) → window_start = 2026-03-15 00:00 UTC
  - [x] `test_naive_ref_dt_raises` : `ref_dt` sans tzinfo → `ValueError`
  - [x] `test_rolling_raises` : `reset_mode="rolling"` → `ValueError`
  - [x] `test_all_datetimes_utc` : toutes les datetimes retournées ont `tzinfo=timezone.utc`

- [x] **Tests unitaires `QuotaUsageService`** dans `backend/app/tests/unit/test_quota_usage_service.py` (AC: 9-19)
  - [x] Fixture : DB SQLite in-memory avec `Base.metadata.create_all(engine)`, insérer user (FK requis)
  - [x] `test_get_usage_counter_absent` : aucune ligne → `UsageState(used=0, remaining=limit, exhausted=False)`
  - [x] `test_get_usage_counter_present` : used_count=3, limit=5 → `used=3, remaining=2, exhausted=False`
  - [x] `test_get_usage_exhausted` : used_count=5, limit=5 → `exhausted=True, remaining=0`
  - [x] `test_get_usage_still_available` : used_count=4, limit=5 → `exhausted=False, remaining=1`
  - [x] `test_get_usage_multiple_quotas_same_feature` : quota_key "daily" et "monthly" sur même feature → `get_usage` résout chacun indépendamment
  - [x] `test_get_usage_no_side_effect` : deux appels consécutifs → même résultat, aucune ligne créée
  - [x] `test_consume_first_creates_counter` : aucune ligne → après consume, ligne créée avec `used_count=1`
  - [x] `test_consume_increments` : used_count=2 → après consume → used_count=3
  - [x] `test_consume_amount_3` : used_count=2, limit=5 → `consume(amount=3)` → `used_count=5, remaining=0, exhausted=True`
  - [x] `test_consume_exactly_limit` : used_count=4, limit=5 → `consume(amount=1)` réussit → `exhausted=True`
  - [x] `test_consume_exceeded_raises` : used_count=5, limit=5 → `consume()` lève `QuotaExhaustedError`, used_count inchangé
  - [x] `test_consume_amount_exceeds_raises` : used_count=3, limit=5 → `consume(amount=3)` lève `QuotaExhaustedError` (3+3 > 5)
  - [x] `test_consume_amount_zero_raises` : `consume(amount=0)` → `ValueError`
  - [x] `test_consume_amount_negative_raises` : `consume(amount=-1)` → `ValueError`
  - [x] `test_consume_atomicity_with_for_update` : vérifier que la requête SQLAlchemy émise par `_find_or_create_counter` contient `FOR UPDATE` (inspecter via `str(query)` ou mock `db.scalar`) — documenter que SQLite ne l'exécute pas réellement, les tests de concurrence réelle sont réservés à PostgreSQL
  - [x] Vérifier que `UsageState` retourné contient `period_unit`, `period_value`, `reset_mode`, `feature_code`

- [x] **Tests d'intégration `EntitlementService` enrichi** — étendre `test_entitlement_service.py` (AC: 20-25)
  - [x] `test_entitlement_quota_remaining_gt_0_final_access_true` : compteur used=2, limit=5 → `final_access=True`, `quota_exhausted=False`, `len(usage_states)==1`
  - [x] `test_entitlement_quota_exhausted_final_access_false` : compteur used=5, limit=5 → `final_access=False`, `quota_exhausted=True`, `reason="canonical_binding"`
  - [x] `test_entitlement_no_counter_final_access_true` : aucun compteur (used=0 implicite) → `final_access=True`
  - [x] `test_entitlement_billing_inactive_skips_quota` : `billing_status=past_due`, quota non épuisé → `final_access=False`, `reason="billing_inactive"`, `usage_states=[]` (quota non consulté)
  - [x] `test_entitlement_no_plan_skips_quota` : `no_plan` → `final_access=False`, `reason="no_plan"`, `usage_states=[]`
  - [x] `test_legacy_fallback_usage_states_empty` : `astrologer_chat` sans binding canonique → `usage_states=[]`, `quota_exhausted=False`, comportement 61-9 préservé

- [x] **Non-régression** (AC: 25)
  - [x] Lancer `pytest backend/app/tests/unit/test_entitlement_service.py` — 14 tests existants + nouveaux, tous verts
  - [x] Lancer `pytest backend/app/tests/unit/test_quota_service.py` — tous verts
  - [x] Lancer `pytest backend/app/tests/unit/test_b2b_usage_service.py` — tous verts
  - [x] Lancer `pytest backend/app/tests/unit/test_product_entitlements_models.py` — tous verts

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column`)
- **Session DB** : `Session` comme type d'annotation (`from sqlalchemy.orm import Session`)
- **Pattern de requête** : `db.scalar(select(Model).where(...).limit(1))`
- **Atomicité** : stratégie `SELECT FOR UPDATE` + `begin_nested()` + `IntegrityError` (voir patron ci-dessous) — conforme à `QuotaService._find_or_create_usage_row` lignes 117-149
- **Aucune migration** : `feature_usage_counters` existe depuis 61-7
- **Classe statique** : `@staticmethod`, PascalCase

### Localisation des fichiers

```
backend/app/services/entitlement_types.py       ← NOUVEAU — QuotaDefinition + FeatureEntitlement
backend/app/services/quota_window_resolver.py   ← NOUVEAU — QuotaWindowResolver + QuotaWindow
backend/app/services/quota_usage_service.py     ← NOUVEAU — QuotaUsageService + UsageState + QuotaExhaustedError
backend/app/services/entitlement_service.py     ← MODIFIÉ — imports + logique quota réel
backend/app/tests/unit/test_quota_window_resolver.py   ← NOUVEAU
backend/app/tests/unit/test_quota_usage_service.py     ← NOUVEAU
```

### Résolution du cycle d'import — `entitlement_types.py` obligatoire

`quota_usage_service.py` a besoin de `QuotaDefinition`. `entitlement_service.py` aura besoin de `QuotaUsageService`. Cycle direct si `QuotaDefinition` reste dans `entitlement_service.py`.

**Solution obligatoire** : créer `backend/app/services/entitlement_types.py` contenant uniquement les dataclasses `QuotaDefinition`, `FeatureEntitlement`, `UsageState` (types purs, zéro import service). Tous les services importent depuis ce module.

```python
# entitlement_service.py
from app.services.entitlement_types import QuotaDefinition, FeatureEntitlement
from app.services.quota_usage_service import QuotaUsageService

# quota_usage_service.py
from app.services.entitlement_types import QuotaDefinition
from app.services.quota_window_resolver import QuotaWindowResolver
```

> Ne **pas** utiliser `TYPE_CHECKING` pour contourner le cycle — cela masque le problème et fragilise les imports runtime.

### Règle d'alignement des slots (period_value > 1)

**Principe fondamental** : pour `period_value > 1`, on calcule un numéro de slot global depuis une époque fixe, puis on dérive `window_start` et `window_end`. La fenêtre n'est jamais relative à `ref_dt`.

```python
# day/calendar
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
days_since_epoch = (ref_dt.date() - UNIX_EPOCH.date()).days
slot = days_since_epoch // period_value
window_start = UNIX_EPOCH + timedelta(days=slot * period_value)
window_end = window_start + timedelta(days=period_value)

# week/calendar
WEEK_ANCHOR = datetime(1969, 12, 29, tzinfo=timezone.utc)  # lundi précédant l'époque
weeks_since_anchor = (ref_dt.date() - WEEK_ANCHOR.date()).days // 7
slot = weeks_since_anchor // period_value
window_start = WEEK_ANCHOR + timedelta(weeks=slot * period_value)
window_end = window_start + timedelta(weeks=period_value)

# month/calendar
total_months = ref_dt.year * 12 + (ref_dt.month - 1)
slot = total_months // period_value
start_month_total = slot * period_value
start_year, start_month_idx = divmod(start_month_total, 12)
window_start = datetime(start_year, start_month_idx + 1, 1, tzinfo=timezone.utc)
end_month_total = start_month_total + period_value
end_year, end_month_idx = divmod(end_month_total, 12)
window_end = datetime(end_year, end_month_idx + 1, 1, tzinfo=timezone.utc)

# year/calendar
slot = ref_dt.year // period_value
window_start = datetime(slot * period_value, 1, 1, tzinfo=timezone.utc)
window_end = datetime((slot + 1) * period_value, 1, 1, tzinfo=timezone.utc)
```

> **Vérification trimestre** : pour `period_value=3`, `ref_dt=2026-01-01` → total_months=24243, slot=8081, start_month_total=24243, start_year=2026, start_month=1 → `window_start=2026-01-01`. `ref_dt=2026-03-31` → total_months=24245, slot=8081 (même) → même `window_start`. `ref_dt=2026-04-01` → total_months=24246, slot=8082 → `window_start=2026-04-01`. ✓

### Pattern `_find_or_create_counter` — atomicité

```python
@staticmethod
def _find_or_create_counter(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    quota: QuotaDefinition,
    window: QuotaWindow,
) -> FeatureUsageCounterModel:
    query = (
        select(FeatureUsageCounterModel)
        .where(
            FeatureUsageCounterModel.user_id == user_id,
            FeatureUsageCounterModel.feature_code == feature_code,
            FeatureUsageCounterModel.quota_key == quota.quota_key,
            FeatureUsageCounterModel.period_unit == quota.period_unit,
            FeatureUsageCounterModel.period_value == quota.period_value,
            FeatureUsageCounterModel.reset_mode == quota.reset_mode,
            FeatureUsageCounterModel.window_start == window.window_start,
        )
        .with_for_update()  # NB: SQLite ignore cette clause, PostgreSQL l'applique
        .limit(1)
    )
    counter = db.scalar(query)
    if counter is not None:
        return counter
    counter = FeatureUsageCounterModel(
        user_id=user_id,
        feature_code=feature_code,
        quota_key=quota.quota_key,
        period_unit=quota.period_unit,
        period_value=quota.period_value,
        reset_mode=quota.reset_mode,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=0,
    )
    try:
        with db.begin_nested():
            db.add(counter)
            db.flush()
    except IntegrityError:
        counter = db.scalar(query)
        if counter is None:
            raise
    return counter
```

### Intégration dans `EntitlementService`

```python
# Dans la branche binding.access_mode == AccessMode.QUOTA, après résolution de quotas
if binding.access_mode == AccessMode.QUOTA and quota_models and is_billing_active:
    usage_states = [
        QuotaUsageService.get_usage(db, user_id=user_id, feature_code=feature_code, quota=q)
        for q in quotas
    ]
    quota_exhausted = any(s.exhausted for s in usage_states)
    final_access = not quota_exhausted
else:
    usage_states = []
    quota_exhausted = False
    final_access = is_billing_active and is_enabled_by_plan

return FeatureEntitlement(
    ...,
    usage_states=usage_states,
    quota_exhausted=quota_exhausted,
    final_access=final_access,
    reason="billing_inactive" if not is_billing_active else "canonical_binding",
)
```

> Ne **jamais** appeler `consume` dans `get_feature_entitlement` — c'est une lecture, pas une consommation.

### Valeurs par défaut pour les cas non-quota

Dans tous les cas où `usage_states` n'est pas pertinent (no_plan, billing_inactive, unlimited, disabled, legacy_fallback), utiliser :
```python
usage_states=[]
quota_exhausted=False
```

### Cas limites à anticiper

| Cas | Comportement attendu |
|-----|---------------------|
| `ref_dt` naïf (sans tzinfo) | `ValueError("ref_dt must be timezone-aware")` |
| `ref_dt` en timezone non-UTC | Conversion automatique en UTC avant calcul |
| `reset_mode=rolling` | `ValueError("rolling windows not supported in this version")` |
| `amount <= 0` dans `consume` | `ValueError("amount must be >= 1")` |
| `used_count + amount == quota_limit` | Autorisé — `exhausted=True`, `remaining=0` |
| `used_count + amount > quota_limit` | `QuotaExhaustedError` |
| Fin de mois (Jan 31 + 1 mois) | window_end = 2026-02-01 — l'algorithme divmod gère correctement |
| Binding `access_mode=quota` sans quota en DB | Cas géré en 61-9 (log warning, `final_access=False`) — inchangé |
| Époque `lifetime` | 1970-01-01 UTC fixe, indépendante de la date de souscription |

### Éviter les erreurs de régression

- **`QuotaService` ne doit PAS être modifié** — lit encore `UserDailyQuotaUsageModel` directement.
- **`B2BUsageService` ne doit PAS être modifié**.
- **Les 14 tests existants de `test_entitlement_service.py`** continuent de passer. Les champs `usage_states` et `quota_exhausted` ont des valeurs par défaut (`[]` et `False`) compatibles. Les tests de binding quota sans compteur (`used=0` implicite) retournent `final_access=True` car `remaining=quota_limit > 0`.
- **Créer `entitlement_types.py` avant tout le reste** pour éviter les imports cassés en cours de dev.

### Pattern de test SQLite in-memory

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infra.db.base import Base

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
# quota_usage_service n'a pas besoin de mocker BillingService
# Les tests opèrent directement sur FeatureUsageCounterModel

# Note : SELECT FOR UPDATE est ignoré par SQLite (traduit en SELECT).
# Les tests de concurrence réelle sont réservés à PostgreSQL (intégration).
```

### Références

- [backend/app/services/quota_service.py](backend/app/services/quota_service.py) lignes 117-149 — patron `_find_or_create_usage_row` à reproduire
- [backend/app/services/entitlement_service.py](backend/app/services/entitlement_service.py) — à enrichir
- [backend/app/infra/db/models/product_entitlements.py](backend/app/infra/db/models/product_entitlements.py) — `FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode`
- [backend/app/tests/unit/test_entitlement_service.py](backend/app/tests/unit/test_entitlement_service.py) — à étendre
- [backend/app/tests/unit/test_quota_service.py](backend/app/tests/unit/test_quota_service.py) — pattern de test atomique
- [docs/architecture/product-entitlements-model.md](docs/architecture/product-entitlements-model.md) — contraintes DB

### Project Structure Notes

- `backend/app/services/` — même niveau que les services existants
- Conventions : `@staticmethod`, PascalCase, `frozen=True` pour les dataclasses de valeur

---

## Hors périmètre explicite

Cette story **ne doit pas** :
- Migrer `QuotaService` ou `B2BUsageService` vers `QuotaUsageService` (→ 61-11)
- Brancher `astrologer_chat` via le chemin `legacy_fallback` sur `feature_usage_counters` (→ 61-11)
- Créer des endpoints API publics `/entitlements/*` ou `/quotas/*`
- Implémenter les fenêtres `rolling`
- Créer de migration Alembic
- Modifier `billing_service.py`, `quota_service.py` ou `b2b_usage_service.py`
- Créer un job de reset des compteurs

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Code review effectué le 2026-03-25 (claude-sonnet-4-6).
- 10 tests manquants ajoutés (marqués [x] mais absents des fichiers) : 3 dans `test_quota_window_resolver.py`, 6 dans `test_quota_usage_service.py`, 1 dans `test_entitlement_service.py`.
- Fixture `db_session` enrichie avec insertion d'un `UserModel` pour respecter la contrainte FK `user_id → users.id`.
- `Optional[datetime]` remplacé par `datetime | None` dans `quota_window_resolver.py` et `quota_usage_service.py` (Python 3.13).
- Suppression des imports `from typing import Optional` devenus inutiles.
- Suite de tests : 53 tests passent (vs 43 avant review).

### File List

- backend/app/services/entitlement_types.py
- backend/app/services/quota_window_resolver.py
- backend/app/services/quota_usage_service.py
- backend/app/services/entitlement_service.py
- backend/app/tests/unit/test_quota_window_resolver.py
- backend/app/tests/unit/test_quota_usage_service.py
- backend/app/tests/unit/test_entitlement_service.py

Status: done

## Story

En tant que système backend,
je veux un `QuotaWindowResolver` qui calcule la fenêtre temporelle active pour un quota, et un `QuotaUsageService` qui lit et consomme atomiquement les lignes `feature_usage_counters`,
afin de rendre effectifs les quotas canoniques définis dans `plan_feature_quotas` — aujourd'hui théoriques — et de brancher ce moteur dans `EntitlementService` pour que `final_access` et l'état de consommation réelle soient exposés au caller.

---

## Contexte métier et enjeu architectural

### Situation après 61-9

- `EntitlementService` calcule correctement les droits canoniques et retourne `FeatureEntitlement` avec `quotas: list[QuotaDefinition]` et `final_access` basé sur le plan et le billing.
- `FeatureUsageCounterModel` (`feature_usage_counters`) existe dans le schéma depuis 61-7 mais **aucun service ne lit ni n'écrit dedans**.
- Résultat : un utilisateur avec `access_mode=quota` et `final_access=True` peut consommer infiniment — le quota est structurel mais pas appliqué.

### Ce que cette story introduit

1. **`QuotaWindowResolver`** : calcul pur (sans I/O) de la fenêtre `(window_start, window_end)` pour un triplet `(period_unit, period_value, reset_mode)` à un instant de référence.
2. **`QuotaUsageService`** : lecture idempotente + consommation atomique de `feature_usage_counters`.
3. **`EntitlementService` enrichi** : `get_feature_entitlement` vérifie les quotas réels pour les bindings `access_mode=quota` — `final_access` et `usage_states` reflètent la consommation réelle.
4. **`entitlement_types.py`** : module tiers obligatoire portant `QuotaDefinition` et `FeatureEntitlement`, pour éviter le cycle d'import entre `entitlement_service.py` et `quota_usage_service.py`.

### Ce que cette story ne fait PAS

- Migrer `QuotaService` ou `B2BUsageService` vers le nouveau moteur (→ 61-11).
- Exposer des endpoints API publics sur les quotas.
- Supporter les fenêtres `rolling` (différé explicitement — uniquement `calendar` et `lifetime`).
- Modifier le schéma DB ou créer une migration Alembic (tables déjà présentes).
- Créer un scheduler ou job de reset des compteurs.

> **Dette explicitement assumée** : 61-10 n'applique les compteurs réels qu'aux chemins canoniques `access_mode=quota`. Les quotas issus du fallback legacy (`astrologer_chat` via `daily_message_limit`) restent purement déclaratifs jusqu'à la migration métier prévue en 61-11+. Un utilisateur sur le chemin legacy peut donc toujours consommer au-delà du quota déclaré pendant cette phase transitoire.

---

## Contrats de sortie

### `entitlement_types.py` (module tiers — **obligatoire**)

```python
# backend/app/services/entitlement_types.py
# Source unique de QuotaDefinition et FeatureEntitlement.
# Importé par entitlement_service.py ET quota_usage_service.py.
# NE PAS importer d'autres services ici → zéro dépendance cyclique.

@dataclass(frozen=True)
class QuotaDefinition:
    quota_key: str
    quota_limit: int
    period_unit: str   # "day" | "week" | "month" | "year" | "lifetime"
    period_value: int
    reset_mode: str    # "calendar" | "lifetime"

@dataclass
class FeatureEntitlement:
    plan_code: str
    billing_status: str
    is_enabled_by_plan: bool
    access_mode: str
    variant_code: str | None
    quotas: list[QuotaDefinition]          # quotas théoriques du plan
    usage_states: list[UsageState]         # état réel de consommation (vide si non applicable)
    quota_exhausted: bool                  # True si au moins un quota est épuisé
    final_access: bool
    reason: str
```

### `QuotaWindow`

```python
@dataclass(frozen=True)
class QuotaWindow:
    window_start: datetime   # timezone-aware UTC
    window_end: datetime | None  # None uniquement si reset_mode="lifetime"
```

### `UsageState`

```python
@dataclass(frozen=True)
class UsageState:
    feature_code: str
    quota_key: str
    quota_limit: int
    used: int
    remaining: int
    exhausted: bool          # used >= quota_limit
    period_unit: str
    period_value: int
    reset_mode: str
    window_start: datetime
    window_end: datetime | None
```

### `QuotaExhaustedError`

```python
class QuotaExhaustedError(Exception):
    def __init__(self, quota_key: str, used: int, limit: int, feature_code: str) -> None: ...
    quota_key: str
    used: int
    limit: int
    feature_code: str
```

---

## Acceptance Criteria

### QuotaWindowResolver

1. **`QuotaWindowResolver.compute_window(period_unit, period_value, reset_mode, ref_dt)`** retourne un `QuotaWindow` UTC-aware pour tous les cas : `day`, `week`, `month`, `year` (reset_mode=`calendar`), `lifetime`, et `period_value > 1`. (AC: 1)

2. **Fenêtres calendar alignées** (`period_value=1`) : `day/calendar` → `window_start` = minuit UTC du jour ; `week/calendar` → lundi UTC de la semaine ; `month/calendar` → 1er du mois 00:00 UTC ; `year/calendar` → 1er janvier 00:00 UTC. (AC: 2)

3. **Règle d'alignement global pour `period_value > 1`** : pour `period_value > 1`, la fenêtre n'est **pas** calculée comme `ref_dt floored + N unités` (glissant), mais comme un **slot calendaire aligné globalement** depuis une époque fixe. Toutes les instances d'un même slot partagent la même `window_start`, quel que soit le `ref_dt` dans ce slot. Règles d'époque par unité : `day` → époque Unix (1970-01-01) ; `week` → lundi 1969-12-29 (lundi précédant l'époque) ; `month` → mois 0 de l'an 0 (`total_months // N`) ; `year` → an 0 (`year // N`). (AC: 3)

4. **Invariant trimestre** : pour `month/calendar/period_value=3`, les fenêtres sont strictement Jan–Mar, Apr–Jun, Jul–Sep, Oct–Déc. Tout `ref_dt` dans un de ces trimestres produit la même `window_start`. (AC: 4)

5. **`lifetime`** : `window_start = datetime(1970, 1, 1, tzinfo=UTC)`, `window_end = None`. Il s'agit d'une **époque fixe canonique**, pas de la date de souscription de l'utilisateur — garantit une clé de fenêtre stable pour tous les utilisateurs. (AC: 5)

6. **Bord de période** : `ref_dt = J 23:59:59.999999 UTC` → même fenêtre `day` que `J 00:00:00 UTC`. `ref_dt = J+1 00:00:00 UTC` → fenêtre différente. (AC: 6)

7. **Conversion UTC obligatoire** : `compute_window` accepte tout `ref_dt` timezone-aware (ex: `Europe/Paris`), le convertit en UTC avant calcul. Lève `ValueError("ref_dt must be timezone-aware")` si `ref_dt` est naïf (sans tzinfo). (AC: 7)

8. **`reset_mode=rolling` refusé** : lève `ValueError("rolling windows not supported in this version")`. (AC: 8)

### QuotaUsageService

9. **`get_usage(db, *, user_id, feature_code, quota, ref_dt=None)`** : retourne `UsageState` avec `used=0` si aucun compteur existe pour la fenêtre active. Aucun effet de bord — n'insère rien. (AC: 9)

10. **Lecture correcte** : si un compteur existe pour la fenêtre active, `used` reflète `FeatureUsageCounterModel.used_count`. `remaining = max(0, quota_limit - used)`. `exhausted = used >= quota_limit`. (AC: 10)

11. **Plusieurs quotas sur une même feature** : `get_usage` traite un seul `QuotaDefinition` par appel. L'appelant itère sur la liste de quotas. (AC: 11)

12. **Idempotence lecture** : deux appels consécutifs à `get_usage` avec les mêmes arguments retournent le même résultat sans créer d'enregistrement. (AC: 12)

13. **`consume(db, *, user_id, feature_code, quota, amount=1, ref_dt=None)`** : crée le compteur s'il n'existe pas, incrémente atomiquement. Retourne `UsageState` post-consommation. (AC: 13)

14. **Première consommation crée le compteur** : une ligne `feature_usage_counters` est insérée avec `used_count=amount` et les bons `window_start`/`window_end`/`period_unit`/`period_value`/`reset_mode`. (AC: 14)

15. **Consommation successive incrémente** : appels successifs à `consume` accumulent correctement `used_count`. (AC: 15)

16. **Dépassement refusé** : si `used_count + amount > quota_limit`, lever `QuotaExhaustedError` sans modifier le compteur. `used_count + amount == quota_limit` est autorisé — résultat `remaining=0`, `exhausted=True`. (AC: 16)

17. **`amount > 1` supporté** : `consume(..., amount=3)` vérifie `used_count + 3 <= quota_limit` avant d'incrémenter de 3. (AC: 17)

18. **`amount <= 0` refusé** : `consume(..., amount=0)` ou `amount=-1` lève `ValueError("amount must be >= 1")`. (AC: 18)

19. **Atomicité** : `consume` utilise une stratégie transactionnelle garantissant l'atomicité du find-or-create et la sécurité en concurrence, conforme au pattern `SELECT FOR UPDATE` + `begin_nested()` + gestion `IntegrityError` de `QuotaService._find_or_create_usage_row`. (AC: 19)

### EntitlementService enrichi

20. **`FeatureEntitlement` expose `usage_states` et `quota_exhausted`** : pour un binding canonique `access_mode=quota` avec billing actif, `usage_states` contient un `UsageState` par quota résolu. `quota_exhausted = any(s.exhausted for s in usage_states)`. (AC: 20)

21. **`final_access` reflète la consommation réelle** : `final_access=True` uniquement si billing actif ET `is_enabled_by_plan=True` ET tous les quotas ont `remaining > 0`. Si au moins un quota est épuisé, `final_access=False`. (AC: 21)

22. **`reason` encode la provenance, pas le verdict** : `reason` reste `"canonical_binding"` même si le quota est épuisé. Le verdict exhaustion est exposé via `quota_exhausted` et `final_access`. (AC: 22)

23. **Guards prioritaires inchangés** : `no_plan` et `billing_inactive` restent prioritaires et court-circuitent avant toute vérification de quota. Pour ces cas, `usage_states=[]` et `quota_exhausted=False`. (AC: 23)

24. **Fallback legacy non connecté** : le chemin `legacy_fallback` pour `astrologer_chat` n'est pas connecté au nouveau moteur — `usage_states=[]`, `quota_exhausted=False`, comportement 61-9 inchangé. (AC: 24)

25. **Non-régression** : `test_entitlement_service.py`, `test_quota_service.py`, `test_b2b_usage_service.py`, `test_product_entitlements_models.py` passent sans modification. Les 14 tests existants de `test_entitlement_service.py` continuent de valider le contrat 61-9 — les champs ajoutés (`usage_states`, `quota_exhausted`) ont des valeurs par défaut cohérentes. (AC: 25)

---

## Tasks / Subtasks

- [x]**Créer `entitlement_types.py`** — module tiers, **première étape obligatoire** (AC: 20, 21, 25)
  - [x]Créer `backend/app/services/entitlement_types.py`
  - [x]Y déplacer `QuotaDefinition` (dataclass frozen=True) depuis `entitlement_service.py`
  - [x]Y déplacer `FeatureEntitlement` (dataclass mutable) depuis `entitlement_service.py`
  - [x]Ajouter les champs `usage_states: list[UsageState]` et `quota_exhausted: bool` à `FeatureEntitlement`
  - [x]Mettre à jour `entitlement_service.py` pour importer depuis `entitlement_types`
  - [x]Vérifier que tous les tests existants passent après refactoring des imports

- [x]**Créer `QuotaWindowResolver`** dans `backend/app/services/quota_window_resolver.py` (AC: 1-8)
  - [x]Implémenter `compute_window(period_unit, period_value, reset_mode, ref_dt) → QuotaWindow`
  - [x]Normaliser `ref_dt` en UTC en début de méthode : `ref_dt = ref_dt.astimezone(timezone.utc)` ; lever `ValueError` si naïf
  - [x]Lever `ValueError` si `reset_mode=rolling`
  - [x]Cas `lifetime` : `window_start = datetime(1970, 1, 1, tzinfo=UTC)`, `window_end = None`
  - [x]Cas `calendar/day` : slot = `days_since_epoch // period_value` depuis UNIX_EPOCH ; `window_end = window_start + timedelta(days=period_value)`
  - [x]Cas `calendar/week` : slot depuis WEEK_ANCHOR (1969-12-29) ; `window_end = window_start + timedelta(weeks=period_value)`
  - [x]Cas `calendar/month` : `slot = (year*12 + month - 1) // period_value` ; utiliser l'algorithme divmod pour window_start et window_end
  - [x]Cas `calendar/year` : `slot = year // period_value` ; `window_start = datetime(slot*N, 1, 1, UTC)`, `window_end = datetime((slot+1)*N, 1, 1, UTC)`
  - [x]Vérifier l'invariant trimestre : `period_unit=month, period_value=3` → slots Jan/Apr/Jul/Oct
  - [x]Toutes les datetimes retournées ont `tzinfo=timezone.utc`

- [x]**Créer `QuotaUsageService`** dans `backend/app/services/quota_usage_service.py` (AC: 9-19)
  - [x]Importer `QuotaDefinition` depuis `app.services.entitlement_types` (pas depuis `entitlement_service`)
  - [x]Définir `QuotaExhaustedError` avec attributs `quota_key`, `used`, `limit`, `feature_code`
  - [x]Définir `UsageState` dataclass (frozen=True) avec tous les champs du contrat
  - [x]Implémenter `get_usage(db, *, user_id, feature_code, quota, ref_dt=None) → UsageState`
    - [x]`ref_dt = datetime.now(UTC)` si None
    - [x]Appeler `QuotaWindowResolver.compute_window(quota.period_unit, quota.period_value, quota.reset_mode, ref_dt)`
    - [x]`db.scalar(select(...).where(...).limit(1))` sans `with_for_update` (lecture pure)
    - [x]Si absent → `UsageState(used=0, remaining=quota_limit, exhausted=False, ...)`
  - [x]Implémenter `consume(db, *, user_id, feature_code, quota, amount=1, ref_dt=None) → UsageState`
    - [x]Lever `ValueError("amount must be >= 1")` si `amount <= 0`
    - [x]Calculer fenêtre via `QuotaWindowResolver`
    - [x]Appeler `_find_or_create_counter(db, ...)` (pattern atomique)
    - [x]Vérifier dépassement avant modification : `if counter.used_count + amount > quota.quota_limit → raise QuotaExhaustedError`
    - [x]`counter.used_count += amount` + `db.flush()`
    - [x]Retourner `UsageState` post-consommation avec tous les champs
  - [x]Implémenter `_find_or_create_counter` (voir patron dans Dev Notes)

- [x]**Enrichir `EntitlementService`** dans `backend/app/services/entitlement_service.py` (AC: 20-24)
  - [x]Importer `QuotaUsageService` depuis `app.services.quota_usage_service`
  - [x]S'assurer que `QuotaDefinition` et `FeatureEntitlement` sont importés depuis `entitlement_types`
  - [x]Dans la branche `access_mode=QUOTA` et `is_billing_active=True` :
    - [x]Calculer `usage_states = [QuotaUsageService.get_usage(db, user_id=user_id, feature_code=feature_code, quota=q) for q in quotas]`
    - [x]`quota_exhausted = any(s.exhausted for s in usage_states)`
    - [x]`final_access = not quota_exhausted`
  - [x]Dans toutes les autres branches (billing_inactive, no_plan, unlimited, disabled, legacy_fallback) : `usage_states=[]`, `quota_exhausted=False`
  - [x]Ne pas appeler `consume` dans `get_feature_entitlement`
  - [x]Ne pas modifier les guards `no_plan` / `billing_inactive` / `_legacy_fallback`

- [x]**Tests unitaires `QuotaWindowResolver`** dans `backend/app/tests/unit/test_quota_window_resolver.py` (AC: 1-8)
  - [x]`test_day_calendar_period_1` : ref_dt = 2026-03-15 14:30 UTC → window [2026-03-15 00:00, 2026-03-16 00:00)
  - [x]`test_week_calendar_period_1` : ref_dt = 2026-03-18 (mercredi) → window [2026-03-16 lundi, 2026-03-23 lundi)
  - [x]`test_month_calendar_period_1` : ref_dt = 2026-03-15 → window [2026-03-01, 2026-04-01)
  - [x]`test_year_calendar_period_1` : ref_dt = 2026-03-15 → window [2026-01-01, 2027-01-01)
  - [x]`test_lifetime` : window_start = 1970-01-01 UTC, window_end = None
  - [x]`test_day_calendar_period_2` : deux ref_dt dans le même slot de 2 jours → même window_start
  - [x]`test_week_calendar_period_2` : period_value=2 → fenêtre 14 jours, deux ref_dt dans le même slot → même window_start
  - [x]`test_month_calendar_period_3_q1` : ref_dt=2026-01-15 → window [2026-01-01, 2026-04-01) (trimestre Q1)
  - [x]`test_month_calendar_period_3_q2` : ref_dt=2026-05-10 → window [2026-04-01, 2026-07-01) (trimestre Q2)
  - [x]`test_month_calendar_period_3_invariant` : ref_dt=2026-03-31 et ref_dt=2026-01-01 → même window_start (même trimestre)
  - [x]`test_border_midnight` : ref_dt = 2026-03-15 23:59:59.999999 UTC → même fenêtre day que 2026-03-15 00:00 UTC
  - [x]`test_border_next_day` : ref_dt = 2026-03-16 00:00:00 UTC → fenêtre différente
  - [x]`test_end_of_month` : ref_dt = 2026-01-31 → window_end = 2026-02-01 (pas de crash)
  - [x]`test_ref_dt_paris_converted_to_utc` : ref_dt = 2026-03-15 01:00 Europe/Paris (= 2026-03-15 00:00 UTC) → window_start = 2026-03-15 00:00 UTC
  - [x]`test_naive_ref_dt_raises` : `ref_dt` sans tzinfo → `ValueError`
  - [x]`test_rolling_raises` : `reset_mode="rolling"` → `ValueError`
  - [x]`test_all_datetimes_utc` : toutes les datetimes retournées ont `tzinfo=timezone.utc`

- [x]**Tests unitaires `QuotaUsageService`** dans `backend/app/tests/unit/test_quota_usage_service.py` (AC: 9-19)
  - [x]Fixture : DB SQLite in-memory avec `Base.metadata.create_all(engine)`, insérer user (FK requis)
  - [x]`test_get_usage_counter_absent` : aucune ligne → `UsageState(used=0, remaining=limit, exhausted=False)`
  - [x]`test_get_usage_counter_present` : used_count=3, limit=5 → `used=3, remaining=2, exhausted=False`
  - [x]`test_get_usage_exhausted` : used_count=5, limit=5 → `exhausted=True, remaining=0`
  - [x]`test_get_usage_still_available` : used_count=4, limit=5 → `exhausted=False, remaining=1`
  - [x]`test_get_usage_multiple_quotas_same_feature` : quota_key "daily" et "monthly" sur même feature → `get_usage` résout chacun indépendamment
  - [x]`test_get_usage_no_side_effect` : deux appels consécutifs → même résultat, aucune ligne créée
  - [x]`test_consume_first_creates_counter` : aucune ligne → après consume, ligne créée avec `used_count=1`
  - [x]`test_consume_increments` : used_count=2 → après consume → used_count=3
  - [x]`test_consume_amount_3` : used_count=2, limit=5 → `consume(amount=3)` → `used_count=5, remaining=0, exhausted=True`
  - [x]`test_consume_exactly_limit` : used_count=4, limit=5 → `consume(amount=1)` réussit → `exhausted=True`
  - [x]`test_consume_exceeded_raises` : used_count=5, limit=5 → `consume()` lève `QuotaExhaustedError`, used_count inchangé
  - [x]`test_consume_amount_exceeds_raises` : used_count=3, limit=5 → `consume(amount=3)` lève `QuotaExhaustedError` (3+3 > 5)
  - [x]`test_consume_amount_zero_raises` : `consume(amount=0)` → `ValueError`
  - [x]`test_consume_amount_negative_raises` : `consume(amount=-1)` → `ValueError`
  - [x]`test_consume_atomicity_with_for_update` : vérifier que la requête SQLAlchemy émise par `_find_or_create_counter` contient `FOR UPDATE` (inspecter via `str(query)` ou mock `db.scalar`) — documenter que SQLite ne l'exécute pas réellement, les tests de concurrence réelle sont réservés à PostgreSQL
  - [x]Vérifier que `UsageState` retourné contient `period_unit`, `period_value`, `reset_mode`, `feature_code`

- [x]**Tests d'intégration `EntitlementService` enrichi** — étendre `test_entitlement_service.py` (AC: 20-25)
  - [x]`test_entitlement_quota_remaining_gt_0_final_access_true` : compteur used=2, limit=5 → `final_access=True`, `quota_exhausted=False`, `len(usage_states)==1`
  - [x]`test_entitlement_quota_exhausted_final_access_false` : compteur used=5, limit=5 → `final_access=False`, `quota_exhausted=True`, `reason="canonical_binding"`
  - [x]`test_entitlement_no_counter_final_access_true` : aucun compteur (used=0 implicite) → `final_access=True`
  - [x]`test_entitlement_billing_inactive_skips_quota` : `billing_status=past_due`, quota non épuisé → `final_access=False`, `reason="billing_inactive"`, `usage_states=[]` (quota non consulté)
  - [x]`test_entitlement_no_plan_skips_quota` : `no_plan` → `final_access=False`, `reason="no_plan"`, `usage_states=[]`
  - [x]`test_legacy_fallback_usage_states_empty` : `astrologer_chat` sans binding canonique → `usage_states=[]`, `quota_exhausted=False`, comportement 61-9 préservé

- [x]**Non-régression** (AC: 25)
  - [x]Lancer `pytest backend/app/tests/unit/test_entitlement_service.py` — 14 tests existants + nouveaux, tous verts
  - [x]Lancer `pytest backend/app/tests/unit/test_quota_service.py` — tous verts
  - [x]Lancer `pytest backend/app/tests/unit/test_b2b_usage_service.py` — tous verts
  - [x]Lancer `pytest backend/app/tests/unit/test_product_entitlements_models.py` — tous verts

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column`)
- **Session DB** : `Session` comme type d'annotation (`from sqlalchemy.orm import Session`)
- **Pattern de requête** : `db.scalar(select(Model).where(...).limit(1))`
- **Atomicité** : stratégie `SELECT FOR UPDATE` + `begin_nested()` + `IntegrityError` (voir patron ci-dessous) — conforme à `QuotaService._find_or_create_usage_row` lignes 117-149
- **Aucune migration** : `feature_usage_counters` existe depuis 61-7
- **Classe statique** : `@staticmethod`, PascalCase

### Localisation des fichiers

```
backend/app/services/entitlement_types.py       ← NOUVEAU — QuotaDefinition + FeatureEntitlement
backend/app/services/quota_window_resolver.py   ← NOUVEAU — QuotaWindowResolver + QuotaWindow
backend/app/services/quota_usage_service.py     ← NOUVEAU — QuotaUsageService + UsageState + QuotaExhaustedError
backend/app/services/entitlement_service.py     ← MODIFIÉ — imports + logique quota réel
backend/app/tests/unit/test_quota_window_resolver.py   ← NOUVEAU
backend/app/tests/unit/test_quota_usage_service.py     ← NOUVEAU
```

### Résolution du cycle d'import — `entitlement_types.py` obligatoire

`quota_usage_service.py` a besoin de `QuotaDefinition`. `entitlement_service.py` aura besoin de `QuotaUsageService`. Cycle direct si `QuotaDefinition` reste dans `entitlement_service.py`.

**Solution obligatoire** : créer `backend/app/services/entitlement_types.py` contenant uniquement les dataclasses `QuotaDefinition`, `FeatureEntitlement`, `UsageState` (types purs, zéro import service). Tous les services importent depuis ce module.

```python
# entitlement_service.py
from app.services.entitlement_types import QuotaDefinition, FeatureEntitlement
from app.services.quota_usage_service import QuotaUsageService

# quota_usage_service.py
from app.services.entitlement_types import QuotaDefinition
from app.services.quota_window_resolver import QuotaWindowResolver
```

> Ne **pas** utiliser `TYPE_CHECKING` pour contourner le cycle — cela masque le problème et fragilise les imports runtime.

### Règle d'alignement des slots (period_value > 1)

**Principe fondamental** : pour `period_value > 1`, on calcule un numéro de slot global depuis une époque fixe, puis on dérive `window_start` et `window_end`. La fenêtre n'est jamais relative à `ref_dt`.

```python
# day/calendar
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
days_since_epoch = (ref_dt.date() - UNIX_EPOCH.date()).days
slot = days_since_epoch // period_value
window_start = UNIX_EPOCH + timedelta(days=slot * period_value)
window_end = window_start + timedelta(days=period_value)

# week/calendar
WEEK_ANCHOR = datetime(1969, 12, 29, tzinfo=timezone.utc)  # lundi précédant l'époque
weeks_since_anchor = (ref_dt.date() - WEEK_ANCHOR.date()).days // 7
slot = weeks_since_anchor // period_value
window_start = WEEK_ANCHOR + timedelta(weeks=slot * period_value)
window_end = window_start + timedelta(weeks=period_value)

# month/calendar
total_months = ref_dt.year * 12 + (ref_dt.month - 1)
slot = total_months // period_value
start_month_total = slot * period_value
start_year, start_month_idx = divmod(start_month_total, 12)
window_start = datetime(start_year, start_month_idx + 1, 1, tzinfo=timezone.utc)
end_month_total = start_month_total + period_value
end_year, end_month_idx = divmod(end_month_total, 12)
window_end = datetime(end_year, end_month_idx + 1, 1, tzinfo=timezone.utc)

# year/calendar
slot = ref_dt.year // period_value
window_start = datetime(slot * period_value, 1, 1, tzinfo=timezone.utc)
window_end = datetime((slot + 1) * period_value, 1, 1, tzinfo=timezone.utc)
```

> **Vérification trimestre** : pour `period_value=3`, `ref_dt=2026-01-01` → total_months=24243, slot=8081, start_month_total=24243, start_year=2026, start_month=1 → `window_start=2026-01-01`. `ref_dt=2026-03-31` → total_months=24245, slot=8081 (même) → même `window_start`. `ref_dt=2026-04-01` → total_months=24246, slot=8082 → `window_start=2026-04-01`. ✓

### Pattern `_find_or_create_counter` — atomicité

```python
@staticmethod
def _find_or_create_counter(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    quota: QuotaDefinition,
    window: QuotaWindow,
) -> FeatureUsageCounterModel:
    query = (
        select(FeatureUsageCounterModel)
        .where(
            FeatureUsageCounterModel.user_id == user_id,
            FeatureUsageCounterModel.feature_code == feature_code,
            FeatureUsageCounterModel.quota_key == quota.quota_key,
            FeatureUsageCounterModel.period_unit == quota.period_unit,
            FeatureUsageCounterModel.period_value == quota.period_value,
            FeatureUsageCounterModel.reset_mode == quota.reset_mode,
            FeatureUsageCounterModel.window_start == window.window_start,
        )
        .with_for_update()  # NB: SQLite ignore cette clause, PostgreSQL l'applique
        .limit(1)
    )
    counter = db.scalar(query)
    if counter is not None:
        return counter
    counter = FeatureUsageCounterModel(
        user_id=user_id,
        feature_code=feature_code,
        quota_key=quota.quota_key,
        period_unit=quota.period_unit,
        period_value=quota.period_value,
        reset_mode=quota.reset_mode,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=0,
    )
    try:
        with db.begin_nested():
            db.add(counter)
            db.flush()
    except IntegrityError:
        counter = db.scalar(query)
        if counter is None:
            raise
    return counter
```

### Intégration dans `EntitlementService`

```python
# Dans la branche binding.access_mode == AccessMode.QUOTA, après résolution de quotas
if binding.access_mode == AccessMode.QUOTA and quota_models and is_billing_active:
    usage_states = [
        QuotaUsageService.get_usage(db, user_id=user_id, feature_code=feature_code, quota=q)
        for q in quotas
    ]
    quota_exhausted = any(s.exhausted for s in usage_states)
    final_access = not quota_exhausted
else:
    usage_states = []
    quota_exhausted = False
    final_access = is_billing_active and is_enabled_by_plan

return FeatureEntitlement(
    ...,
    usage_states=usage_states,
    quota_exhausted=quota_exhausted,
    final_access=final_access,
    reason="billing_inactive" if not is_billing_active else "canonical_binding",
)
```

> Ne **jamais** appeler `consume` dans `get_feature_entitlement` — c'est une lecture, pas une consommation.

### Valeurs par défaut pour les cas non-quota

Dans tous les cas où `usage_states` n'est pas pertinent (no_plan, billing_inactive, unlimited, disabled, legacy_fallback), utiliser :
```python
usage_states=[]
quota_exhausted=False
```

### Cas limites à anticiper

| Cas | Comportement attendu |
|-----|---------------------|
| `ref_dt` naïf (sans tzinfo) | `ValueError("ref_dt must be timezone-aware")` |
| `ref_dt` en timezone non-UTC | Conversion automatique en UTC avant calcul |
| `reset_mode=rolling` | `ValueError("rolling windows not supported in this version")` |
| `amount <= 0` dans `consume` | `ValueError("amount must be >= 1")` |
| `used_count + amount == quota_limit` | Autorisé — `exhausted=True`, `remaining=0` |
| `used_count + amount > quota_limit` | `QuotaExhaustedError` |
| Fin de mois (Jan 31 + 1 mois) | window_end = 2026-02-01 — l'algorithme divmod gère correctement |
| Binding `access_mode=quota` sans quota en DB | Cas géré en 61-9 (log warning, `final_access=False`) — inchangé |
| Époque `lifetime` | 1970-01-01 UTC fixe, indépendante de la date de souscription |

### Éviter les erreurs de régression

- **`QuotaService` ne doit PAS être modifié** — lit encore `UserDailyQuotaUsageModel` directement.
- **`B2BUsageService` ne doit PAS être modifié**.
- **Les 14 tests existants de `test_entitlement_service.py`** continuent de passer. Les champs `usage_states` et `quota_exhausted` ont des valeurs par défaut (`[]` et `False`) compatibles. Les tests de binding quota sans compteur (`used=0` implicite) retournent `final_access=True` car `remaining=quota_limit > 0`.
- **Créer `entitlement_types.py` avant tout le reste** pour éviter les imports cassés en cours de dev.

### Pattern de test SQLite in-memory

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infra.db.base import Base

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
# quota_usage_service n'a pas besoin de mocker BillingService
# Les tests opèrent directement sur FeatureUsageCounterModel

# Note : SELECT FOR UPDATE est ignoré par SQLite (traduit en SELECT).
# Les tests de concurrence réelle sont réservés à PostgreSQL (intégration).
```

### Références

- [backend/app/services/quota_service.py](backend/app/services/quota_service.py) lignes 117-149 — patron `_find_or_create_usage_row` à reproduire
- [backend/app/services/entitlement_service.py](backend/app/services/entitlement_service.py) — à enrichir
- [backend/app/infra/db/models/product_entitlements.py](backend/app/infra/db/models/product_entitlements.py) — `FeatureUsageCounterModel`, `PeriodUnit`, `ResetMode`
- [backend/app/tests/unit/test_entitlement_service.py](backend/app/tests/unit/test_entitlement_service.py) — à étendre
- [backend/app/tests/unit/test_quota_service.py](backend/app/tests/unit/test_quota_service.py) — pattern de test atomique
- [docs/architecture/product-entitlements-model.md](docs/architecture/product-entitlements-model.md) — contraintes DB

### Project Structure Notes

- `backend/app/services/` — même niveau que les services existants
- Conventions : `@staticmethod`, PascalCase, `frozen=True` pour les dataclasses de valeur

---

## Hors périmètre explicite

Cette story **ne doit pas** :
- Migrer `QuotaService` ou `B2BUsageService` vers `QuotaUsageService` (→ 61-11)
- Brancher `astrologer_chat` via le chemin `legacy_fallback` sur `feature_usage_counters` (→ 61-11)
- Créer des endpoints API publics `/entitlements/*` ou `/quotas/*`
- Implémenter les fenêtres `rolling`
- Créer de migration Alembic
- Modifier `billing_service.py`, `quota_service.py` ou `b2b_usage_service.py`
- Créer un job de reset des compteurs

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- 2026-03-25 : correction post-review du chemin `access_mode=quota` pour désactiver proprement l'accès si un quota `reset_mode=rolling` est configuré, au lieu de lever une `ValueError` runtime.
- 2026-03-25 : `EntitlementService` utilise désormais une seule référence temporelle UTC par évaluation pour éviter les dérives entre quotas d'une même requête.
- 2026-03-25 : le test `Europe/Paris` a été réaligné avec le cas d'acceptation demandé (`2026-03-15 01:00 Europe/Paris = 2026-03-15 00:00 UTC`).
- 2026-03-25 : le test d'atomicité vérifie désormais la requête réellement construite par `_find_or_create_counter` et compile `FOR UPDATE` avec le dialecte PostgreSQL.
- 2026-03-25 : ajout d'un test d'intégration pour garantir qu'un quota `rolling` ne fait plus planter `EntitlementService`.

### File List

- backend/app/services/entitlement_service.py
- backend/app/services/entitlement_types.py
- backend/app/services/quota_usage_service.py
- backend/app/services/quota_window_resolver.py
- backend/app/tests/unit/test_entitlement_service.py
- backend/app/tests/unit/test_quota_usage_service.py
- backend/app/tests/unit/test_quota_window_resolver.py

### Senior Developer Review (AI)

- 2026-03-25 : findings de revue corrigés. Le chemin `rolling` ne provoque plus de crash applicatif, le cas Paris revendiqué est bien testé, et la vérification `FOR UPDATE` cible désormais l'implémentation de production.

### Change Log

- 2026-03-25 | Codex | Correction des findings de code review 61-10, durcissement des tests et revalidation lint/tests.

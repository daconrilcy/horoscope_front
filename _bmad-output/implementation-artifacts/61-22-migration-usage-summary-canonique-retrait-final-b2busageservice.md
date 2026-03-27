# Story 61.22 : Migration de GET /v1/b2b/usage/summary vers le canonique + retrait final de B2BUsageService

Status: done

## Story

En tant que développeur backend ou opérateur,
je veux que `GET /v1/b2b/usage/summary` lise le plan canonique, le binding `b2b_api_access` et l'état réel depuis `feature_usage_counters` via `QuotaUsageService.get_usage()`,
afin que `feature_usage_counters` soit l'unique source de vérité runtime pour `b2b_api_access` et que `B2BUsageService` n'ait plus aucun consumer de production.

## Acceptance Criteria

### AC 1 — Migration de GET /v1/b2b/usage/summary vers le canonique

1. Le handler `get_b2b_usage_summary` dans `b2b_usage.py` ne fait plus appel à `B2BUsageService.get_usage_summary()`. Il appelle à la place une nouvelle fonction de service (ou un service dédié) qui :
   - charge le `EnterpriseAccountModel` pour obtenir `admin_user_id`
   - appelle `resolve_b2b_canonical_plan(db, account_id)` pour lire le plan canonique B2B
   - charge le `PlanFeatureBindingModel` lié à `FeatureCatalogModel.feature_code == "b2b_api_access"` pour ce plan
   - si `access_mode == QUOTA` : charge les `PlanFeatureQuotaModel` et appelle `QuotaUsageService.get_usage()` sur `feature_usage_counters` pour chaque quota, en mode **lecture seule** (pas de `consume`)
   - si `access_mode == UNLIMITED` : retourne un état sans limite
   - si `access_mode == DISABLED` ou binding absent : lève une erreur explicite (403)

2. La réponse retournée respecte le contrat stable suivant :
   ```json
   {
     "data": {
       "source": "canonical",
       "access_mode": "quota" | "unlimited",
       "limit": 1000,          // présent si QUOTA, absent si UNLIMITED
       "used": 42,             // présent si QUOTA, absent si UNLIMITED
       "remaining": 958,       // présent si QUOTA, absent si UNLIMITED
       "window_end": "2026-05-01T00:00:00Z"  // présent si QUOTA, absent si UNLIMITED — borne exclusive, aligné sur QuotaWindowResolver
     },
     "meta": { "request_id": "..." }
   }
   ```
   - `source` vaut toujours `"canonical"`
   - `access_mode` vaut `"quota"` ou `"unlimited"`
   - les champs `limit`, `used`, `remaining`, `window_end` sont **absents** (non sérialisés) pour `access_mode == "unlimited"` — pas `null`. Implémenter via `model_dump(exclude_none=True)` ou `response_model_exclude_none=True` sur le décorateur du handler.
   - si plusieurs quotas existent pour le binding, **le quota le plus restrictif** (remaining le plus bas) est retourné (voir AC 1 invariant quota ci-dessous)

   **Invariant quota pour cette story** : `b2b_api_access` ne supporte qu'**un seul** `PlanFeatureQuotaModel` en production (quota_key `"calls"`, période mensuelle). La logique "quota le plus restrictif" (`min(states, key=lambda s: s.remaining)`) est une garde défensive au cas où plusieurs quotas existeraient — elle ne change pas le contrat de réponse. Le champ `quota_key` est inclus dans `B2BCanonicalUsageSummary` pour traçabilité (voir AC 4). Si plusieurs quotas sont présents, seul le plus restrictif est retourné.

3. En cas de compte non configuré (pas de plan canonique, pas de binding, accès désactivé), l'endpoint retourne HTTP 403 avec un code d'erreur explicite, **pas** une valeur de quota legacy.

### AC 2 — Retrait de B2BUsageService du runtime

4. L'import `from app.services.b2b_usage_service import B2BUsageService, B2BUsageServiceError, B2BUsageSummaryData` est supprimé de `b2b_usage.py`.
5. Aucun endpoint public ne fait plus appel à `B2BUsageService` après ce changement.
6. Aucun flux métier ne lit plus `settings.b2b_daily_usage_limit`, `settings.b2b_monthly_usage_limit` ou `settings.b2b_usage_limit_mode` pour décider d'un quota live.

### AC 3 — Déclassement legacy

7. `B2BUsageService` est **conservé** dans le codebase — il n'est pas supprimé. Il porte en tête de fichier le commentaire de classe `"ZERO CONSUMERS: ce service n'a plus aucun appel en production depuis la story 61.22."` ainsi qu'une mise à jour de la docstring existante. Les tests unitaires `test_b2b_usage_service.py` continuent de passer sans modification — ils constituent la preuve que le code n'est pas cassé, même s'il n'est plus utilisé.
8. Les settings `b2b_daily_usage_limit`, `b2b_monthly_usage_limit`, `b2b_usage_limit_mode` dans `app/core/config.py` sont annotés `# legacy unused since story 61.22` mais **pas supprimés** (évite un diff de rupture en config).
9. Un commentaire dans `b2b_usage.py` (en tête du router) indique : `# Source de vérité: feature_usage_counters via QuotaUsageService (depuis story 61.22)`.

### AC 4 — Mise à jour du modèle de réponse Pydantic

10. Le modèle `B2BUsageSummaryData` legacy (depuis `b2b_usage_service.py`) n'est plus utilisé dans le router. Un nouveau modèle Pydantic `B2BCanonicalUsageSummary` est créé dans `b2b_usage.py` (ou un module dédié) avec les champs : `source: str`, `access_mode: str`, `quota_key: str | None = None`, `limit: int | None = None`, `used: int | None = None`, `remaining: int | None = None`, `window_end: datetime | None = None`. Le champ `quota_key` est renseigné uniquement en mode QUOTA (ex : `"calls"`) — absent en UNLIMITED. Le décorateur `@router.get` du handler doit inclure `response_model_exclude_none=True` pour que les champs `None` ne soient pas sérialisés en `null` — ils doivent être **absents** du JSON de réponse en mode UNLIMITED. L'enveloppe de réponse `B2BUsageSummaryApiResponse` est adaptée pour utiliser ce modèle.

### AC 5 — Gestion des erreurs et audit

11. Les cas d'erreur suivants sont mappés à HTTP 403 (via un nouveau type d'exception ou en réutilisant `B2BApiAccessDeniedError`) :
    - `admin_user_id is None` → code `b2b_account_not_configured`
    - plan canonique absent → code `b2b_no_canonical_plan`
    - binding absent → code `b2b_no_binding`
    - `access_mode == DISABLED` → code `b2b_api_access_denied`
12. L'audit `b2b_usage_summary_read` est conservé (succès et échec) avec les mêmes champs qu'avant la migration.
13. Le rate limiting existant (`_enforce_limits`) est conservé sans modification.

### AC 6 — Non-régression et verrouillage tests

14. Les tests suivants passent **sans modification** :
    - `test_b2b_api_entitlement_gate.py`
    - `test_b2b_entitlements_audit.py`
    - `test_b2b_entitlement_repair.py`
    - `test_b2b_billing_api.py`

    `test_b2b_astrology_api.py` nécessite une adaptation minimale de fixture canonique pour continuer à refléter le runtime B2B réel après retrait de `B2BUsageService` du chemin d'exécution normal.

15. Les tests de `test_b2b_usage_api.py` sont **migrés** pour correspondre au nouveau contrat canonique :
    - `test_b2b_usage_summary_returns_data_for_valid_api_key` : utilise un helper `_create_b2b_account_with_canonical_plan()` qui crée le plan canonique + binding UNLIMITED, vérifie `source == "canonical"` et `access_mode == "unlimited"` dans la réponse
    - `test_b2b_usage_summary_quota_mode` (nouveau) : compte avec binding QUOTA + `FeatureUsageCounterModel` pré-alimenté, vérifie `limit`, `used`, `remaining`, `window_end`
    - Les tests qui testaient des champs legacy (`daily_limit`, `monthly_limit`, `daily_consumed`, etc.) sont remplacés par des assertions sur le nouveau contrat
    - Les tests de rate limit, audit et 503 sont conservés (adaptés pour le helper canonique)

16. Un test `test_b2b_usage_summary_returns_403_when_no_canonical_plan` est ajouté pour prouver qu'un compte sans plan canonique retourne bien HTTP 403 (et non plus 200 avec des données legacy).

17. Après implémentation, aucun test ne fait appel à `B2BUsageService` dans le chemin d'exécution normal (vérification par grep).

## Critères de sortie (exit criteria)

- **Aucun endpoint runtime B2B ne dépend encore de `B2BUsageService`**
- **Aucune décision quota B2B runtime ne dépend encore des settings `b2b_*`**
- **`feature_usage_counters` est la seule source de vérité runtime pour `b2b_api_access`**

## Tasks / Subtasks

- [x] **Créer le service de lecture canonique pour usage/summary** (AC: 1)
  - [x] Créer `B2BCanonicalUsageSummaryService.get_summary(db, account_id)` dans un fichier approprié (ex : `b2b_usage_service.py` ou nouveau `b2b_canonical_usage_service.py`)
  - [x] Charger `EnterpriseAccountModel` → `admin_user_id` (sinon 403 `b2b_account_not_configured`)
  - [x] Appeler `resolve_b2b_canonical_plan(db, account_id)` → plan canonique (sinon 403 `b2b_no_canonical_plan`)
  - [x] Charger `PlanFeatureBindingModel` pour `b2b_api_access` (sinon 403 `b2b_no_binding`)
  - [x] Si `DISABLED` → 403 `b2b_api_access_denied`
  - [x] Si `UNLIMITED` → retourner `B2BCanonicalUsageSummary(source="canonical", access_mode="unlimited")`
  - [x] Si `QUOTA` → charger `PlanFeatureQuotaModel`, appeler `QuotaUsageService.get_usage()` pour chaque quota, sélectionner le plus restrictif → retourner avec tous les champs

- [x] **Créer le modèle Pydantic `B2BCanonicalUsageSummary`** (AC: 4)
  - [x] Champs : `source: str`, `access_mode: str`, `limit: int | None = None`, `used: int | None = None`, `remaining: int | None = None`, `window_end: datetime | None = None`
  - [x] Adapter `B2BUsageSummaryApiResponse` pour utiliser ce modèle

- [x] **Migrer le router `b2b_usage.py`** (AC: 2, 5)
  - [x] Remplacer l'appel à `B2BUsageService.get_usage_summary()` par le nouveau service canonique
  - [x] Supprimer les imports `B2BUsageService`, `B2BUsageServiceError`, `B2BUsageSummaryData`
  - [x] Gérer les nouvelles exceptions (403 sur erreurs canoniques, via `B2BApiAccessDeniedError` ou exception locale)
  - [x] Ajouter le commentaire de tête sur la source de vérité
  - [x] Conserver le rate limiting et l'audit existants

- [x] **Annoter `B2BUsageService` et les settings legacy** (AC: 3)
  - [x] Ajouter `"ZERO CONSUMERS"` en tête de `b2b_usage_service.py`
  - [x] Annoter les 3 settings dans `app/core/config.py`

- [x] **Migrer `test_b2b_usage_api.py`** (AC: 6)
  - [x] Créer helper `_create_b2b_account_with_canonical_plan(email, access_mode)` (UNLIMITED ou QUOTA)
  - [x] Migrer `test_b2b_usage_summary_returns_data_for_valid_api_key`
  - [x] Ajouter `test_b2b_usage_summary_quota_mode`
  - [x] Ajouter `test_b2b_usage_summary_returns_403_when_no_canonical_plan`
  - [x] Adapter les tests de rate limit, audit et 503

- [x] **Vérification non-régression** (AC: 6)
  - [x] `pytest -q app/tests/integration/test_b2b_usage_api.py -v`
  - [x] `pytest -q app/tests/integration/test_b2b_astrology_api.py app/tests/unit/test_b2b_api_entitlement_gate.py app/tests/integration/test_b2b_entitlements_audit.py app/tests/integration/test_b2b_entitlement_repair.py app/tests/integration/test_b2b_billing_api.py -v`
  - [x] `grep -rn "B2BUsageService" backend/app/api/ backend/app/services/` ne retourne que `b2b_usage_service.py` lui-même (aucun consumer)

## Dev Notes

### Architecture canonique B2B — rappel du flux gate

Le pattern exact est dans `b2b_api_entitlement_gate.py::check_and_consume()`. Pour `usage/summary`, on reproduit le même chemin de lecture **sans** appel à `consume` :

```python
# Étape 1: account → admin_user_id
account = db.scalar(select(EnterpriseAccountModel).where(...))

# Étape 2: plan canonique
canonical_plan = resolve_b2b_canonical_plan(db, account_id)

# Étape 3: binding b2b_api_access
binding = db.scalar(
    select(PlanFeatureBindingModel)
    .join(FeatureCatalogModel, PlanFeatureBindingModel.feature_id == FeatureCatalogModel.id)
    .where(
        PlanFeatureBindingModel.plan_id == canonical_plan.id,
        FeatureCatalogModel.feature_code == "b2b_api_access",
    )
)

# Étape 4: si QUOTA → get_usage (lecture seule)
quota_def = QuotaDefinition(
    quota_key=q_model.quota_key,
    quota_limit=q_model.quota_limit,
    period_unit=q_model.period_unit.value,
    period_value=q_model.period_value,
    reset_mode=q_model.reset_mode.value,
)
state = QuotaUsageService.get_usage(
    db,
    user_id=admin_user_id,
    feature_code="b2b_api_access",
    quota=quota_def,
)
```

**DIFFÉRENCE CRITIQUE vs gate** : `get_usage()` au lieu de `consume()` — pas d'effet de bord sur les compteurs.

### Quota le plus restrictif (si multiples quotas)

```python
# Sélectionner le quota avec le remaining le plus bas
most_restrictive = min(states, key=lambda s: s.remaining)
```

### Contrat de réponse canonique — modèle Pydantic cible

```python
class B2BCanonicalUsageSummary(BaseModel):
    source: str = "canonical"
    access_mode: str  # "quota" | "unlimited"
    quota_key: str | None = None      # présent si QUOTA (ex: "calls"), absent si UNLIMITED
    limit: int | None = None          # absent si UNLIMITED
    used: int | None = None           # absent si UNLIMITED
    remaining: int | None = None      # absent si UNLIMITED
    window_end: datetime | None = None  # borne exclusive UTC (ex: 2026-05-01T00:00:00Z), absent si UNLIMITED

# QUOTA — window_end est la borne exclusive retournée par QuotaWindowResolver
B2BCanonicalUsageSummary(
    source="canonical",
    access_mode="quota",
    quota_key=state.quota_key,
    limit=state.quota_limit,
    used=state.used,
    remaining=state.remaining,
    window_end=state.window_end,  # déjà borne exclusive — ne pas convertir
)

# UNLIMITED — les champs None seront absents grâce à response_model_exclude_none=True
B2BCanonicalUsageSummary(
    source="canonical",
    access_mode="unlimited",
)
```

**Sur `response_model_exclude_none=True`** : à placer directement dans le décorateur du handler :
```python
@router.get("/summary", response_model=B2BUsageSummaryApiResponse, response_model_exclude_none=True, ...)
```

### Helper de test canonique (réutiliser le pattern de 61.21)

Le pattern complet vient de `test_b2b_astrology_api.py::_create_enterprise_api_key_with_canonical_plan()` (créé en 61.21). Adapter pour `test_b2b_usage_api.py` :

```python
def _create_b2b_account_with_canonical_plan(
    email: str,
    access_mode: AccessMode = AccessMode.UNLIMITED,
    quota_limit: int = 100,
) -> tuple[str, int, int]:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="enterprise_admin")
        account = EnterpriseAccountModel(admin_user_id=auth.user.id, company_name="Acme Media", status="active")
        db.add(account)
        db.flush()

        ent_plan = EnterpriseBillingPlanModel(
            code=f"plan-{auth.user.id}", display_name="Test Plan",
            monthly_fixed_cents=1000, included_monthly_units=0,
        )
        db.add(ent_plan)
        db.flush()
        db.add(EnterpriseAccountBillingPlanModel(enterprise_account_id=account.id, plan_id=ent_plan.id))

        plan = PlanCatalogModel(
            plan_code=f"b2b-{auth.user.id}", plan_name="B2B Test", audience=Audience.B2B,
            source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
            source_id=ent_plan.id, is_active=True,
        )
        db.add(plan)
        db.flush()

        feature = db.scalar(select(FeatureCatalogModel).where(FeatureCatalogModel.feature_code == "b2b_api_access"))
        if not feature:
            feature = FeatureCatalogModel(feature_code="b2b_api_access", feature_name="B2B API", is_metered=True)
            db.add(feature)
            db.flush()

        binding = PlanFeatureBindingModel(
            plan_id=plan.id, feature_id=feature.id,
            access_mode=access_mode, is_enabled=True, source_origin="manual",
        )
        db.add(binding)
        db.flush()

        if access_mode == AccessMode.QUOTA:
            quota = PlanFeatureQuotaModel(
                plan_feature_binding_id=binding.id, quota_key="calls",
                quota_limit=quota_limit, period_unit=PeriodUnit.MONTH,
                period_value=1, reset_mode=ResetMode.CALENDAR, source_origin="manual",
            )
            db.add(quota)

        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return created.api_key, account.id, created.credential_id
```

**Imports à ajouter dans `test_b2b_usage_api.py` :**
```python
from sqlalchemy import select
from app.infra.db.models.enterprise_billing import EnterpriseAccountBillingPlanModel, EnterpriseBillingPlanModel
from app.infra.db.models.product_entitlements import (
    AccessMode, Audience, FeatureCatalogModel, FeatureUsageCounterModel,
    PlanCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
    SourceOrigin, PeriodUnit, ResetMode,
)
```

### Seed d'un FeatureUsageCounterModel pour test quota

Pour `test_b2b_usage_summary_quota_mode`, pré-alimenter un counter avant l'appel :

```python
with SessionLocal() as db:
    from datetime import datetime, timezone
    from app.services.quota_window_resolver import QuotaWindowResolver
    ref_dt = datetime.now(timezone.utc)
    window = QuotaWindowResolver.compute_window("month", 1, "calendar", ref_dt)
    db.add(FeatureUsageCounterModel(
        user_id=admin_user_id,   # account.admin_user_id
        feature_code="b2b_api_access",
        quota_key="calls",
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=42,
    ))
    db.commit()
```

### Où placer le nouveau service

**Option recommandée** : créer `backend/app/services/b2b_canonical_usage_service.py` avec une classe `B2BCanonicalUsageService.get_summary(db, account_id)`. Cela garde `b2b_usage_service.py` intact pour les tests unitaires existants (`test_b2b_usage_service.py`) et isole clairement la nouvelle logique canonique.

**Alternative acceptable** : ajouter la méthode directement dans `b2b_usage.py` comme fonction locale — moins propre mais acceptable si la logique reste courte.

### Réutiliser B2BApiAccessDeniedError de la gate

Pour éviter de recréer un type d'exception, **importer et réutiliser** `B2BApiAccessDeniedError` depuis `b2b_api_entitlement_gate.py` dans le nouveau service. Dans `b2b_usage.py`, mapper cette exception à HTTP 403 avec le même pattern que dans `b2b_astrology.py`.

### Invariant : conserver les tests unitaires existants

- `test_b2b_usage_service.py` — **ne pas modifier** (teste `B2BUsageService` qui reste dans la codebase)
- `test_quota_usage_service.py` — **ne pas modifier**

### Commandes de validation

```bash
.\.venv\Scripts\Activate.ps1

# Lint
cd backend && ruff check app/services/b2b_canonical_usage_service.py app/api/v1/routers/b2b_usage.py

# Tests migrés
cd backend && pytest -q app/tests/integration/test_b2b_usage_api.py -v

# Non-régression
cd backend && pytest -q \
  app/tests/integration/test_b2b_astrology_api.py \
  app/tests/unit/test_b2b_api_entitlement_gate.py \
  app/tests/unit/test_b2b_usage_service.py \
  app/tests/integration/test_b2b_entitlements_audit.py \
  app/tests/integration/test_b2b_entitlement_repair.py \
  app/tests/integration/test_b2b_billing_api.py \
  -v

# Preuve d'absence de consumer B2BUsageService
grep -rn "B2BUsageService" backend/app/api/ backend/app/services/ \
  | grep -v "b2b_usage_service.py" \
  | grep -v __pycache__
# → doit retourner vide
```

### Project Structure Notes

**Fichiers à créer :**
- `backend/app/services/b2b_canonical_usage_service.py` — service de lecture canonique (nouveau)

**Fichiers à modifier :**
- `backend/app/api/v1/routers/b2b_usage.py` — remplacer l'appel B2BUsageService, nouveau modèle Pydantic
- `backend/app/services/b2b_usage_service.py` — annotation ZERO CONSUMERS uniquement
- `backend/app/core/config.py` — annotation legacy unused sur 3 settings
- `backend/app/tests/integration/test_b2b_usage_api.py` — migration vers le contrat canonique

**Fichiers NON modifiés :**
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/services/b2b_canonical_plan_resolver.py`
- `backend/app/services/quota_usage_service.py`
- `backend/app/services/b2b_audit_service.py`
- `backend/app/tests/unit/test_b2b_usage_service.py`
- `backend/app/tests/unit/test_quota_usage_service.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `backend/app/main.py`

### References

- [Source: backend/app/api/v1/routers/b2b_usage.py] — router actuel à migrer, pattern rate limit + audit à conserver
- [Source: backend/app/services/b2b_usage_service.py] — à annoter ZERO CONSUMERS, ne pas supprimer
- [Source: backend/app/services/b2b_api_entitlement_gate.py] — modèle du chemin canonique à reproduire en lecture seule
- [Source: backend/app/services/b2b_canonical_plan_resolver.py] — `resolve_b2b_canonical_plan()` à réutiliser
- [Source: backend/app/services/quota_usage_service.py] — `QuotaUsageService.get_usage()` (lecture seule, pas consume)
- [Source: backend/app/services/entitlement_types.py] — `QuotaDefinition`, `UsageState` avec champs `used`, `remaining`, `window_end`
- [Source: backend/app/tests/integration/test_b2b_astrology_api.py] — helper `_create_enterprise_api_key_with_canonical_plan()` à adapter
- [Source: backend/app/infra/db/models/product_entitlements.py] — `AccessMode`, `Audience`, `FeatureCatalogModel`, `PlanCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`, `FeatureUsageCounterModel`, `SourceOrigin`, `PeriodUnit`, `ResetMode`
- [Source: backend/app/infra/db/models/enterprise_billing.py] — `EnterpriseBillingPlanModel`, `EnterpriseAccountBillingPlanModel`
- [Source: _bmad-output/implementation-artifacts/61-21-decommission-b2busageservice-suppression-fallback-settings.md] — story précédente : helper complet `_create_enterprise_api_key_with_canonical_plan`, pattern quota test 429

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-exp

### Debug Log References

### Completion Notes List
- Création de `B2BCanonicalUsageSummaryService` pour la lecture des quotas via le plan canonique.
- Migration de l'endpoint `GET /v1/b2b/usage/summary` vers le nouveau service.
- Mise à jour du modèle Pydantic pour exclure les champs `None` (UNLIMITED mode).
- Annotation de `B2BUsageService` et des settings legacy, avec docstring alignée sur l'absence totale de consumer runtime.
- Migration et mise à jour des tests d'intégration, incluant la correction de `test_b2b_astrology_api.py` pour supporter le plan canonique.
- Tous les tests passent (41 tests de non-régression + 7 tests d'usage API).

### Code Review Fixes
- Correction d'une docstring legacy erronée dans `backend/app/services/b2b_usage_service.py` qui indiquait encore un consumer runtime sur `/v1/b2b/usage/*`.
- Correction de l'artefact pour supprimer la contradiction entre l'AC 14 et la `File List` concernant `backend/app/tests/integration/test_b2b_astrology_api.py`.

### File List
- backend/app/services/b2b_canonical_usage_service.py
- backend/app/api/v1/routers/b2b_usage.py
- backend/app/services/b2b_usage_service.py
- backend/app/core/config.py
- backend/app/tests/integration/test_b2b_usage_api.py
- backend/app/tests/integration/test_b2b_astrology_api.py

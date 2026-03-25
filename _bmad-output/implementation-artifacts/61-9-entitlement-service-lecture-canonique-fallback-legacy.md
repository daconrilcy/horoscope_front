# Story 61.9 : EntitlementService — lecture canonique avec fallback legacy

Status: done

## Story

En tant que système backend,
je veux un `EntitlementService` qui calcule les droits d'accès d'un utilisateur à partir du modèle canonique en priorité, avec fallback sur les règles legacy si la feature n'est pas encore couverte,
afin de centraliser la lecture des droits produit sans casser les services métiers existants (`QuotaService`, `B2BUsageService`, flux Stripe).

---

## Contexte métier et enjeu architectural

### Situation après 61-8

- Le modèle canonique (`plan_catalog`, `feature_catalog`, `plan_feature_bindings`, `plan_feature_quotas`) est opérationnel et peuplé via seed (61-7) + backfill DB (61-8).
- Features couvertes : `astrologer_chat` (B2C quota journalier), `b2b_api_access` (B2B quota mensuel), `natal_chart_long`, `natal_chart_short`, `thematic_consultation` (seedées manuellement).
- Les services métier (`QuotaService`, `B2BUsageService`) lisent encore directement les tables legacy. **Ils ne doivent pas être modifiés dans cette story.**

### Rôle de cette story

Créer un `EntitlementService` en **lecture seule** sur le modèle canonique, avec fallback legacy transparent. Il répond à trois questions :

1. Quel est le **plan commercial canonique** de l'utilisateur ?
2. Pour une `feature_code`, quel est l'**entitlement calculé** ?
3. Si le canonique ne couvre pas le cas, comment **retomber proprement sur le legacy** ?

### Ce que cette story ne fait PAS

- Migrer `QuotaService` ou `B2BUsageService` vers `EntitlementService`.
- Créer des endpoints API publics (un endpoint debug interne `/internal/entitlements/check` est optionnel).
- Modifier les tables ou schémas existants (aucune migration Alembic).
- Gérer les compteurs d'usage (`FeatureUsageCounterModel`).
- Introduire de la logique Stripe ou de facturation.

---

## Contrat de sortie : `FeatureEntitlement`

Le service retourne toujours un objet `FeatureEntitlement` avec les champs suivants :

| Champ | Type | Description |
|-------|------|-------------|
| `plan_code` | `str` | Code du plan canonical (ex : `"premium"`, `"free"`, `"none"` si absent) |
| `billing_status` | `str` | Valeur brute retournée par `BillingService` — typiquement `"active"`, `"trialing"`, `"past_due"`, `"canceled"`, `"none"`. Toute valeur hors `{"active", "trialing"}` est traitée comme inactive pour `final_access`. |
| `is_enabled_by_plan` | `bool` | `True` si le plan autorise la feature (`access_mode != "disabled"`) |
| `access_mode` | `str` | `"disabled"` / `"unlimited"` / `"quota"` / `"unknown"` — mode d'accès au plan, indépendant de la provenance |
| `variant_code` | `str \| None` | Variante du binding (ex : `"single_astrologer"` vs `"multi_astrologer"`) |
| `quotas` | `list[QuotaDefinition]` | Liste des quotas associés au binding canonique |
| `final_access` | `bool` | `True` si l'utilisateur peut accéder à la feature **maintenant** |
| `reason` | `str` | Raison de la décision (voir valeurs ci-dessous) |

**Valeurs de `reason` :**

| Valeur | Signification |
|--------|---------------|
| `"canonical_binding"` | Binding trouvé dans `plan_feature_bindings` — décision issue du canonique |
| `"legacy_fallback"` | Aucun binding canonique applicable, fallback legacy utilisé avec succès (ex : `astrologer_chat` via `daily_message_limit`) |
| `"canonical_no_binding"` | Plan canonique trouvé mais feature non bindée **et** aucun fallback legacy applicable |
| `"no_plan"` | `subscription.plan is None` ou `subscription.status == "none"` — aucun plan retourné par le billing |
| `"billing_inactive"` | Plan présent mais `billing_status` hors `{"active", "trialing"}` |
| `"feature_unknown"` | Feature absente du canonique et non gérée par le fallback legacy |

> **Règle de décision pour `reason`** : `canonical_binding` si binding trouvé → `legacy_fallback` si fallback connu utilisé → `canonical_no_binding` si plan trouvé sans binding et sans fallback → `feature_unknown` si feature totalement inconnue. `no_plan` et `billing_inactive` sont des guards en entrée, prioritaires sur toute résolution feature.

**`QuotaDefinition` :**

```python
@dataclass(frozen=True)
class QuotaDefinition:
    quota_key: str        # ex: "messages", "calls", "interpretations"
    quota_limit: int
    period_unit: str      # "day" | "week" | "month" | "year" | "lifetime"
    period_value: int
    reset_mode: str       # "calendar" | "rolling" | "lifetime"
```

---

## Acceptance Criteria

1. **`get_user_canonical_plan(db, user_id)`** : Résout le `PlanCatalogModel` à partir du `plan_code` retourné par `BillingService.get_subscription_status`. Retourne `None` si `subscription.plan is None` ou si le `plan_code` n'est pas trouvé dans `plan_catalog`. Ne duplique pas la logique de résolution d'abonnement — délègue à `BillingService`. (AC: 1)

2. **`get_feature_entitlement(db, user_id, feature_code)`** : Retourne un `FeatureEntitlement` complet pour tous les cas (plan trouvé/non trouvé, binding trouvé/non trouvé, billing actif/inactif, fallback legacy). (AC: 2)

3. **Priorité canonique** : Si un `PlanFeatureBindingModel` existe pour `(plan_id, feature_id)`, la décision est issue du modèle canonique avec `reason="canonical_binding"`. Les quotas sont lus depuis `PlanFeatureQuotaModel`. (AC: 3)

4. **Fallback legacy pour `astrologer_chat`** : Si aucun binding canonique, lire `BillingPlanModel.daily_message_limit` pour calculer `access_mode` (`quota` si > 0, `disabled` si = 0) avec `reason="legacy_fallback"`. (AC: 4)

5. **`final_access` correct** : `True` uniquement si `billing_status` est `"active"` ou `"trialing"` ET `is_enabled_by_plan` est `True`. Jamais `True` si `billing_status` est `"past_due"`, `"canceled"` ou `"none"`. (AC: 5)

6. **Aucune rupture legacy** : Les tests existants `test_quota_service.py`, `test_b2b_usage_service.py` et `test_billing_service.py` continuent de passer sans modification. `QuotaService` et `B2BUsageService` ne sont pas modifiés. (AC: 6)

7. **Cas `no_plan`** : Si `subscription.plan is None` ou `subscription.status == "none"`, retourner immédiatement `FeatureEntitlement(plan_code="none", billing_status="none", is_enabled_by_plan=False, access_mode="unknown", variant_code=None, quotas=[], final_access=False, reason="no_plan")`. `plan_code="none"` est une valeur synthétique de réponse, non une ligne de `plan_catalog`. (AC: 7)

8. **Cas `billing_inactive`** : Si l'abonnement existe mais `billing_status` est `"past_due"` ou `"canceled"`, `final_access=False` avec `reason="billing_inactive"`. L'entitlement du plan est quand même calculé et retourné. (AC: 8)

9. **Idempotence lecture** : Le service est sans effet de bord. Deux appels consécutifs avec les mêmes arguments retournent le même résultat. (AC: 9)

10. **Tests unitaires** : `backend/app/tests/unit/test_entitlement_service.py` couvre au minimum : binding canonique trouvé (quota), binding canonique trouvé (unlimited), binding canonique trouvé (disabled), pas de binding → fallback `astrologer_chat` (`daily_message_limit=5`), pas de binding → fallback `astrologer_chat` (`daily_message_limit=0`), feature inconnue (ni binding ni fallback), `no_plan` (`subscription.plan is None`), `billing_inactive` (`past_due`), plan présent dans `user_subscriptions` mais absent de `plan_catalog`, binding `access_mode=quota` sans entrée dans `plan_feature_quotas`, statut billing non répertorié (ex : `"unknown_status"`) traité comme inactif. (AC: 10)

---

## Tasks / Subtasks

- [x] **Définir les dataclasses de contrat** `QuotaDefinition` et `FeatureEntitlement` (AC: 2)
  - [x] Créer `backend/app/services/entitlement_service.py` avec les dataclasses en tête de fichier
  - [x] Utiliser `@dataclass(frozen=True)` pour `QuotaDefinition`
  - [x] Utiliser `@dataclass` pour `FeatureEntitlement` (mutable pour faciliter les tests)

- [x] **Implémenter `get_user_canonical_plan`** (AC: 1)
  - [x] Lire `UserSubscriptionModel` → `BillingPlanModel.code` (via `BillingService.get_subscription_status`)
  - [x] Chercher `PlanCatalogModel` par `plan_code` dans `plan_catalog`
  - [x] Retourner `None` si plan absent de `plan_catalog` (log warning)

- [x] **Implémenter `get_feature_entitlement`** (AC: 2, 3, 4, 5, 7, 8)
  - [x] Résoudre `billing_status` et `plan_code` via `BillingService.get_subscription_status`
  - [x] Guard `no_plan` : `subscription.plan is None` ou `status == "none"` → retour immédiat (`plan_code="none"`, `billing_status="none"`)
  - [x] Guard `billing_inactive` : `billing_status` hors `{"active", "trialing"}` → calculer entitlement plan mais `final_access=False`, `reason="billing_inactive"`
  - [x] Résoudre `PlanCatalogModel` et `FeatureCatalogModel`
  - [x] Chercher `PlanFeatureBindingModel` par `(plan_id, feature_id)`
  - [x] Si binding trouvé → lire quotas → construire `FeatureEntitlement` canonique
  - [x] Si binding non trouvé → appeler `_legacy_fallback`
  - [x] Calculer `final_access = billing_status in ("active", "trialing") and is_enabled_by_plan`

- [x] **Implémenter `_legacy_fallback`** (AC: 4)
  - [x] Pour `astrologer_chat` : lire `subscription.plan.daily_message_limit` → `access_mode="quota"` si > 0, sinon `"disabled"`
  - [x] Pour toute autre feature non couverte : retourner `access_mode="unknown"`, `reason="feature_unknown"`, `final_access=False`

- [x] **Tests unitaires** `backend/app/tests/unit/test_entitlement_service.py` (AC: 10)
  - [x] Fixture : DB SQLite in-memory avec `plan_catalog`, `feature_catalog`, `plan_feature_bindings`, `plan_feature_quotas`
  - [x] Mocker `BillingService.get_subscription_status` (via `unittest.mock.patch`)
  - [x] Test : binding canonique `access_mode=quota` → `final_access=True`, `quotas` peuplé, `reason="canonical_binding"`
  - [x] Test : binding canonique `access_mode=unlimited` → `final_access=True`, `quotas=[]`
  - [x] Test : binding canonique `access_mode=disabled` → `final_access=False`, `is_enabled_by_plan=False`
  - [x] Test : pas de binding → fallback `astrologer_chat` avec `daily_message_limit=5` → `access_mode="quota"`, `reason="legacy_fallback"`
  - [x] Test : pas de binding → fallback `astrologer_chat` avec `daily_message_limit=0` → `access_mode="disabled"`, `final_access=False`
  - [x] Test : feature inconnue (ni canonique ni legacy) → `reason="feature_unknown"`, `final_access=False`
  - [x] Test : `billing_status="past_due"` → `final_access=False`, `reason="billing_inactive"`, entitlement quand même calculé
  - [x] Test : `billing_status="none"` (pas d'abo) → `reason="no_plan"`, `plan_code="none"`
  - [x] Test : plan présent en `user_subscriptions` mais absent de `plan_catalog` → fallback legacy
  - [x] Test : binding `access_mode=quota` sans quota en `plan_feature_quotas` → log warning + `final_access=False`
  - [x] Test : `billing_status="unknown_status"` (valeur non répertoriée) → traité comme inactif, `final_access=False`
  - [x] Test : feature connue dans `feature_catalog`, plan canonique trouvé dans `plan_catalog`, mais aucun binding `(plan_id, feature_id)` et feature hors scope fallback legacy → `reason="canonical_no_binding"`, `access_mode="unknown"`, `final_access=False` — **distinct du cas `feature_unknown` où la feature est absente de `feature_catalog`**

- [x] **Non-régression** (AC: 6)
  - [x] Vérifier que `QuotaService` n'importe pas `EntitlementService`
  - [x] Vérifier que `B2BUsageService` n'importe pas `EntitlementService`
  - [x] Lancer tous les tests existants entitlements + quota + b2b

---

## Dev Notes

### Architecture Guardrails

- **Stack** : Python 3.13, FastAPI, SQLAlchemy 2.0 (`Mapped` / `mapped_column`)
- **Session DB** : `from app.infra.db.session import SessionLocal` — utiliser `Session` comme type d'annotation
- **Pattern de requête** : `db.scalar(select(Model).where(...).limit(1))` — exactement comme dans `quota_service.py` et `backfill_plan_catalog_from_legacy.py`
- **Aucune migration** : service purement en lecture sur des tables existantes

### Modèles à importer

```python
from app.infra.db.models.product_entitlements import (
    PlanCatalogModel,
    FeatureCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    AccessMode,
)
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.services.billing_service import BillingService, SubscriptionStatusData
```

### Résolution du plan B2C

L'utilisateur B2C est résolu via `BillingService.get_subscription_status` qui est déjà le point d'entrée de `QuotaService`. **Ne pas dupliquer** la logique de résolution — utiliser `BillingService` directement.

```python
subscription: SubscriptionStatusData = BillingService.get_subscription_status(db, user_id=user_id)
# subscription.status : "active" | "trialing" | "past_due" | "canceled" | "none"
# subscription.plan : BillingPlanData | None
#   .code : str  # ex: "premium"
#   .daily_message_limit : int
```

### Logique de résolution canonique

```
PlanCatalogModel  → via plan_code (= subscription.plan.code)
FeatureCatalogModel → via feature_code
PlanFeatureBindingModel → via (plan_id, feature_id), UniqueConstraint garantie → au plus 1 résultat
PlanFeatureQuotaModel → via plan_feature_binding_id (plusieurs quotas possibles par binding)
```

### Champ `is_enabled` vs `access_mode`

`PlanFeatureBindingModel` a deux champs :
- `is_enabled: bool` — indicateur redondant (peut servir à désactiver temporairement un binding)
- `access_mode: AccessMode` — source de vérité pour le calcul d'entitlement

`is_enabled_by_plan` dans `FeatureEntitlement` doit être calculé comme :
```python
is_enabled_by_plan = binding.is_enabled and binding.access_mode != AccessMode.DISABLED
```

### Pattern de fallback legacy pour `astrologer_chat`

```python
# Lecture directe de la limite depuis la subscription déjà résolue
daily_limit = subscription.plan.daily_message_limit if subscription.plan else 0
if daily_limit > 0:
    access_mode = "quota"
    quotas = [QuotaDefinition(
        quota_key="messages",
        quota_limit=daily_limit,
        period_unit="day",
        period_value=1,
        reset_mode="calendar",
    )]
else:
    access_mode = "disabled"
    quotas = []
```

**Ne pas re-faire de requête SQL** — la `subscription` est déjà résolue en amont.

### Pattern de test SQLite in-memory (hérité de 61-7/61-8)

```python
# Reproduire exactement le pattern de test_product_entitlements_models.py et test_backfill_plan_catalog.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infra.db.base import Base
from app.infra.db.models.product_entitlements import (
    PlanCatalogModel, FeatureCatalogModel, PlanFeatureBindingModel, PlanFeatureQuotaModel,
    Audience, AccessMode, PeriodUnit, ResetMode, SourceOrigin
)

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

# Mocker BillingService
from unittest.mock import patch
from app.services.billing_service import BillingPlanData, SubscriptionStatusData

mock_subscription = SubscriptionStatusData(
    status="active",
    plan=BillingPlanData(
        code="premium",
        display_name="Premium",
        monthly_price_cents=2000,
        currency="EUR",
        daily_message_limit=1000,
        is_active=True,
    ),
    failure_reason=None,
)

with patch("app.services.entitlement_service.BillingService.get_subscription_status", return_value=mock_subscription):
    result = EntitlementService.get_feature_entitlement(db, user_id=1, feature_code="astrologer_chat")
```

### Localisation du fichier

```
backend/app/services/entitlement_service.py   ← nouveau fichier principal
backend/app/tests/unit/test_entitlement_service.py  ← nouveaux tests unitaires
```

**Ne pas** créer de router API dans cette story. Le service est un module interne.

### Cas limites à anticiper

| Cas | Comportement attendu |
|-----|---------------------|
| `plan_code` présent en `user_subscriptions.billing_plans` mais absent de `plan_catalog` | Log warning, fallback legacy |
| `feature_code` présent en `feature_catalog`, plan canonique trouvé, mais pas de binding ET feature hors scope fallback | `reason="canonical_no_binding"`, `access_mode="unknown"`, `final_access=False` |
| `feature_code` présent en `feature_catalog`, pas de binding, mais fallback legacy applicable (`astrologer_chat`) | `reason="legacy_fallback"`, `access_mode` calculé depuis `daily_message_limit` |
| `feature_code` absent de `feature_catalog` ET hors scope fallback | `reason="feature_unknown"`, `access_mode="unknown"`, `final_access=False` |
| Binding avec `access_mode=quota` mais aucun quota en `plan_feature_quotas` | Log warning, `final_access=False` car quota indéfini |
| `billing_status="trialing"` | Traité comme `"active"` pour `final_access` |
| `billing_status="past_due"` | `final_access=False`, entitlement calculé quand même |

### Périmètre du fallback legacy — règle stricte

Le fallback legacy dans cette story est **limité à un seul cas** :

- **`astrologer_chat` B2C** → `subscription.plan.daily_message_limit`

Toute autre feature sans binding canonique retourne `reason="canonical_no_binding"` ou `reason="feature_unknown"` selon que la feature existe dans `feature_catalog` ou non. **Il ne faut pas inventer un fallback B2B ou un fallback générique.** La feature `b2b_api_access` est dans `plan_catalog` via 61-8, mais son support métier complet (comptes entreprise, limites settings) est hors périmètre de 61-9.

### Gestion des statuts billing non anticipés

`billing_status` est la valeur brute retournée par `BillingService`. Tout statut hors `{"active", "trialing"}` doit être traité comme inactif pour `final_access`. **Ne pas utiliser** `if billing_status == "active"` seul — utiliser `if billing_status in _ACTIVE_BILLING_STATUSES` avec une constante :

```python
_ACTIVE_BILLING_STATUSES = frozenset({"active", "trialing"})
```

### Éviter les erreurs de régression

**`QuotaService` ne doit PAS être modifié.** Il continuera de lire `BillingPlanModel.daily_message_limit` directement. La coexistence est intentionnelle pour cette story. La migration de `QuotaService` vers `EntitlementService` est prévue dans une story ultérieure.

**Import cycle risk** : `EntitlementService` importe `BillingService`. `BillingService` ne doit pas importer `EntitlementService`. Vérifier qu'il n'y a pas de cycle.

### References

- [backend/app/infra/db/models/product_entitlements.py](backend/app/infra/db/models/product_entitlements.py) — modèles canoniques et enums
- [backend/app/services/billing_service.py](backend/app/services/billing_service.py) — `BillingService.get_subscription_status`, `SubscriptionStatusData`, `BillingPlanData`
- [backend/app/services/quota_service.py](backend/app/services/quota_service.py) — pattern `_resolve_active_quota_from_subscription` à **ne pas dupliquer** mais à prendre en référence pour le style
- [backend/app/tests/unit/test_product_entitlements_models.py](backend/app/tests/unit/test_product_entitlements_models.py) — pattern SQLite in-memory à reproduire
- [backend/app/tests/unit/test_backfill_plan_catalog.py](backend/app/tests/unit/test_backfill_plan_catalog.py) — pattern de mock et fixtures
- [docs/architecture/product-entitlements-model.md](docs/architecture/product-entitlements-model.md) — documentation du modèle canonique

### Project Structure Notes

- Alignement avec la structure existante : `backend/app/services/` pour tous les services métier
- Pas de sous-dossier spécifique, même niveau que `quota_service.py` et `billing_service.py`
- Conventions de nommage : `EntitlementService` (PascalCase, classe statique comme `QuotaService`), méthodes `@staticmethod`

---

## Hors périmètre explicite

Cette story **ne doit pas** :
- Migrer `QuotaService` ou `B2BUsageService`
- Créer des endpoints API publics `/entitlements/*`
- Toucher `FeatureUsageCounterModel`
- Implémenter un fallback B2B (comptes entreprise, `EnterpriseAccountModel`, `settings.b2b_*`) — si un plan B2B arrive sans binding canonique, retourner `reason="canonical_no_binding"` ou `reason="feature_unknown"` selon le cas
- Créer de migration Alembic
- Modifier `billing_service.py`, `quota_service.py`, ou `b2b_usage_service.py`
- Inventer de nouvelles valeurs de `access_mode` au-delà de `"disabled"`, `"unlimited"`, `"quota"`, `"unknown"`

---

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Implementation started 2026-03-25
- All unit tests passed (13/13)
- Non-regression tests passed (19/19)
- [2026-03-25] Code review : 2 issues critiques corrigés — (1) `canonical_no_binding` jamais retourné : `get_feature_entitlement` restructuré pour distinguer "plan+feature connus sans binding" (→ `canonical_no_binding`) de "feature absente du catalogue" (→ `feature_unknown`) ; (2) test `test_get_feature_entitlement_canonical_no_binding` ajouté (AC 10 exige ce cas). Imports inutilisés supprimés (`field`, `MagicMock`, `QuotaDefinition`). Branche `elif is_billing_active` redondante supprimée. 14/14 tests, 28/28 non-régression.
- [2026-03-25] Post-review corrections manuelles : (1) `billing_inactive` guard étendu à tous les cas y compris `feature_unknown` — quand le billing est inactif, la raison est toujours `billing_inactive` quelle que soit la résolution feature ; (2) warning explicite ajouté dans `get_feature_entitlement` quand `plan_code` existe côté billing mais manque dans `plan_catalog`. 14/14 tests.

### Completion Notes List

- EntitlementService implémenté avec priorité canonique et fallback legacy.
- Tests unitaires complets : 14 tests couvrant tous les cas du contrat.
- Non-régression vérifiée : 28 tests existants (quota, b2b, entitlements) passent.
- Code review adversarial appliqué : `canonical_no_binding` correctement retourné, test manquant ajouté.

### File List

- `backend/app/services/entitlement_service.py`
- `backend/app/tests/unit/test_entitlement_service.py`
- `_bmad-output/implementation-artifacts/61-9-entitlement-service-lecture-canonique-fallback-legacy.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- Initial implementation of EntitlementService (61-9)
- Added unit tests for EntitlementService
- [code-review] Fix canonical_no_binding never returned + add missing test + remove unused imports

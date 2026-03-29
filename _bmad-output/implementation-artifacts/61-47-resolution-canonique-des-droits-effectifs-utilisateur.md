# Story 61.47 : Résolution canonique des droits effectifs utilisateur

Status: done

## Story

En tant que runtime produit,
je veux résoudre pour un utilisateur ou un compte entreprise un snapshot unique de droits effectifs,
afin que le plan commercial, le billing et les quotas soient interprétés une seule fois, de manière cohérente, partout dans l'application.

---

## Contexte métier et enjeu architectural

Le chantier `61.7` à `61.46` a déjà livré :

- le modèle canonique des plans, features, bindings et quotas ;
- la lecture canonique B2C par feature (`EntitlementService`) ;
- le moteur de fenêtres et les compteurs réels B2C/B2B ;
- la séparation stricte des scopes B2C/B2B via `FEATURE_SCOPE_REGISTRY` ;
- les garde-fous DB/runtime/CI ;
- la migration des principaux flux métier vers le canonique.

Ce qui manque encore est un **resolver runtime unique**, orienté lecture seule, capable de produire un **snapshot complet** des droits effectifs pour un sujet donné :

- un utilisateur B2C (`app_user_id`) ;
- ou un compte entreprise B2B (`enterprise_account_id`).

L'objectif n'est plus de décider l'accès à une feature isolée, mais de calculer en une seule fois un état canonique réutilisable par le produit, les endpoints et les futures gates, sans recalcul dispersé ni divergence de raisonnement.

---

## Contrat de sortie attendu

### `EffectiveEntitlementsSnapshot`

Le service retourne un snapshot unique avec au minimum :

| Champ | Type | Description |
|---|---|---|
| `subject_type` | `"b2c_user" \| "b2b_account"` | Type de sujet résolu |
| `subject_id` | `int` | Identifiant du sujet |
| `plan_code` | `str` | Code du plan canonique ou synthétique (`"none"` si absent) |
| `billing_status` | `str` | Statut de billing effectif du sujet |
| `entitlements` | `dict[str, EffectiveFeatureAccess]` | Snapshot par `feature_code` |

### `EffectiveFeatureAccess`

Chaque entrée `entitlements[feature_code]` contient au minimum :

| Champ | Type | Description |
|---|---|---|
| `granted` | `bool` | Accès effectif maintenant |
| `reason_code` | `str` | Raison normalisée de la décision |
| `access_mode` | `str \| None` | `disabled`, `unlimited`, `quota`, ou `None` |
| `variant_code` | `str \| None` | Variante du binding si présente |
| `quota_limit` | `int \| None` | Limite synthétique principale exposée |
| `quota_used` | `int \| None` | Consommation synthétique principale exposée |
| `quota_remaining` | `int \| None` | Reste synthétique principal exposé |
| `period_unit` | `str \| None` | Unité de période synthétique |
| `period_value` | `int \| None` | Valeur de période synthétique |
| `reset_mode` | `str \| None` | Mode de reset synthétique |

Comme un binding canonique peut porter **plusieurs quotas**, le contrat doit aussi conserver le détail réel dans un champ additionnel, par exemple `usage_states: list[UsageState]` ou un équivalent dédié, afin d'éviter tout snapshot lossy. Les champs scalaires ci-dessus servent de résumé minimal.

### `reason_code` normalisés

Le resolver doit normaliser ses décisions avec un vocabulaire stable. Le set minimal attendu est :

- `granted`
- `feature_not_in_plan`
- `billing_inactive`
- `quota_exhausted`
- `binding_disabled`
- `subject_not_eligible`

Le service ne doit pas introduire de chaînes ad hoc différentes selon le chemin B2C/B2B.

---

## Acceptance Criteria

1. Un nouveau service `EffectiveEntitlementResolverService` existe dans `backend/app/services/effective_entitlement_resolver_service.py`. (AC: 1)

2. Le service expose au minimum :
   - `resolve_b2c_user_snapshot(db, *, app_user_id: int) -> EffectiveEntitlementsSnapshot`
   - `resolve_b2b_account_snapshot(db, *, enterprise_account_id: int) -> EffectiveEntitlementsSnapshot` (AC: 1)

3. `EffectiveEntitlementsSnapshot` et `EffectiveFeatureAccess` sont introduits comme contrats explicites réutilisables, sans duplication de types existants inutile. Les types partagés existants dans `backend/app/services/entitlement_types.py` doivent être étendus si cela évite un nouveau module redondant. (AC: 2)

4. Le snapshot couvre **toutes les features actives du scope du sujet** :
   - snapshot B2C : toutes les features déclarées B2C dans `FEATURE_SCOPE_REGISTRY` ;
   - snapshot B2B : toutes les features déclarées B2B dans `FEATURE_SCOPE_REGISTRY`. (AC: 5)

5. Le resolver B2C résout le plan canonique via le billing existant, évalue les bindings/quota canoniques sans effet de bord, et produit un `EffectiveFeatureAccess` correct pour au minimum :
   - feature présente et quota disponible ;
   - feature absente du plan ;
   - feature présente mais billing inactif ;
   - feature présente mais quota épuisé ;
   - feature `UNLIMITED` ;
   - feature `DISABLED`. (AC: 3, 4, 5)

6. Le resolver B2B résout le compte entreprise, son plan canonique et ses compteurs entreprise sans effet de bord, et produit un `EffectiveFeatureAccess` correct pour au minimum un cas avec compteurs entreprise. (AC: 3, 4, 5)

7. Les `reason_code` sont normalisés et cohérents entre chemins B2C et B2B. Une feature non bindée au plan retourne `feature_not_in_plan`, un binding `DISABLED` retourne `binding_disabled`, un statut de billing inactif retourne `billing_inactive`, un quota épuisé retourne `quota_exhausted`, et un sujet ou une feature hors scope/éligibilité retourne `subject_not_eligible`. (AC: 4)

8. Le service est strictement **read-only** :
   - aucune écriture DB ;
   - aucun appel à `consume(...)` ;
   - aucun appel à un helper B2B susceptible de créer un mapping par défaut. (AC: 4)

9. Toute lecture de droits effectifs dans le runtime doit pouvoir être reconstruite à partir du snapshot retourné, sans dépendre de règles implicites hors snapshot. (AC: 5)

10. Des tests unitaires couvrent au minimum :
    - feature présente et quota disponible ;
    - feature absente du plan ;
    - feature présente mais billing inactif ;
    - feature présente mais quota épuisé ;
    - feature `UNLIMITED` ;
    - feature `DISABLED` ;
    - cas B2B avec compteurs entreprise. (AC: 6)

---

## Tasks / Subtasks

- [x] **Créer les contrats de snapshot effectif** (AC: 2, 5)
  - [x] Étendre `backend/app/services/entitlement_types.py` avec `EffectiveEntitlementsSnapshot` et `EffectiveFeatureAccess` au lieu de créer un nouveau module de types redondant
  - [x] Conserver le détail multi-quota dans un champ dédié (`usage_states` ou équivalent), en plus des champs scalaires de résumé
  - [x] Définir une règle de résumé déterministe pour les champs `quota_*` si plusieurs quotas existent : quota épuisé prioritaire, sinon quota au `remaining` minimal

- [x] **Implémenter `EffectiveEntitlementResolverService`** dans `backend/app/services/effective_entitlement_resolver_service.py` (AC: 1, 3, 4, 5)
  - [x] Charger une seule fois le statut billing/plan du sujet
  - [x] Charger les features du scope cible à partir de `FEATURE_SCOPE_REGISTRY`
  - [x] Charger en lot les bindings et quotas du plan canonique
  - [x] Produire un snapshot complet `feature_code -> EffectiveFeatureAccess`
  - [x] Ne faire aucune écriture DB

- [x] **Implémenter `resolve_b2c_user_snapshot`** (AC: 1, 3, 4, 5)
  - [x] Réutiliser `BillingService.get_subscription_status` pour la résolution du plan B2C
  - [x] Réutiliser `QuotaUsageService.get_usage(...)` uniquement en lecture pour les quotas B2C
  - [x] Mapper les cas `QUOTA`, `UNLIMITED`, `DISABLED`, absence de binding et billing inactif vers les `reason_code` normalisés
  - [x] Retourner `plan_code="none"` et `billing_status="none"` si aucun abonnement actif n'est résoluble

- [x] **Implémenter `resolve_b2b_account_snapshot`** (AC: 1, 3, 4, 5)
  - [x] Lire `EnterpriseAccountModel` et valider l'éligibilité du compte sans lever d'effet de bord
  - [x] Résoudre le plan canonique B2B en lecture seule
  - [x] Réutiliser `EnterpriseQuotaUsageService.get_usage(...)` uniquement en lecture pour les quotas B2B
  - [x] Ne pas appeler `B2BBillingService._resolve_active_plan_for_account(...)`, car cette méthode peut créer un mapping par défaut

- [x] **Normaliser les `reason_code`** (AC: 4)
  - [x] Introduire une constante locale ou un enum interne pour éviter les chaînes magiques
  - [x] Aligner B2C et B2B sur le même vocabulaire
  - [x] Documenter le mapping `cas runtime -> reason_code`

- [x] **Ajouter les tests unitaires** dans `backend/app/tests/unit/test_effective_entitlement_resolver_service.py` (AC: 6)
  - [x] Ajouter une fixture SQLite in-memory alignée sur les tests entitlements existants
  - [x] Cibler les cas B2C demandés par les AC
  - [x] Ajouter au moins un cas B2B avec `enterprise_feature_usage_counters`
  - [x] Vérifier l'absence d'effet de bord en lecture : aucune création de compteur si absent

- [x] **Non-régression minimale** (AC: 4, 6)
  - [x] Vérifier que `test_entitlement_service.py` reste vert
  - [x] Vérifier que `test_quota_usage_service.py` reste vert
  - [x] Vérifier que `test_enterprise_quota_usage_service.py` reste vert

---

## Dev Notes

### Architecture Guardrails

- Stack imposée : Python 3.13, FastAPI, SQLAlchemy 2.x, pytest.
- Le service est un use-case applicatif de lecture : emplacement attendu `backend/app/services/`.
- Utiliser `Session` SQLAlchemy comme annotation, `select(...).where(...).limit(1)` comme pattern dominant.
- Le resolver doit être **sans effet de bord**. Il ne doit jamais consommer, muter ni réparer.

### Règle de conception principale

Ne pas implémenter ce resolver en bouclant naïvement sur `EntitlementService.get_feature_entitlement(...)` pour chaque feature :

- cela répéterait la résolution billing et les lectures plan/binding ;
- cela hériterait de `reason` legacy/non normalisés (`canonical_binding`, `disabled_by_plan`, etc.) ;
- cela produirait un snapshot moins maîtrisé et plus coûteux.

Le resolver doit charger une fois les données sujet/plan/features/bindings/quotas, puis calculer le snapshot complet.

### Réutilisation autorisée et interdite

Réutilisations recommandées :

- `BillingService.get_subscription_status(...)` pour B2C
- `resolve_b2b_canonical_plan(...)` ou une logique équivalente strictement read-only pour B2B
- `QuotaUsageService.get_usage(...)` pour les compteurs B2C
- `EnterpriseQuotaUsageService.get_usage(...)` pour les compteurs B2B
- `FEATURE_SCOPE_REGISTRY` comme source de vérité du scope B2C/B2B

Réutilisations interdites dans cette story :

- `QuotaUsageService.consume(...)`
- `EnterpriseQuotaUsageService.consume(...)`
- `B2BBillingService._resolve_active_plan_for_account(...)` car il peut écrire en base
- tout fallback legacy non canonique

### Résolution B2C attendue

Pour `resolve_b2c_user_snapshot(...)` :

1. Résoudre `subscription` via `BillingService.get_subscription_status`.
2. Déduire `plan_code` et `billing_status`.
3. Charger `PlanCatalogModel` via `plan_code`.
4. Énumérer toutes les features B2C depuis `FEATURE_SCOPE_REGISTRY`.
5. Pour chaque feature :
   - binding absent -> `feature_not_in_plan`
   - binding `DISABLED` ou `is_enabled=False` -> `binding_disabled`
   - billing inactif -> `billing_inactive`
   - binding `UNLIMITED` -> `granted`
   - binding `QUOTA` + quota disponible -> `granted`
   - binding `QUOTA` + quota épuisé -> `quota_exhausted`

### Résolution B2B attendue

Pour `resolve_b2b_account_snapshot(...)` :

1. Charger `EnterpriseAccountModel`.
2. Si le compte est absent ou inactif, retourner un snapshot non accordé avec `subject_not_eligible`.
3. Résoudre le plan canonique via le mapping `enterprise_account_billing_plans -> plan_catalog`.
4. Énumérer toutes les features B2B depuis `FEATURE_SCOPE_REGISTRY`.
5. Évaluer les bindings B2B comme pour le B2C, mais avec `EnterpriseQuotaUsageService.get_usage(...)`.

Important : la story ne doit pas réintroduire de logique settings/fallback B2B. Le runtime B2B a déjà été basculé vers le canonique entre `61.18` et `61.26`.

### Règle de couverture du snapshot

Le snapshot doit être reconstructible partout dans le runtime. Il doit donc contenir une entrée pour **chaque feature active du scope** même si :

- aucun binding n'existe pour le plan ;
- le billing est inactif ;
- le sujet n'est pas éligible.

Ne pas limiter `entitlements` aux seules features bindées, sinon le cas `feature_not_in_plan` devient impossible à reconstruire depuis le snapshot seul.

### Synthèse multi-quota

Le modèle canonique autorise plusieurs quotas par binding. Les champs scalaires requis (`quota_limit`, `quota_used`, `quota_remaining`, `period_unit`, `period_value`, `reset_mode`) doivent donc être des **résumés**.

Règle recommandée :

1. Si au moins un quota est épuisé, exposer en résumé le premier quota épuisé selon l'ordre déterministe `(quota_key, period_unit, period_value)`.
2. Sinon exposer le quota avec `remaining` minimal.
3. Si pas de quota : tous les champs `quota_*` et `period_*` à `None`.

Le détail complet reste présent dans `usage_states`.

### Mapping des `reason_code`

| Cas | `reason_code` attendu |
|---|---|
| Accès accordé (`UNLIMITED` ou `QUOTA` disponible) | `granted` |
| Feature sans binding dans le plan | `feature_not_in_plan` |
| Billing inactif | `billing_inactive` |
| Binding désactivé ou `DISABLED` | `binding_disabled` |
| Au moins un quota épuisé | `quota_exhausted` |
| Sujet absent/inactif ou feature hors scope du sujet | `subject_not_eligible` |

### Fichiers cibles

```text
backend/app/services/effective_entitlement_resolver_service.py      ← NOUVEAU
backend/app/services/entitlement_types.py                           ← MODIFIÉ
backend/app/tests/unit/test_effective_entitlement_resolver_service.py ← NOUVEAU
```

### Patterns de test à reprendre

- `backend/app/tests/unit/test_entitlement_service.py` pour le setup SQLite in-memory B2C
- `backend/app/tests/unit/test_quota_usage_service.py` pour les cas quota disponible/épuisé sans side effects
- `backend/app/tests/unit/test_enterprise_quota_usage_service.py` pour les compteurs entreprise

### Anti-régressions explicites

- Ne pas modifier `QuotaUsageService` ni `EnterpriseQuotaUsageService` dans cette story.
- Ne pas modifier `B2BApiEntitlementGate` ni les gates métier existantes : le resolver prépare le terrain, il ne remplace pas encore tous les call sites.
- Ne pas ajouter de migration Alembic.
- Ne pas écrire d'endpoint API dans cette story.
- Ne pas inventer de nouveau fallback legacy B2C/B2B.

### Git Intelligence

Les derniers commits de l'épic 61 (`61.43` à `61.46`) concernent l'alerting ops et la suppression de bruit. Ils sont orthogonaux à cette story. Le resolver doit rester concentré sur le runtime produit et ne pas coupler sa sortie aux sous-systèmes ops d'audit/alerting.

### References

- `backend/app/services/entitlement_service.py`
- `backend/app/services/entitlement_types.py`
- `backend/app/services/quota_usage_service.py`
- `backend/app/services/enterprise_quota_usage_service.py`
- `backend/app/services/b2b_canonical_plan_resolver.py`
- `backend/app/services/feature_scope_registry.py`
- `backend/app/services/b2b_api_entitlement_gate.py`
- `backend/app/tests/unit/test_entitlement_service.py`
- `backend/app/tests/unit/test_enterprise_quota_usage_service.py`
- `backend/app/infra/db/models/product_entitlements.py`
- `backend/app/infra/db/models/enterprise_feature_usage_counters.py`
- `docs/architecture/product-entitlements-model.md`
- `_bmad-output/implementation-artifacts/61-9-entitlement-service-lecture-canonique-fallback-legacy.md`
- `_bmad-output/implementation-artifacts/61-10-quota-window-resolver-et-usage-service.md`
- `_bmad-output/implementation-artifacts/61-7-a-61-46-synthese-entitlements-canoniques-et-ops.md`

### Project Structure Notes

- Respecter `backend/app/services` pour le service métier et `backend/app/tests/unit` pour les tests.
- Réutiliser les dataclasses/types existants dans `entitlement_types.py` plutôt que multiplier les fichiers de types proches.
- Aucun changement frontend attendu dans cette story.

---

## Hors périmètre explicite

Cette story ne doit pas :

- migrer les call sites existants vers le nouveau snapshot ;
- remplacer `EntitlementService` ;
- créer un endpoint `/v1/entitlements/effective` ;
- modifier le modèle de données canonique ;
- introduire des écritures compensatoires ou réparations automatiques ;
- consommer un quota ;
- changer les services ops des stories `61.31` à `61.46`.

---

## Dev Agent Record

### Agent Model Used

gpt-5-codex

### Debug Log References

- Analyse du workflow `bmad-create-story` et de son template/checklist.
- Relecture des stories 61.8, 61.9, 61.10 et de la synthèse 61.7 à 61.46.
- Relecture du code réel : `entitlement_service`, `entitlement_types`, `enterprise_quota_usage_service`, `b2b_billing_service`, `b2b_api_entitlement_gate`, `feature_scope_registry`, modèles DB et tests unitaires existants.
- Vérification de l'historique git récent : derniers commits centrés sur 61.46, sans dépendance directe sur le runtime entitlement.

### Completion Notes List

- Implémentation du service `EffectiveEntitlementResolverService` avec les méthodes `resolve_b2c_user_snapshot` et `resolve_b2b_account_snapshot`.
- Extension de `entitlement_types.py` pour inclure `EffectiveEntitlementsSnapshot` et `EffectiveFeatureAccess`.
- Normalisation des `reason_code` selon les spécifications.
- Implémentation d'une règle de synthèse déterministe pour le multi-quota.
- Ajout de tests unitaires complets couvrant les cas B2C et B2B.
- Validation de la non-régression avec les tests existants.

### File List

- `backend/app/services/entitlement_types.py`
- `backend/app/services/effective_entitlement_resolver_service.py`
- `backend/app/tests/unit/test_effective_entitlement_resolver_service.py`
- `_bmad-output/implementation-artifacts/61-47-resolution-canonique-des-droits-effectifs-utilisateur.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

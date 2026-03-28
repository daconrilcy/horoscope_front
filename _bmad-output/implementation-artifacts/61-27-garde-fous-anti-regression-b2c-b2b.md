# Story 61.27 : Garde-fous anti-régression entre compteurs B2C et B2B

Status: done

## Story

En tant que développeur backend,
je veux introduire un registre de scope explicite pour les `feature_code` et faire lever une erreur immédiate et claire à `QuotaUsageService` et `EnterpriseQuotaUsageService` si le mauvais service est appelé pour le mauvais scope,
afin que la séparation B2C/B2B entre `feature_usage_counters` et `enterprise_feature_usage_counters` soit une règle structurelle du code — impossible à violer par inadvertance.

## Acceptance Criteria

### AC 1 — Registre de scope centralisé (`feature_scope_registry.py`)

1. [x] Un fichier `backend/app/services/feature_scope_registry.py` est créé, contenant :
   - Un `Enum` ou `Literal` `FeatureScope` avec les valeurs `"b2c"` et `"b2b"`.
   - Un dictionnaire `FEATURE_SCOPE_REGISTRY: dict[str, FeatureScope]` — **registre exhaustif des feature codes soumis aux services de quota** (pas de toutes les features produit) :
     - `"astrologer_chat"` → `FeatureScope.B2C`
     - `"thematic_consultation"` → `FeatureScope.B2C`
     - `"natal_chart_long"` → `FeatureScope.B2C`
     - `"b2b_api_access"` → `FeatureScope.B2B`
   - Une fonction utilitaire `get_feature_scope(feature_code: str) -> FeatureScope` qui retourne le scope ou lève `UnknownFeatureCodeError` si le code n'est pas enregistré.
2. [x] Une exception `UnknownFeatureCodeError(ValueError)` est définie dans ce même fichier pour les codes inconnus. Elle constitue elle-même un garde-fou : tout `feature_code` passé à un service de quota **doit** être enregistré dans `FEATURE_SCOPE_REGISTRY`.
3. [x] Une exception `InvalidQuotaScopeError(ValueError)` est définie dans ce même fichier. Elle porte les attributs : `feature_code: str`, `expected_scope: FeatureScope`, `actual_scope: FeatureScope`. Son message est explicite, par exemple :
   `"feature_code 'b2b_api_access' is B2B — use EnterpriseQuotaUsageService, not QuotaUsageService."`

### AC 2 — Garde-fou dans `QuotaUsageService`

4. [x] `QuotaUsageService.get_usage()` et `QuotaUsageService.consume()` appellent `get_feature_scope(feature_code)` en début de méthode, **sans** intercepter `UnknownFeatureCodeError`.
5. [x] Si le scope retourné est `FeatureScope.B2B`, ils lèvent `InvalidQuotaScopeError` **avant** toute interaction DB.
6. [x] Si le `feature_code` est inconnu, `UnknownFeatureCodeError` **se propage** immédiatement — comportement **fail-closed** : un code non enregistré est bloqué, pas ignoré. Toute nouvelle feature quota **doit** être ajoutée à `FEATURE_SCOPE_REGISTRY` avant usage.
7. [x] Les méthodes privées `_find_or_create_counter` ne sont pas modifiées directement — la validation se fait dans les méthodes publiques.

### AC 3 — Garde-fou dans `EnterpriseQuotaUsageService`

8. [x] `EnterpriseQuotaUsageService.get_usage()` et `EnterpriseQuotaUsageService.consume()` appellent `get_feature_scope(feature_code)` en début de méthode, **sans** intercepter `UnknownFeatureCodeError`.
9. [x] Si le scope retourné est `FeatureScope.B2C`, ils lèvent `InvalidQuotaScopeError` **avant** toute interaction DB.
10. [x] Si le `feature_code` est inconnu, `UnknownFeatureCodeError` **se propage** immédiatement — même comportement fail-closed que pour `QuotaUsageService`.

### AC 4 — Tests unitaires des garde-fous

11. [x] `backend/app/tests/unit/test_quota_usage_service.py` est complété avec :
    - `test_quota_usage_service_rejects_b2b_feature_on_get_usage` : `QuotaUsageService.get_usage(..., feature_code="b2b_api_access")` → lève `InvalidQuotaScopeError`.
    - `test_quota_usage_service_rejects_b2b_feature_on_consume` : `QuotaUsageService.consume(..., feature_code="b2b_api_access")` → lève `InvalidQuotaScopeError`.
    - `test_quota_usage_service_rejects_unknown_feature_code` : `QuotaUsageService.get_usage(..., feature_code="unregistered_feature")` → lève `UnknownFeatureCodeError` (fail-closed — code non enregistré bloqué).

12. [x] `backend/app/tests/unit/test_enterprise_quota_usage_service.py` est complété avec :
    - `test_enterprise_quota_usage_service_rejects_b2c_feature_on_get_usage` : `EnterpriseQuotaUsageService.get_usage(..., feature_code="astrologer_chat")` → lève `InvalidQuotaScopeError`.
    - `test_enterprise_quota_usage_service_rejects_b2c_feature_on_consume` : `EnterpriseQuotaUsageService.consume(..., feature_code="thematic_consultation")` → lève `InvalidQuotaScopeError`.
    - `test_enterprise_quota_usage_service_rejects_unknown_feature_code` : `EnterpriseQuotaUsageService.get_usage(..., feature_code="unregistered_feature")` → lève `UnknownFeatureCodeError` (fail-closed).

13. [x] `backend/app/tests/unit/test_feature_scope_registry.py` est créé avec :
    - `test_known_b2c_feature_codes` : vérifie que `astrologer_chat`, `thematic_consultation`, `natal_chart_long` retournent `FeatureScope.B2C`.
    - `test_known_b2b_feature_codes` : vérifie que `b2b_api_access` retournent `FeatureScope.B2B`.
    - `test_unknown_feature_code_raises` : `get_feature_scope("unknown_code")` → lève `UnknownFeatureCodeError`.
    - `test_invalid_scope_error_message_b2b` : vérifie que `InvalidQuotaScopeError` levée pour `b2b_api_access` dans `QuotaUsageService` contient la mention `"EnterpriseQuotaUsageService"` dans son message.

### AC 5 — Non-régression structurelle (test de séparation des imports)

14. [x] Un test `backend/app/tests/unit/test_scope_separation_imports.py` est créé. Il vérifie statiquement (par import inspection) que :
    - `B2BApiEntitlementGate` **n'importe pas** `QuotaUsageService`.
    - `B2BCanonicalUsageSummaryService` **n'importe pas** `QuotaUsageService`.
    - `B2BBillingService` **n'importe pas** `QuotaUsageService`.
    - `B2BReconciliationService` **n'importe pas** `QuotaUsageService`.
    - `ChatEntitlementGate` **n'importe pas** `EnterpriseQuotaUsageService`.
    - `ThematicConsultationEntitlementGate` **n'importe pas** `EnterpriseQuotaUsageService`.
    - `NatalChartLongEntitlementGate` **n'importe pas** `EnterpriseQuotaUsageService`.
    - Technique : parser le fichier source avec le module `ast` et inspecter les nœuds `Import` et `ImportFrom` — fiable, insensible aux commentaires/docstrings et aux alias d'import.

### AC 6 — Documentation mise à jour

15. [x] `backend/docs/entitlements-canonical-platform.md` est mis à jour avec une section **"Séparation stricte B2C/B2B — Règle structurelle post-61.27"** qui documente :
    - `feature_usage_counters` = B2C-only, géré par `QuotaUsageService`.
    - `enterprise_feature_usage_counters` = B2B-only, géré par `EnterpriseQuotaUsageService`.
    - `FEATURE_SCOPE_REGISTRY` dans `feature_scope_registry.py` est la source unique de vérité pour le scope de chaque **feature code soumis aux services de quota** (pas toutes les features produit).
    - Tout `feature_code` non enregistré provoque une erreur immédiate (`UnknownFeatureCodeError`) — comportement fail-closed.
    - En violation de scope → `InvalidQuotaScopeError` levée immédiatement, avant toute DB.
    - Invariant post-61.27 : aucune lecture/écriture B2B dans `feature_usage_counters`, aucune B2C dans `enterprise_feature_usage_counters`.

## Tasks / Subtasks

- [x] **Créer `feature_scope_registry.py`** (AC: 1)
  - [x] Définir `FeatureScope` enum avec `B2C` et `B2B`
  - [x] Définir `FEATURE_SCOPE_REGISTRY` avec les 4 feature codes connus
  - [x] Définir `get_feature_scope(feature_code: str) -> FeatureScope`
  - [x] Définir `UnknownFeatureCodeError(ValueError)` avec message clair
  - [x] Définir `InvalidQuotaScopeError(ValueError)` avec attributs `feature_code`, `expected_scope`, `actual_scope` et message explicite mentionnant le service à utiliser

- [x] **Ajouter garde-fou dans `QuotaUsageService`** (AC: 2)
  - [x] Importer `get_feature_scope`, `FeatureScope`, `InvalidQuotaScopeError` depuis `feature_scope_registry` (pas besoin d'importer `UnknownFeatureCodeError` — elle se propage sans être catchée)
  - [x] Ajouter la validation en début de `get_usage()` : appel `get_feature_scope()` sans try/except ; si scope == B2B → lever `InvalidQuotaScopeError`
  - [x] Ajouter la validation en début de `consume()` : même pattern

- [x] **Ajouter garde-fou dans `EnterpriseQuotaUsageService`** (AC: 3)
  - [x] Importer `get_feature_scope`, `FeatureScope`, `InvalidQuotaScopeError` depuis `feature_scope_registry`
  - [x] Ajouter la validation en début de `get_usage()` : appel `get_feature_scope()` sans try/except ; si scope == B2C → lever `InvalidQuotaScopeError`
  - [x] Ajouter la validation en début de `consume()` : même pattern

- [x] **Créer `test_feature_scope_registry.py`** (AC: 4, sous-tâche 13)
  - [x] `test_known_b2c_feature_codes`
  - [x] `test_known_b2b_feature_codes`
  - [x] `test_unknown_feature_code_raises`
  - [x] `test_invalid_scope_error_message_b2b`

- [x] **Compléter `test_quota_usage_service.py`** (AC: 4, sous-tâche 11)
  - [x] `test_quota_usage_service_rejects_b2b_feature_on_get_usage`
  - [x] `test_quota_usage_service_rejects_b2b_feature_on_consume`
  - [x] `test_quota_usage_service_rejects_unknown_feature_code` (fail-closed)

- [x] **Compléter `test_enterprise_quota_usage_service.py`** (AC: 4, sous-tâche 12)
  - [x] `test_enterprise_quota_usage_service_rejects_b2c_feature_on_get_usage`
  - [x] `test_enterprise_quota_usage_service_rejects_b2c_feature_on_consume`
  - [x] `test_enterprise_quota_usage_service_rejects_unknown_feature_code` (fail-closed)

- [x] **Créer `test_scope_separation_imports.py`** (AC: 5)
  - [x] Vérifier que les services B2B n'importent pas `QuotaUsageService`
  - [x] Vérifier que les services B2C n'importent pas `EnterpriseQuotaUsageService`
  - [x] Technique : parser les fichiers source avec `ast` et inspecter les nœuds `Import` / `ImportFrom`

- [x] **Mettre à jour la documentation** (AC: 6)
  - [x] Ajouter section "Séparation stricte B2C/B2B — Règle structurelle post-61.27" dans `entitlements-canonical-platform.md`
  - [x] Mettre à jour table des invariants

- [x] **Validation finale**
  - [x] `ruff check` sur tous les fichiers modifiés/créés
  - [x] Suite pytest complète B2B + B2C + scope registry

## Dev Notes

... (unchanged)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Linting errors (E501, I001, F401) fixed via `ruff check --fix` and manual wrapping.
- `ModuleNotFoundError` in `test_scope_separation_imports.py` fixed by correcting module name `app.services.b2b_canonical_usage_service`.

### Completion Notes List

- Created `feature_scope_registry.py` with `FeatureScope` enum and `FEATURE_SCOPE_REGISTRY`.
- Updated `QuotaUsageService` and `EnterpriseQuotaUsageService` with runtime scope validation.
- Added comprehensive unit tests in `test_feature_scope_registry.py`, `test_quota_usage_service.py`, and `test_enterprise_quota_usage_service.py`.
- Implemented AST-based import separation check in `test_scope_separation_imports.py`.
- Updated documentation in `entitlements-canonical-platform.md`.
- All tests passing (37 tests).

### File List

- `backend/app/services/feature_scope_registry.py`
- `backend/app/services/quota_usage_service.py`
- `backend/app/services/enterprise_quota_usage_service.py`
- `backend/app/tests/unit/test_feature_scope_registry.py`
- `backend/app/tests/unit/test_quota_usage_service.py`
- `backend/app/tests/unit/test_enterprise_quota_usage_service.py`
- `backend/app/tests/unit/test_scope_separation_imports.py`
- `backend/docs/entitlements-canonical-platform.md`

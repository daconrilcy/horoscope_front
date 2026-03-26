# Story 61.13 : Migration de natal_chart_long vers les entitlements canoniques

Status: done

## Story

En tant qu'utilisateur B2C authentifié,
je veux que mon accès à l'interprétation complète du thème natal soit gouverné exclusivement par le moteur d'entitlements canonique,
de sorte que mon quota d'interprétations soit réellement consommé, que les refus soient clairs et que le front puisse afficher le variant astrologue disponible (single ou multi) et mon quota restant.

## Acceptance Criteria

1. [x] `POST /v1/natal/interpretation` avec `use_case_level="complete"` est refusé (HTTP 403) si `final_access=False` avec `reason` parmi : `no_plan`, `billing_inactive`, `canonical_no_binding`, `feature_unknown`
2. [x] La requête est refusée (HTTP 403) si le binding `natal_chart_long` est désactivé (`reason="disabled_by_plan"`) — par exemple pour le plan free
3. [x] La requête est refusée (HTTP 429) si `final_access=False` avec `quota_exhausted=True` — le quota lifetime d'interprétations est épuisé
4. [x] Un chemin canonique `access_mode=quota` consomme exactement 1 unité dans `feature_usage_counters` avant d'appeler `NatalInterpretationServiceV2.interpret()`
5. [x] Un chemin canonique `access_mode=unlimited` n'effectue aucune consommation dans `feature_usage_counters`
6. [x] La `variant_code` retournée par l'entitlement (`"single_astrologer"` ou `"multi_astrologer"`) est incluse dans la réponse du endpoint sous `entitlement_info.variant_code`
7. [x] La réponse de `POST /v1/natal/interpretation` pour `use_case_level="complete"` inclut un objet `entitlement_info` avec les champs `remaining`, `limit`, `window_end` (null pour les quotas lifetime), `variant_code`
8. [x] `POST /v1/natal/interpretation` avec `use_case_level="short"` n'est PAS soumis au gate `natal_chart_long` — aucune consommation de quota, `entitlement_info=null` dans la réponse
9. [x] Aucun appel à `QuotaService` legacy n'est effectué pour `natal_chart_long` — gouverné uniquement par le canonique
10. [x] En cas d'exception `NatalChartLongAccessDeniedError` ou `NatalChartLongQuotaExceededError`, le routeur appelle `db.rollback()` avant de retourner la `JSONResponse`
11. [x] Les tests existants de `test_natal_interpretation_endpoint.py` continuent de passer
12. [x] Si aucun binding canonique n'existe pour `natal_chart_long` → refus 403 avec `reason="canonical_no_binding"` (pas de fallback legacy)
13. [x] Les tests d'intégration couvrent les fenêtres lifetime :
    - trial (idem basic, configs identiques) : 1ère interprétation complète ok ; 2ème refusée en 429
    - premium : 5ème interprétation ok ; 6ème refusée en 429
14. [x] Un appel `POST /v1/natal/interpretation` avec `use_case_level="complete"` consomme 1 unité **même si** `NatalInterpretationServiceV2.interpret()` retourne un résultat déjà existant ou mis en cache (`force_refresh=False`). `POST /interpretation` est une opération de génération ; pour lire une interprétation sans consommer, utiliser `GET /v1/natal/interpretations/{id}`

## Tasks / Subtasks

- [x] **Créer `NatalChartLongEntitlementGate`** dans `backend/app/services/natal_chart_long_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6, 9, 12)
  - [x] Définir `FEATURE_CODE = "natal_chart_long"` comme constante de classe
  - [x] Définir `NatalChartLongAccessDeniedError(Exception)` avec attributs `reason: str`, `billing_status: str`, `plan_code: str`
  - [x] Définir `NatalChartLongQuotaExceededError(Exception)` avec attributs `quota_key: str`, `used: int`, `limit: int`, `window_end: datetime | None`
  - [x] Définir `NatalChartLongEntitlementResult` dataclass avec : `path: str` (`"canonical_quota"` | `"canonical_unlimited"`), `variant_code: str | None`, `usage_states: list[UsageState]`
  - [x] Implémenter `check_and_consume(db, *, user_id) → NatalChartLongEntitlementResult` (méthode statique) — **respecter cet ordre strict** :
    - [x] Appeler `EntitlementService.get_feature_entitlement(db, user_id=user_id, feature_code=FEATURE_CODE)`
    - [x] **Pas de chemin legacy_fallback** — si `entitlement.reason == "legacy_fallback"` → lever `NatalChartLongAccessDeniedError(reason="canonical_no_binding", ...)` (AC: 12)
    - [x] Si `entitlement.final_access=False` et `entitlement.quota_exhausted=True` → lever `NatalChartLongQuotaExceededError` avec infos du premier quota épuisé dans `usage_states` (AC: 3)
    - [x] Si `entitlement.final_access=False` → lever `NatalChartLongAccessDeniedError(reason=entitlement.reason, ...)` (AC: 1, 2)
    - [x] Si `entitlement.access_mode == "unlimited"` → retourner `NatalChartLongEntitlementResult(path="canonical_unlimited", variant_code=entitlement.variant_code, usage_states=entitlement.usage_states)` (AC: 5)
    - [x] Si `entitlement.access_mode == "quota"` → pour chaque quota dans `entitlement.quotas` : appeler `QuotaUsageService.consume(db, user_id=user_id, feature_code=FEATURE_CODE, quota=quota, amount=1)` ; propager `QuotaExhaustedError` comme `NatalChartLongQuotaExceededError` avec `window_end=None` (AC: 4, car lifetime)
    - [x] Retourner `NatalChartLongEntitlementResult(path="canonical_quota", variant_code=entitlement.variant_code, usage_states=[...states post-consommation])`

- [x] **Modifier `backend/app/api/v1/schemas/natal_interpretation.py`** (AC: 7)
  - [x] Ajouter `NatalChartLongEntitlementInfo` Pydantic model : `remaining: int | None = None`, `limit: int | None = None`, `window_end: datetime | None = None`, `variant_code: str | None = None`
  - [x] Ajouter `entitlement_info: NatalChartLongEntitlementInfo | None = None` à `NatalInterpretationResponse`

- [x] **Modifier `backend/app/api/v1/routers/natal_interpretation.py`** (AC: 1, 2, 3, 4, 5, 7, 8, 10)
  - [x] Importer `NatalChartLongEntitlementGate`, `NatalChartLongAccessDeniedError`, `NatalChartLongQuotaExceededError`, `NatalChartLongEntitlementResult` depuis `app.services.natal_chart_long_entitlement_gate`
  - [x] Importer `NatalChartLongEntitlementInfo` depuis les schémas
  - [x] Ajouter helper `_build_natal_entitlement_info(result: NatalChartLongEntitlementResult) -> NatalChartLongEntitlementInfo`
  - [x] Dans `interpret_natal_chart`, **avant** l'appel à `NatalInterpretationServiceV2.interpret()`, et **uniquement si `body.use_case_level == "complete"`** :
    - Appeler `NatalChartLongEntitlementGate.check_and_consume(db, user_id=current_user.id)`
    - Construire `entitlement_info` depuis le résultat
    - Gérer `NatalChartLongQuotaExceededError` → HTTP 429 avec `db.rollback()`
    - Gérer `NatalChartLongAccessDeniedError` → HTTP 403 avec `db.rollback()`
  - [x] Pour `use_case_level="short"` : `entitlement_info` reste `None` (pas de gate)
  - [x] Modifier le `return response` final pour setter `response.entitlement_info = entitlement_info`
  - [x] Ajouter `403` et `429` aux `responses={}` du décorateur `@router.post("/interpretation")`

- [x] **Tests unitaires `NatalChartLongEntitlementGate`** dans `backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py` (AC: 1, 2, 3, 4, 5, 6, 9, 12)
  - [x] `test_canonical_quota_path_consumes` : binding quota canonique → `path="canonical_quota"`, `consume()` appelé 1 fois, `variant_code` correct
  - [x] `test_canonical_unlimited_path_no_consume` : binding unlimited → `path="canonical_unlimited"`, `consume()` non appelé
  - [x] `test_variant_code_single_astrologer` : binding avec `variant_code="single_astrologer"` → `result.variant_code == "single_astrologer"`
  - [x] `test_variant_code_multi_astrologer` : binding avec `variant_code="multi_astrologer"` → `result.variant_code == "multi_astrologer"`
  - [x] `test_legacy_fallback_treated_as_no_binding` : `reason="legacy_fallback"` → `NatalChartLongAccessDeniedError(reason="canonical_no_binding")` (AC: 12)
  - [x] `test_access_denied_no_plan` : `final_access=False, reason="no_plan"` → `NatalChartLongAccessDeniedError`
  - [x] `test_access_denied_disabled_by_plan` : `final_access=False, reason="disabled_by_plan"` → `NatalChartLongAccessDeniedError` (plan free)
  - [x] `test_quota_exceeded_raises_natal_error` : quota épuisé → `NatalChartLongQuotaExceededError` avec `window_end=None` (lifetime)
  - [x] `test_no_legacy_quota_service_called` : vérifier qu'aucun appel à `QuotaService` legacy
  - [x] Utiliser des mocks pour `EntitlementService.get_feature_entitlement` et `QuotaUsageService.consume` — PAS de vraie DB

- [x] **Tests d'intégration endpoint `POST /v1/natal/interpretation`** dans `backend/app/tests/integration/test_natal_chart_long_entitlement.py` (AC: 1, 2, 3, 4, 6, 7, 8, 10, 13)
  - [x] `test_complete_canonical_quota_ok` : binding quota 1/lifetime → 200, `entitlement_info.remaining=0`, `entitlement_info.variant_code="single_astrologer"`
  - [x] `test_complete_canonical_unlimited_ok` : binding unlimited → 200, `entitlement_info.remaining=None`
  - [x] `test_complete_no_plan_rejected` : user sans plan → 403, `code="natal_chart_long_access_denied"`
  - [x] `test_complete_quota_exhausted_rejected` : compteur épuisé → 429, `code="natal_chart_long_quota_exceeded"`, `details.window_end=null` (lifetime)
  - [x] `test_complete_disabled_binding_returns_disabled_by_plan` : plan free → 403, `details.reason="disabled_by_plan"`
  - [x] `test_complete_no_canonical_binding_returns_no_binding` : `reason="canonical_no_binding"` → 403 (AC: 12)
  - [x] `test_short_level_bypasses_gate` : `use_case_level="short"` → 200 sans appel au gate, `entitlement_info=null` (AC: 8)
  - [x] `test_complete_rolls_back_on_access_denied` : gate lève access denied → rollback appelé (AC: 10)
  - [x] `test_trial_quota_1_per_lifetime` : user trial, 1ère interprétation ok, 2ème refusée 429 (AC: 13) — `trial` et `basic` sont identiques sur ce quota ; tester `trial` suffit, inutile de dupliquer pour `basic`
  - [x] `test_premium_quota_5_per_lifetime` : user premium, 5 interprétations ok, 6ème refusée 429 (AC: 13)
  - [x] `test_variant_code_in_response` : premium → `entitlement_info.variant_code="multi_astrologer"` ; trial → `"single_astrologer"`

- [x] **Non-régression** (AC: 11)
  - [x] `pytest backend/app/tests/integration/test_natal_interpretation_endpoint.py` — tous verts
  - [x] `pytest backend/app/tests/integration/test_natal_interpretations_history.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_entitlement_service.py` — tous verts
  - [x] `pytest backend/app/tests/unit/test_quota_usage_service.py` — tous verts

---

## Dev Notes

... (rest of notes)

---

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- [2026-03-26] Implementation started.
- [2026-03-26] All tests passed. Code review performed. Fixed quota integrity in router.

### Completion Notes List

- Migrated `natal_chart_long` to canonical entitlements.
- Created `NatalChartLongEntitlementGate`.
- Updated schemas and router.
- Added comprehensive unit and integration tests.
- Verified non-regression.

### File List

- `backend/app/services/natal_chart_long_entitlement_gate.py`
- `backend/app/api/v1/schemas/natal_interpretation.py`
- `backend/app/api/v1/routers/natal_interpretation.py`
- `backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py`
- `backend/app/tests/integration/test_natal_chart_long_entitlement.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`

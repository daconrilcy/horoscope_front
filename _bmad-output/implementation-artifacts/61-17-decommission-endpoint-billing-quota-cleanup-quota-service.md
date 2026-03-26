# Story 61.17 : Décommission de GET /v1/billing/quota et nettoyage du module QuotaService

Status: done

## Story

En tant que développeur de la plateforme,
je veux supprimer l'endpoint legacy `GET /v1/billing/quota`, retirer le module `quota_service.py` et renommer les helpers frontend à noms obsolètes,
de sorte que l'API publique ne contienne plus d'endpoint mort, que le module `QuotaService` n'existe plus dans le codebase, et que les noms de fonctions frontend reflètent leur implémentation réelle.

## Acceptance Criteria

1. [x] L'endpoint `GET /v1/billing/quota` est supprimé de `billing.py` ; tout appel à cet endpoint retourne HTTP 404 (Not Found).
2. [x] Les classes de réponse `QuotaApiResponse` et `QuotaStatusData` sont supprimées de `billing.py`.
3. [x] Le fichier `backend/app/services/quota_service.py` est supprimé.
4. [x] Aucun import de `QuotaService` ou appel à ses méthodes ne subsiste dans le code backend de production.
5. [x] Les helpers frontend `useBillingQuota` et `fetchQuotaStatus` (dans `billing.ts`) sont renommés respectivement en `useChatEntitlementUsage` et `fetchChatEntitlementUsage`.
6. [x] Tous les composants frontend (`BillingPanel.tsx`, `ChatPage.tsx`, `UsageSettings.tsx`, etc.) et leurs tests utilisent désormais les nouveaux noms.
7. [x] Le fichier `backend/docs/entitlements-canonical-platform.md` est mis à jour pour acter la décommission.
8. [x] Tous les tests d'intégration backend impactés (billing, chat, load, secrets) sont mis à jour pour vérifier l'état via `GET /v1/entitlements/me` et passent avec succès.

## Technical Tasks

### Backend - Suppression Endpoint et Service
- [x] **Audit Final QuotaService**
  - [x] Grep backend (tout le repo) : `"quota_service"`, `"QuotaService"`, `"QuotaStatusData"`, `"QuotaServiceError"`, `"QuotaApiResponse"` — y compris `__init__.py`, `conftest.py`, scripts, snapshots OpenAPI, docs markdown
- [x] **Supprimer `GET /v1/billing/quota`** (AC: 1)
  - [x] Retirer le handler `get_quota_status` de `backend/app/api/v1/routers/billing.py`
  - [x] Supprimer l'import ligne 31 : `from app.services.quota_service import QuotaService, QuotaServiceError, QuotaStatusData`
- [x] **Supprimer `QuotaApiResponse` et `QuotaStatusData`** (AC: 2)
  - [x] Supprimer les définitions de modèles liées dans `billing.py`
- [x] **Supprimer `quota_service.py`** (AC: 2)
  - [x] Supprimer `backend/app/services/quota_service.py` en entier
  - [x] Grep de sécurité : `grep -r "quota_service\|QuotaService" backend/app/` pour s'assurer qu'aucun import de production ne subsiste
- [x] **Supprimer `test_quota_service.py`** (AC: 3)
  - [x] Supprimer `backend/app/tests/unit/test_quota_service.py` en entier

### Backend - Nettoyage Tests et Guards
- [x] **Mettre à jour les tests d'intégration** (AC: 8)
  - [x] `test_billing_api.py` : remplacer les appels legacy par `/v1/entitlements/me`
  - [x] `test_chat_api.py` : remplacer les appels legacy par `/v1/entitlements/me`
  - [x] `test_load_smoke_critical_flows.py` : rerouter le test de charge billing vers `/v1/entitlements/me`
  - [x] `test_secret_rotation_critical_flows.py` : vérifier la continuité via `/v1/entitlements/me`
- [x] **Supprimer les guards "QuotaService jamais appelé"** (AC: 5)
  - [x] `test_chat_entitlement.py` : supprimer `test_send_message_quota_service_never_called` (l. 214) et la référence `QuotaService.consume_quota_or_raise` (l. 257)
  - [x] `test_natal_chart_long_entitlement_gate.py` : supprimer `test_no_legacy_quota_service_called` (l. 161)
  - [x] `test_thematic_consultation_entitlement_gate.py` : supprimer `test_no_legacy_quota_service_called` (l. 154)

### Frontend - Refactor Renommage
- [x] **Renommer les helpers frontend** (AC: 5)
  - [x] Dans `frontend/src/api/billing.ts` :
    - `useBillingQuota` -> `useChatEntitlementUsage`
    - `fetchQuotaStatus` -> `fetchChatEntitlementUsage`
    - `BillingQuotaStatus` -> `ChatEntitlementUsageStatus`
    - `queryKey: ["billing-quota"]` -> `["chat-entitlement-usage"]`
- [x] **Mettre à jour les consumers frontend** (AC: 6)
  - [x] `BillingPanel.tsx`
  - [x] `ChatPage.tsx`
  - [x] `UsageSettings.tsx`
  - [x] `SubscriptionSettings.tsx` (invalidations React Query)
- [x] **Mettre à jour les tests frontend**
  - [x] `BillingPanel.test.tsx`
  - [x] `ChatPage.test.tsx`

### Documentation
- [x] **Mettre à jour la documentation** (AC: 7)
  - [x] `backend/docs/entitlements-canonical-platform.md`
    - Marquer la décommission comme terminée (61.17)
    - Indiquer que `quota_service.py` est supprimé — tout nouveau code de comptage doit utiliser `QuotaUsageService` + `feature_usage_counters`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List
- Decommission complète de `QuotaService` et de l'endpoint `/v1/billing/quota`.
- Migration de tous les tests d'intégration backend vers le système canonique d'entitlements.
- Seeding systématique des plans canoniques dans les `_cleanup_tables` des tests d'intégration pour garantir le passage des gates.
- Refactor complet du frontend pour utiliser les nouveaux noms de types et helpers.
- Vérification par `ruff` et passage de 84 tests d'intégration backend et 24 tests frontend vitest.
- Revue BMAD effectuée après implémentation: correction du contrat TypeScript `billing.ts`, du flux `BillingPanel`, suppression des styles inline restants dans `SubscriptionSettings`, et ajout d'un test explicite de retour `404` sur `GET /v1/billing/quota`.

### File List
- backend/app/api/v1/routers/billing.py
- backend/app/services/quota_service.py (SUPPRIMÉ)
- backend/app/tests/unit/test_quota_service.py (SUPPRIMÉ)
- backend/app/tests/integration/test_billing_api.py
- backend/app/tests/integration/test_chat_api.py
- backend/app/tests/integration/test_chat_entitlement.py
- backend/app/tests/integration/test_guidance_api.py
- backend/app/tests/integration/test_load_smoke_critical_flows.py
- backend/app/tests/integration/test_ops_monitoring_api.py
- backend/app/tests/integration/test_secret_rotation_critical_flows.py
- backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py
- backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py
- backend/docs/entitlements-canonical-platform.md
- frontend/src/api/billing.ts
- frontend/src/components/BillingPanel.tsx
- frontend/src/pages/ChatPage.tsx
- frontend/src/pages/settings/Settings.css
- frontend/src/pages/settings/SubscriptionSettings.tsx
- frontend/src/pages/settings/UsageSettings.tsx
- frontend/src/tests/App.test.tsx
- frontend/src/tests/AppShell.test.tsx
- frontend/src/tests/BillingPanel.test.tsx
- frontend/src/tests/ChatPage.test.tsx
- frontend/src/tests/SettingsPage.test.tsx
- frontend/src/tests/router.test.tsx

## Senior Developer Review (AI)

### Findings
- HIGH: `frontend/src/api/billing.ts` avait dérivé du contrat backend réel (`/v1/billing/subscription`, `/v1/billing/checkout`, `/v1/billing/plan-change`) avec des types incompatibles et un import invalide de `getAccessTokenAuthHeader`, ce qui cassait la vérification TypeScript sur le périmètre billing.
- MEDIUM: `frontend/src/components/BillingPanel.tsx` utilisait des payloads et champs de réponse qui n'existent pas (`checkoutId`, `payment_failure_reason`, `last_failed_checkout_id`), ce qui rendait le flux de retry et de changement de plan incohérent avec l'API réelle.
- MEDIUM: l'AC1 n'était pas vérifié explicitement par un test de régression dédié sur le `404` de `GET /v1/billing/quota`.
- MEDIUM: la `File List` de la story était incomplète par rapport au delta réel du commit.

### Fixes Applied
- Contrat billing frontend réaligné sur les DTO backend et helper renommé conservé (`useChatEntitlementUsage`).
- `BillingPanel` corrigé pour utiliser les vrais payloads de checkout/retry/plan-change.
- `SubscriptionSettings` nettoyé pour supprimer les styles inline restants du périmètre touché.
- Test backend ajouté pour valider le `404` sur `/v1/billing/quota`.
- `File List` synchronisée avec les fichiers réellement modifiés autour de la story.

### Validation
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_billing_api.py`
- `npx vitest run src/tests/BillingPanel.test.tsx src/tests/ChatPage.test.tsx src/tests/SettingsPage.test.tsx src/tests/App.test.tsx src/tests/AppShell.test.tsx src/tests/router.test.tsx`

## Change Log

- 2026-03-26: revue BMAD 61-17 exécutée, issues frontend/backend corrigées, couverture de régression `404` ajoutée, artefact de story synchronisé.

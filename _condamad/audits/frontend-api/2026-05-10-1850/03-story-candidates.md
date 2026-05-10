# Story Candidates - frontend-api - 2026-05-10-1850

## SC-001 - Converger le transport HTTP frontend

- Candidate ID: SC-001
- Source finding: F-001
- Source finding ID: F-001
- Suggested story title: Converger les appels backend frontend sous le client HTTP canonique
- Suggested archetype: frontend-api-transport-convergence
- Primary domain: frontend-api
- Required contracts: No Legacy / DRY Audit Contract
- Draft objective: remplacer les appels backend `fetch` directs par un helper central conserveur de `apiFetch`, timeout et gestion `token_expired`.
- Closure intent: full-closure
- Must include: preserve or explicitly reimplement the geocoding-specific 15s timeout; migrate `b2bAstrology.ts`, `b2bBilling.ts`, `b2bEditorial.ts`, `b2bUsage.ts`, `billing.ts`, `enterpriseCredentials.ts`, `help.ts`, `opsMonitoring.ts`, `support.ts`, and backend proxy calls in `geocoding.ts`; preserve request paths and headers.
- Validation hints: `npm run lint`; `npm run test -- apiClient b2b billing help support geocodingApi`; scan `rg -n "\bfetch\(" frontend/src/api` must show only `client.ts` plus explicitly documented exceptions, or zero exceptions if the transport helper supports custom timeout/signals.
- Blockers: none for backend HTTP calls; geocoding timeout behavior must be retained or covered by tests before migration.

### Exhaustive Files To Modify

- `frontend/src/api/client.ts`
- `frontend/src/api/b2bAstrology.ts`
- `frontend/src/api/b2bBilling.ts`
- `frontend/src/api/b2bEditorial.ts`
- `frontend/src/api/b2bUsage.ts`
- `frontend/src/api/billing.ts`
- `frontend/src/api/enterpriseCredentials.ts`
- `frontend/src/api/help.ts`
- `frontend/src/api/opsMonitoring.ts`
- `frontend/src/api/support.ts`
- `frontend/src/api/geocoding.ts`

## SC-002 - Centraliser les enveloppes et erreurs API

- Candidate ID: SC-002
- Source finding: F-002
- Source finding ID: F-002
- Suggested story title: Ajouter un helper partagé pour enveloppes et erreurs API frontend
- Suggested archetype: api-error-contract-centralization
- Primary domain: frontend-api
- Required contracts: No Legacy / DRY Audit Contract
- Draft objective: créer un owner unique pour `ErrorEnvelope`, `ResponseEnvelope`, parsing JSON d'erreur et conversion transport, puis migrer les modules API.
- Closure intent: phased-with-map
- Must include: phase 1 shared helper plus admin/support/B2B; phase 2 prediction/natal/chat/billing/hooks; stop when `rg -l 'ErrorEnvelope|ResponseEnvelope|parseError|toTransportError|extractAdminApiErrorMessage|throw new Error' frontend/src/api -g '*.ts'` shows no duplicated local envelope/parser except typed wrappers backed by the helper.
- Validation hints: `npm run lint`; `npm run test -- adminPromptsApi b2b Reconciliation privacy guidance chat natalChartApi`.
- Blockers: decide whether typed domain-specific `*ApiError` classes remain public API or converge to `ApiError`.

### Exhaustive Files To Modify

- `frontend/src/api/client.ts` or new `frontend/src/api/core/errors.ts`
- `frontend/src/api/adminContent.ts`
- `frontend/src/api/adminDashboard.ts`
- `frontend/src/api/adminLogs.ts`
- `frontend/src/api/adminOperations.ts`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/api/adminUsers.ts`
- `frontend/src/api/astrologers.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/api/authMe.ts`
- `frontend/src/api/b2bAstrology.ts`
- `frontend/src/api/b2bBilling.ts`
- `frontend/src/api/b2bEditorial.ts`
- `frontend/src/api/b2bReconciliation.ts`
- `frontend/src/api/b2bUsage.ts`
- `frontend/src/api/billing.ts`
- `frontend/src/api/chat.ts`
- `frontend/src/api/dailyPrediction.ts`
- `frontend/src/api/enterpriseCredentials.ts`
- `frontend/src/api/guidance.ts`
- `frontend/src/api/help.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/api/opsMonitoring.ts`
- `frontend/src/api/opsPersona.ts`
- `frontend/src/api/privacy.ts`
- `frontend/src/api/support.ts`
- `frontend/src/api/useBirthData.ts`
- `frontend/src/api/userSettings.ts`

## SC-003 - Découper les modules API volumineux par domaine

- Candidate ID: SC-003
- Source finding: F-003
- Source finding ID: F-003
- Suggested story title: Structurer `adminPrompts` et `natalChart` en sous-dossiers API de domaine
- Suggested archetype: namespace-convergence
- Primary domain: frontend-api
- Required contracts: No Legacy / DRY Audit Contract
- Draft objective: extraire types, requêtes, hooks et effets navigateur dans des fichiers dédiés sans changer les imports publics.
- Closure intent: full-closure
- Must include: preserve `@api` exports during migration or provide codemod/import update; no compatibility re-export beyond the chosen public entrypoint.
- Validation hints: `npm run lint`; `npm run test -- AdminPromptsPage adminPromptsApi natalChartApi NatalChartPage natalInterpretation`.
- Blockers: public facade policy from F-006 may alter final path names.

### Exhaustive Files To Modify

- `frontend/src/api/adminPrompts.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/api/index.ts`
- New domain files under `frontend/src/api/admin-prompts/**` and `frontend/src/api/natal-chart/**`, if approved.

## SC-004 - Ajouter une garde d'import API interne

- Candidate ID: SC-004
- Source finding: F-004
- Source finding ID: F-004
- Suggested story title: Interdire les imports `@api` depuis `frontend/src/api`
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-api
- Required contracts: dependency-direction-audit
- Draft objective: remplacer l'import `ApiError` de `useDailyPrediction.ts` par `./client` et ajouter un test/scan empêchant les imports barrel dans le domaine API.
- Closure intent: full-closure
- Must include: no wildcard allowlist; exact scan under `frontend/src/api`; preserve external consumer imports.
- Validation hints: `npm run lint`; scan `rg -n 'from [''\""]@api' frontend/src/api` must return zero.
- Blockers: none.

### Exhaustive Files To Modify

- `frontend/src/api/useDailyPrediction.ts`
- guard test file selected by existing architecture test convention

## SC-005 - Clarifier ownership support versus ops

- Candidate ID: SC-005
- Source finding: F-005
- Source finding ID: F-005
- Suggested story title: Retirer la composition ops persona du client support
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-api
- Required contracts: No Legacy / DRY Audit Contract
- Draft objective: arrêter d'exposer `useOpsRollbackPersona` depuis `support.ts` et faire importer le panneau support depuis le propriétaire canonique ou une composition feature.
- Closure intent: full-closure
- Must include: classification du endpoint `/v1/support/users/context?email=...`; suppression du commentaire placeholder ou remplacement par contrat explicite.
- Validation hints: `npm run lint`; `npm run test -- SupportOpsPanel opsPersona`.
- Blockers: confirm backend contract and product ownership for support search-by-email.

### Exhaustive Files To Modify

- `frontend/src/api/support.ts`
- `frontend/src/features/support/SupportOpsPanel.tsx`
- tests support/ops related

## SC-006 - Décider la politique de façade publique `@api`

- Candidate ID: SC-006
- Source finding: F-006
- Source finding ID: F-006
- Suggested story title: Définir la structure cible de `frontend/src/api` par domaines
- Suggested archetype: blocked
- Primary domain: frontend-api
- Required contracts: No Legacy / DRY Audit Contract
- Draft objective: choisir entre barrel public global conservé, entrypoints par domaine, ou imports directs seulement.
- Closure intent: blocked
- Must include: classify B2B/Ops modules as runtime-owned, test-only, public-export-only, or delete-candidate after decision.
- Validation hints: source-level import inventory before/after; `npm run lint`; targeted tests for moved modules.
- Blockers: architecture decision required before deletion or public export changes.

### Exhaustive Files To Modify

- none until user decision

## Deferred Non-Domain Context

- Backend endpoint contract verification for support search and B2B/Ops availability belongs to backend API/runtime contract audit, not this frontend API audit.

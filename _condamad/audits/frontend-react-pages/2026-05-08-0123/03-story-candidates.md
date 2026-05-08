<!-- Candidats stories issus de l'audit CONDAMAD des pages React du frontend. -->

# Story Candidates - frontend-react-pages

## Exhaustive Files To Modify

The exact implementation scope should be finalized by `condamad-story-writer`, but the audit evidence points to these candidate surfaces.

Likely application files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/admin/AdminPromptEditorPanel.tsx`
- `frontend/src/pages/admin/AdminPromptsLogicGraph.tsx`
- `frontend/src/pages/admin/AdminPromptCatalogNodeModal.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/PersonasAdmin.tsx`
- `frontend/src/pages/admin/AdminDashboardPage.tsx`
- `frontend/src/pages/admin/AdminLogsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminUserDetailPage.tsx`
- `frontend/src/pages/admin/AdminUsersPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/index.ts`
- `frontend/src/pages/index.ts`
- `frontend/src/app/routes.tsx`

Likely new or changed canonical owners:

- `frontend/src/features/admin-prompts/**`
- `frontend/src/features/admin/**`
- `frontend/src/api/admin*.ts` or narrower `frontend/src/api/adminDashboard.ts`, `adminLogs.ts`, `adminUsers.ts`, etc.
- `frontend/src/utils/formatters.ts` or feature-scoped formatter modules.
- `frontend/src/tests/page-architecture-guards.test.ts` or equivalent.

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Extraire le domaine feature `admin-prompts` hors de la page monolithique | ownership-routing-refactor | frontend-react-pages/admin-prompts | None, but split incrementally to avoid one massive PR. |
| SC-002 | F-002 | Centraliser les contrats et hooks API admin consommes par les pages | service-boundary-refactor | frontend-react-pages/admin-api | Decide target owner: `frontend/src/api` flat modules or `features/admin/**/api`. |
| SC-003 | F-003 | Reduire les helpers/composants dupliques dans les pages React | duplicate-rule-removal | frontend-react-pages/page-helpers | Needs prioritization by cluster to keep delta small. |
| SC-004 | F-004 | Converger les barrels de pages et les exports stale | legacy-facade-removal | frontend-react-pages/barrels | None, unless an external import depends on a stale barrel. |
| SC-005 | F-005 | Classer et converger les routes alias publiques | route-architecture-convergence | frontend-react-pages/routes | User decision required for `/today`, `/natal-chart`, `/birth-profile`. |
| SC-006 | F-006 | Ajouter des guards anti-drift d'architecture des pages frontend | architecture-guard-hardening | frontend-react-pages/architecture-guards | Should run with `npm run test -- page-architecture` or equivalent filter. |

## Candidate Details

## SC-001 - Extraire le domaine feature `admin-prompts` hors de la page monolithique

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Extraire le domaine feature `admin-prompts` hors de la page monolithique
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-react-pages/admin-prompts
- Required contracts: no-legacy-dry-audit-contract, page ownership boundary, existing `RG-054` and frontend design-system guardrails.
- Draft objective: turn `AdminPromptsPage` into a typed route container that composes feature-owned tabs, hooks, and components.
- Must include: remove `// @ts-nocheck` from the migrated slice, preserve prompts routing tests, keep `AdminPromptsRouteSlot` behavior or replace it with explicit child rendering, and avoid unrelated visual restyling.
- Validation hints: `npm run lint`, `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow legacy-style design-system`.
- Blockers: none.

## SC-002 - Centraliser les contrats et hooks API admin consommes par les pages

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Centraliser les contrats et hooks API admin consommes par les pages
- Suggested archetype: service-boundary-refactor
- Primary domain: frontend-react-pages/admin-api
- Required contracts: no-legacy-dry-audit-contract, explicit API client boundary.
- Draft objective: remove direct `apiFetch` ownership from admin pages by introducing canonical typed API modules/hooks.
- Must include: migrate at least one coherent cluster first, such as dashboard/logs/users; preserve query keys intentionally; centralize response/error parsing.
- Validation hints: `npm run lint`, `npm run test -- AdminDashboardPage AdminLogsPage AdminUserDetailPage AdminUsersPage admin`.
- Blockers: choose target owner layout: flat `frontend/src/api/admin*.ts` modules or feature-scoped admin API modules.

## SC-003 - Reduire les helpers/composants dupliques dans les pages React

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Reduire les helpers/composants dupliques dans les pages React
- Suggested archetype: duplicate-rule-removal
- Primary domain: frontend-react-pages/page-helpers
- Required contracts: no-legacy-dry-audit-contract.
- Draft objective: extract repeated page helper responsibilities into canonical utility or feature-local modules without changing behavior.
- Must include: classify repeated formatters/error helpers first; migrate one cluster at a time; add focused tests for extracted helpers.
- Validation hints: `npm run lint`, `npm run test -- formatDate BirthProfilePage NatalChartPage SubscriptionSettings AdminSamplePayloadsAdmin PersonasAdmin`.
- Blockers: none, but scope should be sliced by cluster.

## SC-004 - Converger les barrels de pages et les exports stale

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Converger les barrels de pages et les exports stale
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-react-pages/barrels
- Required contracts: no-legacy-dry-audit-contract, route contract tests.
- Draft objective: remove or explicitly classify stale page export surfaces.
- Must include: remove duplicate exports in `pages/admin/index.ts`; classify broad `pages/index.ts`; prevent stale admin modules from remaining available through barrels.
- Validation hints: `npm run lint`, `npm run test -- router AdminPage AdminPromptsRouting ui-nav BottomNavPremium`.
- Blockers: none, unless an external import depends on a stale barrel.

## SC-005 - Classer et converger les routes alias publiques

- Candidate ID: SC-005
- Source finding: F-005
- Suggested story title: Classer et converger les routes alias publiques
- Suggested archetype: route-architecture-convergence
- Primary domain: frontend-react-pages/routes
- Required contracts: no-legacy-dry-audit-contract, route contract tests.
- Draft objective: classify `/today`, `/natal-chart`, and `/birth-profile` as supported public aliases or legacy redirects to remove.
- Must include: document canonical route contract; update tests that currently assert `birth-profile`; preserve user-facing navigation behavior deliberately.
- Validation hints: `npm run lint`, `npm run test -- router DashboardPage DailyHoroscopePage NatalChartPage BirthProfilePage`.
- Blockers: user decision required for `/today`, `/natal-chart`, `/birth-profile`.

## SC-006 - Ajouter des guards anti-drift d'architecture des pages frontend

- Candidate ID: SC-006
- Source finding: F-006
- Suggested story title: Ajouter des guards anti-drift d'architecture des pages frontend
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-react-pages/architecture-guards
- Required contracts: no-legacy-dry-audit-contract, report-output-contract for future audits.
- Draft objective: add deterministic tests/scans that prevent the audited page structure problems from growing.
- Must include: guard `@ts-nocheck` in pages, direct `apiFetch` in pages with exact allowlist, page barrel duplicates/stale exports, route alias allowlist, and page-size exceptions with owner/exit notes.
- Validation hints: `npm run test -- page-architecture`, `npm run lint`.
- Blockers: define temporary allowlist entries for existing monoliths if the guard lands before refactors.

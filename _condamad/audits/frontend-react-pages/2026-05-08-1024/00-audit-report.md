<!-- Rapport de continuite de l'audit CONDAMAD des pages React frontend. -->

# CONDAMAD Domain Audit - frontend-react-pages

Date: 2026-05-08 10:24 Europe/Paris

## Domain

- Domain key: `frontend-react-pages`
- Target: `frontend/src/pages/**`, `frontend/src/app/routes.tsx`, API consumption from React pages, page barrels, page architecture guards, and directly related feature/API owners.
- Archetypes: `legacy-surface-audit`, `dependency-direction-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Domain Closure Status

Status: `phased-with-map`

The previous audit stories CS-090 to CS-095 closed the route aliases, stale admin barrel exports, `AdminPromptsPage` `@ts-nocheck`, and the missing page-architecture guard. The domain is not fully closed because four finite residual surfaces remain:

1. `AdminPromptsPage.tsx` remains an oversized route container with route orchestration, UI sections, modal flow, filtering state, mutations, and presentation helpers still colocated in one 2909-line page.
2. Four admin pages still call `apiFetch(` directly and are now exact allowlist exceptions with owners and exits.
3. Reusable page helpers still have local duplicates outside the CS-092 helper slice.
4. Three pages still carry `@ts-nocheck`; they are guarded exceptions but remain typed-debt surfaces.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/01-evidence-log.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/03-story-candidates.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-090-extraire-domaine-feature-admin-prompts/**`
- `_condamad/stories/CS-091-centraliser-contrats-hooks-api-admin-pages/**`
- `_condamad/stories/CS-092-reduire-helpers-composants-dupliques-pages-react/**`
- `_condamad/stories/CS-093-converger-barrels-pages-exports-stale/**`
- `_condamad/stories/CS-094-classer-converger-routes-alias-publiques/**`
- `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/**`

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| F-001 admin prompts monolith | `still-active` / superseded by current F-001 | E-004, E-005, E-010, E-011 | `@ts-nocheck` is closed, but the page still has 2909 lines and many local responsibilities. |
| F-002 admin API ownership duplicated | `still-active` / superseded by current F-002 | E-006, E-007, E-011 | CS-091 migrated dashboard/logs/users; four admin pages remain exact direct-API exceptions. |
| F-003 page helpers duplicated | `still-active` / superseded by current F-003 | E-008, E-011 | CS-092 centralized `shouldLogSupportForApiError`; other local formatters remain. |
| F-004 stale and duplicate page barrels | `closed` | E-009, E-011 | `PricingAdmin`, `MonitoringAdmin`, and duplicate admin exports are absent; no active barrel consumers were found. |
| F-005 public route aliases | `closed` | E-003, E-011 | `/today`, `/natal-chart`, and `/birth-profile` route aliases are absent and guarded. |
| F-006 missing page-architecture drift guard | `closed` | E-002, E-011, RG-064 | `page-architecture` guard covers `@ts-nocheck`, direct page API calls, public aliases, stale admin exports, and page size exceptions. |

## Active Findings Summary

- High: 1
- Medium: 3
- Low: 0

## Exhaustive Remaining Implementation Surfaces

### Current F-001 - Admin prompts decomposition

Application files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css` only when extracted JSX requires class ownership movement
- `frontend/src/features/admin-prompts/**`
- Existing canonical prompt subcomponents reused by the page:
  - `frontend/src/pages/admin/AdminPromptEditorPanel.tsx`
  - `frontend/src/pages/admin/AdminPromptsLogicGraph.tsx`
  - `frontend/src/pages/admin/AdminPromptCatalogNodeModal.tsx`
  - `frontend/src/pages/admin/PersonasAdmin.tsx`
  - `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`

Governance/test files:

- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`

Stop condition:

- `AdminPromptsPage.tsx` becomes a route composition container below the page-size exception threshold, or the exception is narrowed to a documented permanent route-container owner with no extractable feature/UI logic left.

### Current F-002 - Admin direct API exceptions

Application files:

- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- New or existing canonical API owner files under `frontend/src/api/**`

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing page tests for each migrated page, or new focused tests if absent.

Stop condition:

- `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"` returns zero hits, and `DIRECT_API_PAGE_EXCEPTIONS` becomes empty.

### Current F-003 - Page helper duplication

Application files:

- `frontend/src/pages/admin/PersonasAdmin.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/AdminContentPage.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- Canonical helper owners under `frontend/src/utils/**` or an explicitly documented feature-local owner.

Governance/test files:

- `frontend/src/tests/formatDate.test.ts`
- Focused tests for any new money/date helper if behavior is moved.

Stop condition:

- Local helper duplicates are either removed in favor of canonical helpers or explicitly classified as page-specific one-off logic with tests and no cross-page duplicate.

### Current F-004 - Remaining page `@ts-nocheck`

Application files:

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/pages/NotFoundPage.tsx`

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing page tests or new focused tests for typed behavior.

Stop condition:

- `rg -n "@ts-nocheck" frontend/src/pages -g "*.tsx"` returns zero hits, and `TS_NOCHECK_PAGE_EXCEPTIONS` becomes empty.

## Deferred Non-Domain Context

- Broader design-system token work is protected by existing RG-044 to RG-063 and is not reopened here.
- Backend/API contract changes are out of domain unless needed by a future frontend API-owner story.
- Product route decisions for `/today`, `/natal-chart`, and `/birth-profile` are closed by CS-094 as delete decisions.

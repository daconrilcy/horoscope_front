<!-- Candidats de stories issus de l'audit de continuite des pages React frontend. -->

# Story Candidates - frontend-react-pages

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Decomposer les responsabilites restantes de `AdminPromptsPage` | ownership-routing-refactor | frontend-react-pages/admin-prompts | Stop if an extracted responsibility requires product behavior changes or a backend contract change. |
| SC-002 | F-002 | Centraliser les appels API admin restants hors pages | service-boundary-refactor | frontend-react-pages/admin-api | Stop if an endpoint contract is ambiguous and cannot be inferred from existing page behavior or tests. |
| SC-003 | F-003 | Classer et centraliser les helpers de formatage encore dupliques | duplicate-rule-removal | frontend-react-pages/page-helpers | Stop if two helpers intentionally format different product concepts and cannot share a utility without changing UI copy. |
| SC-004 | F-004 | Typer les pages React encore exclues de TypeScript | architecture-guard-hardening | frontend-react-pages/type-safety | Stop if the typing requires changing an API payload shape not covered by current frontend contracts. |

## SC-001 - Decomposer le reste du conteneur admin-prompts

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Decomposer les responsabilites restantes de `AdminPromptsPage`
- Suggested archetype: ownership-routing-refactor
- Primary domain: `frontend-react-pages/admin-prompts`
- Required contracts: Ownership Routing, No Legacy / DRY, Reintroduction Guard, Baseline Snapshot
- Draft objective: move the remaining extractable admin-prompts helpers, modals, filters, and section rendering into canonical feature/component owners until the route page is only a composition container or has a sharply justified permanent exception.
- Closure intent: `phased-with-map`
- Must include:
  - Capture before/after line counts and responsibility inventory for `AdminPromptsPage.tsx`.
  - Extract one or more coherent slices from this finite map: local modal components, catalog filter state/actions, release diff helpers, consumption section state/rendering, archive rollback helpers, and manual execution flow.
  - Reuse existing canonical prompt components and API hooks instead of creating wrappers.
  - Tighten `PAGE_SIZE_EXCEPTIONS` after each extracted slice.
  - No wildcard allowlist; no folder-wide exception; no compatibility re-export from the page.
- Validation hints:
  - `npm run lint`
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture`
  - `rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" frontend/src/pages/admin/AdminPromptsPage.tsx frontend/src/features/admin-prompts`
- Blockers:
  - Stop if an extracted responsibility requires product behavior changes or a backend contract change.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css` only if classes move with an extracted component
- `frontend/src/features/admin-prompts/**`
- Existing prompt component files only if reused ownership requires typed props:
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

Required before/after evidence:

- line count and local responsibility inventory before;
- line count and extracted ownership inventory after;
- `page-architecture` guard still green.

Stop condition:

- The page-size exception is removed or narrowed to a permanent route-container rationale with no known extractable feature/UI slice left.

## SC-002 - Centraliser les quatre exceptions API admin restantes

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Centraliser les appels API admin restants hors pages
- Suggested archetype: service-boundary-refactor
- Primary domain: `frontend-react-pages/admin-api`
- Required contracts: Ownership Routing, Contract Shape, Reintroduction Guard, No Legacy / DRY
- Draft objective: migrate the remaining page-local `apiFetch(` calls to canonical API modules/hooks and remove all `DIRECT_API_PAGE_EXCEPTIONS`.
- Closure intent: `full-closure`
- Must include:
  - Create or extend canonical owners for admin AI generations, entitlements, settings exports, and support.
  - Preserve existing loading/error/empty behavior.
  - Keep API response parsing and endpoint construction outside React pages.
  - Remove exact allowlist entries after migration.
  - No wildcard exception for pages or admin folders.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture AdminAiGenerationsPage AdminEntitlementsPage AdminSettingsPage AdminSupportPage`
  - `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"`
- Blockers:
  - Stop if an endpoint contract is ambiguous and cannot be inferred from existing page behavior or tests.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminSettingsPage.tsx`
- `frontend/src/pages/admin/AdminSupportPage.tsx`
- `frontend/src/api/**` exact owner modules to create or extend

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing or new tests for the four migrated pages/API hooks

Required before/after evidence:

- before scan listing the four direct API pages;
- after scan zero-hit for `apiFetch(` under `frontend/src/pages`;
- `DIRECT_API_PAGE_EXCEPTIONS` empty.

Stop condition:

- `rg -n "apiFetch\\(" frontend/src/pages -g "*.tsx"` returns zero hits and `npm run test -- page-architecture` passes.

## SC-003 - Classer et centraliser les helpers page restants

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Classer et centraliser les helpers de formatage encore dupliques
- Suggested archetype: duplicate-rule-removal
- Primary domain: `frontend-react-pages/page-helpers`
- Required contracts: No Legacy / DRY, Ownership Routing, Baseline Snapshot
- Draft objective: classify remaining local date, price, and error formatting helpers and move repeated shared behavior into canonical utility modules.
- Closure intent: `phased-with-map`
- Must include:
  - Before inventory for `formatDate`, `formatPrice`, and `getErrorMessage` local definitions.
  - Shared helper extraction only where behavior is actually duplicated.
  - Explicit classification for retained local helpers with reason and tests.
  - No compatibility helper wrappers with old names unless they are the canonical owner.
- Validation hints:
  - `npm run lint`
  - `npm run test -- formatDate`
  - targeted tests for any new money/error helper
  - `rg -n "function formatDate|const formatDate|function formatPrice|const formatPrice|function getErrorMessage|const getErrorMessage" frontend/src -g "*.ts" -g "*.tsx"`
- Blockers:
  - Stop if two helpers intentionally format different product concepts and cannot share a utility without changing UI copy.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/admin/PersonasAdmin.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx`
- `frontend/src/pages/admin/AdminContentPage.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/utils/formatDate.ts`
- New or existing canonical money/error utility under `frontend/src/utils/**` if classification proves shared behavior

Governance/test files:

- `frontend/src/tests/formatDate.test.ts`
- New focused tests for any new shared helper

Required before/after evidence:

- helper inventory before and after;
- classification of retained local helpers;
- no duplicated shared helper behavior left without owner.

Stop condition:

- Every hit is either canonical, imported from a canonical helper, or classified as a page-specific one-off with no shared duplicate.

## SC-004 - Retirer les trois exceptions `@ts-nocheck` pages

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Typer les pages React encore exclues de TypeScript
- Suggested archetype: architecture-guard-hardening
- Primary domain: `frontend-react-pages/type-safety`
- Required contracts: Reintroduction Guard, No Legacy / DRY, Runtime Behavior
- Draft objective: remove `// @ts-nocheck` from the three exact remaining page files while preserving page behavior and keeping the page-architecture guard green.
- Closure intent: `full-closure`
- Must include:
  - Type props, API values, route params, state, and event handlers without weakening `tsconfig.lint.json`.
  - Remove entries from `TS_NOCHECK_PAGE_EXCEPTIONS`.
  - Avoid `@ts-ignore`, `any` broadening, or wrapper compatibility types.
  - Preserve existing visual and route behavior.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture AstrologerProfilePage ConsultationResultPage NotFoundPage`
  - `rg -n "@ts-nocheck|@ts-ignore" frontend/src/pages -g "*.tsx"`
- Blockers:
  - Stop if the typing requires changing an API payload shape not covered by current frontend contracts.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/pages/NotFoundPage.tsx`

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing or new tests for the three pages if behavior is not already covered

Required before/after evidence:

- before scan showing the three hits;
- after scan zero-hit for `@ts-nocheck` in `frontend/src/pages`;
- `TS_NOCHECK_PAGE_EXCEPTIONS` empty;
- lint and page-architecture guard green.

Stop condition:

- `rg -n "@ts-nocheck" frontend/src/pages -g "*.tsx"` returns zero hits and `npm run lint` passes.

## Deferred Non-Domain Context

- No backend implementation story is emitted by this audit.
- No design-system story is emitted unless future page extraction requires CSS ownership movement outside existing token rules.

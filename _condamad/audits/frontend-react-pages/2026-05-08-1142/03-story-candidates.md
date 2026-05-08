<!-- Candidats de stories issus de l'audit de continuite des pages React frontend. -->

# Story Candidates - frontend-react-pages

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Fermer les sections restantes de `AdminPromptsPage` | ownership-routing-refactor | frontend-react-pages/admin-prompts | Stop if extracting a section requires backend contract or product behavior changes. |
| SC-002 | F-002 | Decomposer les pages volumineuses encore allowlistees | ownership-routing-refactor | frontend-react-pages/page-size | Stop if a page is intentionally permanent as a route owner and needs user approval to keep the exception. |
| SC-003 | F-003 | Centraliser le formatage date/heure inline des pages | duplicate-rule-removal | frontend-react-pages/page-helpers | Stop if a visible format differs by product copy and cannot be preserved through the canonical helper. |

## SC-001 - Fermer les sections restantes de AdminPromptsPage

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Fermer les sections restantes de `AdminPromptsPage`
- Suggested archetype: ownership-routing-refactor
- Primary domain: `frontend-react-pages/admin-prompts`
- Required contracts: Ownership Routing, No Legacy / DRY, Reintroduction Guard, Baseline Snapshot
- Draft objective: extract the remaining catalog, consumption, and release sections from `AdminPromptsPage.tsx` into canonical feature owners so the route file is a route composition container.
- Closure intent: `phased-with-map`
- Must include:
  - Use `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md` as the baseline closure map.
  - Extract one coherent section at a time from the finite map: catalog detail/table, consumption surface, or release surface.
  - Preserve existing query hooks and API contracts from `frontend/src/api/adminPrompts.ts`.
  - Remove duplicated state/rendering ownership from the page after each extraction.
  - Tighten or remove `PAGE_SIZE_EXCEPTIONS` for `AdminPromptsPage.tsx`.
  - No wildcard allowlist, no compatibility re-export, no page-local copy of extracted helpers/components.
- Validation hints:
  - `npm run lint`
  - `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture`
  - `rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" frontend/src/pages/admin/AdminPromptsPage.tsx frontend/src/features/admin-prompts -g "*.tsx"`
- Blockers:
  - Stop if extracting a section requires backend contract or product behavior changes.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/features/admin-prompts/**`
- `frontend/src/pages/admin/AdminPromptsPage.css` only if extracted JSX requires class ownership movement

Governance/test files:

- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/AdminPromptsRouting.test.tsx`
- `frontend/src/tests/AdminPromptsCatalogFlow.test.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/admin-prompts-after.md`

Required before/after evidence:

- before line count and selected residual section;
- after line count and extracted owner path;
- absence proof that the extracted section is no longer implemented in the page;
- `page-architecture` guard still green.

Stop condition:

- `AdminPromptsPage.tsx` has no temporary page-size exception, or the remaining exception is permanent-route-only and the closure map has no `remaining-next-slice`.

## SC-002 - Decomposer les pages volumineuses encore allowlistees

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Decomposer les pages volumineuses encore allowlistees
- Suggested archetype: ownership-routing-refactor
- Primary domain: `frontend-react-pages/page-size`
- Required contracts: Ownership Routing, Reintroduction Guard, No Legacy / DRY, Baseline Snapshot
- Draft objective: close the remaining page-size allowlist debt outside `AdminPromptsPage` by decomposing route pages or explicitly reclassifying permanent exceptions.
- Closure intent: `phased-with-map`
- Must include:
  - Capture current line counts and current `PAGE_SIZE_EXCEPTIONS`.
  - Process this finite page map:
    - `frontend/src/pages/AstrologerProfilePage.tsx`
    - `frontend/src/pages/BirthProfilePage.tsx`
    - `frontend/src/pages/settings/SubscriptionSettings.tsx`
    - `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` only if still over the guard threshold or still present as a stale exception.
  - For each page, classify route-only responsibilities vs extractable feature/UI sections.
  - Remove stale allowlist entries when a page is below threshold.
  - No folder-wide page-size exception and no threshold growth.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture`
  - targeted existing tests for each touched page
  - line-count inventory before/after
- Blockers:
  - Stop if a page is intentionally permanent as a route owner and needs user approval to keep the exception.

### Exhaustive Files To Modify

Application files:

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` when still above threshold or stale in allowlist
- Existing or new canonical component/feature owners under `frontend/src/components/**`, `frontend/src/features/**`, or page-adjacent owners selected by local architecture

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing page tests or focused new tests for extracted behavior

Required before/after evidence:

- line-count inventory before and after;
- responsibility classification for every listed page;
- exact allowlist diff with no wildcard exception;
- `page-architecture` guard green.

Stop condition:

- `PAGE_SIZE_EXCEPTIONS` contains no temporary page decomposition debt outside approved permanent-route-only exceptions.

## SC-003 - Centraliser le formatage date/heure inline des pages

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Centraliser le formatage date/heure inline des pages
- Suggested archetype: duplicate-rule-removal
- Primary domain: `frontend-react-pages/page-helpers`
- Required contracts: No Legacy / DRY, Ownership Routing, Baseline Snapshot, Reintroduction Guard
- Draft objective: replace repeated page-level date/time UI formatting with canonical helpers from `frontend/src/utils/formatDate.ts`, or classify exact retained page-specific formatting.
- Closure intent: `full-closure`
- Must include:
  - Build a before inventory from the exact selection rule:
    `rg -n "new Date\\([^\\n]+\\)\\.toLocale(DateString|String)|Intl\\.DateTimeFormat|\\.toLocaleString\\(" frontend/src/pages -g "*.tsx"`.
  - Exclude numeric-only formatting hits after classification.
  - Route date/time UI formatting through `formatDate`, `formatDateTime`, or `formatDateWithOptions`; extend `formatDate.ts` only when preserving current output requires it.
  - Add or update `formatDate.test.ts` when helper behavior changes.
  - Record retained page-specific date/time hits with exact reason.
- Validation hints:
  - `npm run lint`
  - `npm run test -- formatDate page-architecture`
  - final targeted scan and classification inventory
- Blockers:
  - Stop if a visible format differs by product copy and cannot be preserved through the canonical helper.

### Exhaustive Files To Modify

Application files:

- Exact selection rule: all date/time UI formatting hits under `frontend/src/pages/**/*.tsx` from the scan above.
- Current high-confidence files:
  - `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
  - `frontend/src/pages/admin/AdminLogsPage.tsx`
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/pages/admin/AdminSupportPage.tsx`
  - `frontend/src/pages/admin/AdminUserDetailPage.tsx`
  - `frontend/src/pages/admin/AdminUsersPage.tsx`
  - `frontend/src/pages/settings/SubscriptionSettings.tsx`
  - `frontend/src/pages/settings/UsageSettings.tsx`
- `frontend/src/utils/formatDate.ts` only if the canonical helper needs an exact behavior-preserving variant.

Governance/test files:

- `frontend/src/tests/formatDate.test.ts`
- A story-level before/after helper inventory

Required before/after evidence:

- before scan with every hit classified as date/time UI, numeric-only, canonical consumer, or out-of-scope;
- after scan with every remaining hit classified;
- focused helper tests if helper behavior changes.

Stop condition:

- Every page date/time formatting hit is canonical, classified page-specific, numeric-only, or outside the selection rule; no duplicated shared date/time formatting behavior remains unowned.

## Deferred Non-Domain Context

- No backend implementation story is emitted by this audit.
- No design-system story is emitted unless future extraction moves CSS ownership across existing token/inline-style guardrails.
- Frontend API-client consistency inside `frontend/src/api/**` is deferred to a separate API-client audit.

<!-- Registre des constats de l'audit CONDAMAD des pages React du frontend. -->

# Finding Register - frontend-react-pages

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-react-pages/admin-prompts | E-003, E-004, E-005, E-006, E-010 | `AdminPromptsPage` is an active monolith that owns routing tabs, data orchestration, UI sections, helpers, modals, responsive behavior, and style surface while bypassing TypeScript checks. | Extract `admin-prompts` feature modules with typed hooks/components and remove `@ts-nocheck` through incremental slices. | yes |
| F-002 | High | High | missing-canonical-owner | frontend-react-pages/admin-api | E-007, E-011 | Admin API contracts, query keys, path building, response parsing, and errors are repeatedly owned by pages instead of one canonical API layer. | Create canonical admin API hooks/contracts under `frontend/src/api` or a dedicated feature API module, then migrate direct page `apiFetch` usage. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-react-pages/page-helpers | E-003, E-006 | Pages repeatedly define reusable helpers and internal components, increasing drift risk and making page files hard to reason about. | Move shared formatting/error/path helpers to `utils` or feature-local modules and extract page-local components when reused or independently testable. | yes |
| F-004 | Medium | High | legacy-surface | frontend-react-pages/barrels | E-008, E-009, E-011 | Page barrels keep old or duplicate import paths active, including stale admin exports and duplicated exports in `pages/admin/index.ts`. | Converge page exports: remove stale page barrels or replace them with exact canonical exports protected by a guard. | yes |
| F-005 | Medium | Medium | needs-user-decision | frontend-react-pages/routes | E-005, E-009, E-011 | Public route aliases and redirects remain active beside canonical routes, so navigation ownership is not explicit. | Decide whether `/today`, `/natal-chart`, and `/birth-profile` are supported public aliases or legacy redirects to remove; encode the decision in route tests. | yes |
| F-006 | Medium | High | missing-guard | frontend-react-pages/architecture-guards | E-002, E-010, E-011, E-012 | Existing frontend guards protect design-system drift, but not page ownership drift. New monoliths, direct API calls, barrels, or `@ts-nocheck` can be reintroduced silently. | Add deterministic frontend page-architecture guards for direct page API calls, page barrels, `@ts-nocheck`, route aliases, and size exceptions. | yes |

## Finding Details

### F-001 - Admin prompts page is an active monolith

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-react-pages/admin-prompts
- Evidence: E-003, E-004, E-005, E-006, E-010.
- Expected rule: a page should primarily compose route-level data, layout, and feature components; complex domain UI and data decisions should have canonical feature owners.
- Actual state: `AdminPromptsPage.tsx` is 3035 lines, imports `@api`, owns route tab resolution, many filters, local modals/helpers, `PersonasAdmin`, `AdminSamplePayloadsAdmin`, logic graph projections, and uses `// @ts-nocheck`.
- Impact: `AdminPromptsPage` is an active monolith that owns routing tabs, data orchestration, UI sections, helpers, modals, responsive behavior, and style surface while bypassing TypeScript checks.
- Recommended action: Extract `admin-prompts` feature modules with typed hooks/components and remove `@ts-nocheck` through incremental slices.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

### F-002 - Admin API ownership is duplicated in pages

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-react-pages/admin-api
- Evidence: E-007, E-011.
- Expected rule: pages consume canonical API clients/hooks and uniform error handling, rather than rebuilding endpoint paths and response parsing locally.
- Actual state: direct `apiFetch` calls appear in multiple admin pages with page-local DTOs, query keys, error strings, URL builders, and response parsing.
- Impact: Admin API contracts, query keys, path building, response parsing, and errors are repeatedly owned by pages instead of one canonical API layer.
- Recommended action: Create canonical admin API hooks/contracts under `frontend/src/api` or a dedicated feature API module, then migrate direct page `apiFetch` usage.
- Story candidate: yes
- Suggested archetype: service-boundary-refactor

### F-003 - Page-local helpers and components duplicate responsibilities

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-react-pages/page-helpers
- Evidence: E-003, E-006.
- Expected rule: formatting, API error classification, route/path construction, and reusable UI chunks should have one owner when used across pages or feature slices.
- Actual state: repeated helpers include `formatDate`, `formatPrice`, `shouldLogSupportForApiError`, `getErrorMessage`, `buildLlmLogsPath`, `buildAuditLogsPath`, and page-local components such as KPI cards, modals, catalog cards, subscription cards, and profile metrics.
- Impact: Pages repeatedly define reusable helpers and internal components, increasing drift risk and making page files hard to reason about.
- Recommended action: Move shared formatting/error/path helpers to `utils` or feature-local modules and extract page-local components when reused or independently testable.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-004 - Page barrels preserve stale and duplicate import surfaces

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-react-pages/barrels
- Evidence: E-008, E-009, E-011.
- Expected rule: page imports should have canonical paths; removed or renamed pages should not remain available through barrels unless explicitly supported.
- Actual state: `frontend/src/pages/admin/index.ts` exports `PricingAdmin`, `MonitoringAdmin`, and duplicate entries for several admin pages. `frontend/src/pages/index.ts` broadly re-exports pages including `HomePage`.
- Impact: Page barrels keep old or duplicate import paths active, including stale admin exports and duplicated exports in `pages/admin/index.ts`.
- Recommended action: Converge page exports: remove stale page barrels or replace them with exact canonical exports protected by a guard.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-005 - Public route aliases need an explicit product decision

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: frontend-react-pages/routes
- Evidence: E-005, E-009, E-011.
- Expected rule: route aliases are either deliberate supported public contracts or classified legacy redirects with an exit plan.
- Actual state: `/today` redirects to `/dashboard/horoscope`, `/birth-profile` redirects to `/profile`, and `/natal-chart` renders `NatalChartPage` beside `/natal`. Tests still assert the existence of `birth-profile`.
- Impact: Public route aliases and redirects remain active beside canonical routes, so navigation ownership is not explicit.
- Recommended action: Decide whether `/today`, `/natal-chart`, and `/birth-profile` are supported public aliases or legacy redirects to remove; encode the decision in route tests.
- Story candidate: yes
- Suggested archetype: route-architecture-convergence

### F-006 - Missing page-architecture drift guard

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-react-pages/architecture-guards
- Evidence: E-002, E-010, E-011, E-012.
- Expected rule: recurrent architectural risks should be guarded by deterministic tests or scans.
- Actual state: design-system guards exist, but no page-architecture guard blocks direct page `apiFetch`, duplicate page barrels, new page `@ts-nocheck`, unclassified route aliases, or oversized page exceptions.
- Impact: Existing frontend guards protect design-system drift, but not page ownership drift. New monoliths, direct API calls, barrels, or `@ts-nocheck` can be reintroduced silently.
- Recommended action: Add deterministic frontend page-architecture guards for direct page API calls, page barrels, `@ts-nocheck`, route aliases, and size exceptions.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

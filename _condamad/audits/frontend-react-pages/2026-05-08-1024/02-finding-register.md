<!-- Registre des constats restants apres les stories CS-090 a CS-095. -->

# Finding Register - frontend-react-pages

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-react-pages/admin-prompts | E-004, E-005, E-010, E-011, E-014 | `AdminPromptsPage` is typed and guarded now, but it remains a large route page that still owns extractable feature/UI responsibilities. | Continue decomposition with a finite slice map that removes local modal/helper/section ownership from the page and tightens the size exception. | yes |
| F-002 | Medium | High | missing-canonical-owner | frontend-react-pages/admin-api | E-006, E-007, E-011, E-012 | Admin API ownership is partially centralized, but four admin pages still build requests directly through `apiFetch`. | Migrate the four exact direct-API exceptions to canonical `frontend/src/api/**` owners and empty the allowlist. | yes |
| F-003 | Medium | Medium | duplicate-responsibility | frontend-react-pages/page-helpers | E-008, E-011, E-012 | CS-092 centralized one support-error helper, but repeated date, price, and error helpers still create drift risk across pages. | Classify the remaining helper duplicates and centralize the repeated ones under `utils` or feature-local owners. | yes |
| F-004 | Medium | High | missing-guard | frontend-react-pages/type-safety | E-007, E-011, E-013 | Three pages still bypass TypeScript checks; the guard prevents silent growth but does not close the typed-debt surface. | Type the three exact page exceptions and remove them from `TS_NOCHECK_PAGE_EXCEPTIONS`. | yes |

## Finding Details

### F-001 - Admin prompts page remains an oversized feature owner

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-react-pages/admin-prompts
- Evidence: E-004, E-005, E-010, E-011, E-014.
- Impact: `AdminPromptsPage` is typed and guarded now, but it remains a large route page that still owns extractable feature/UI responsibilities.
- Expected rule: a React page should compose route-level layout and feature owners; reusable feature sections, modals, helpers, and orchestration should live in canonical feature or component modules.
- Actual state: `AdminPromptsPage.tsx` is 2909 lines. It no longer has `@ts-nocheck`, but it still owns route tab resolution, multiple local components/helpers, a large state surface, mutations, modals, filters, and heavy JSX sections. The guard allows it up to 3200 lines with an exit note.
- Recommended action: Continue decomposition with a finite slice map that removes local modal/helper/section ownership from the page and tightens the size exception.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: `phased-with-map`

### F-002 - Four admin pages still own direct API calls

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-react-pages/admin-api
- Evidence: E-006, E-007, E-011, E-012.
- Impact: Admin API ownership is partially centralized, but four admin pages still build requests directly through `apiFetch`.
- Expected rule: pages consume canonical API clients/hooks and uniform error handling rather than building admin endpoints directly.
- Actual state: CS-091 created canonical owners for dashboard, logs, and users. Direct `apiFetch(` calls remain in `AdminAiGenerationsPage.tsx`, `AdminEntitlementsPage.tsx`, `AdminSettingsPage.tsx`, and `AdminSupportPage.tsx`; these are exact guard exceptions.
- Recommended action: Migrate the four exact direct-API exceptions to canonical `frontend/src/api/**` owners and empty the allowlist.
- Story candidate: yes
- Suggested archetype: service-boundary-refactor
- Closure classification: `closure-ready`

### F-003 - Remaining page helper duplication is only partially reduced

- Severity: Medium
- Confidence: Medium
- Category: duplicate-responsibility
- Domain: frontend-react-pages/page-helpers
- Evidence: E-008, E-011, E-012.
- Impact: CS-092 centralized one support-error helper, but repeated date, price, and error helpers still create drift risk across pages.
- Expected rule: repeated date, money, and API error formatting helpers have one canonical owner unless a page-specific variant is explicitly justified.
- Actual state: `shouldLogSupportForApiError` is centralized under `frontend/src/utils/apiErrorSupport.ts`, but local `formatDate`, `formatPrice`, and error message helpers remain in several pages and settings/admin modules.
- Recommended action: Classify the remaining helper duplicates and centralize the repeated ones under `utils` or feature-local owners.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal
- Closure classification: `phased-with-map`

### F-004 - `@ts-nocheck` remains on three page files

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-react-pages/type-safety
- Evidence: E-007, E-011, E-013.
- Impact: Three pages still bypass TypeScript checks; the guard prevents silent growth but does not close the typed-debt surface.
- Expected rule: React pages should type-check; any temporary bypass must be exact, owned, guarded, and have an exit.
- Actual state: `AstrologerProfilePage.tsx`, `ConsultationResultPage.tsx`, and `NotFoundPage.tsx` still contain `// @ts-nocheck`. They are listed in `TS_NOCHECK_PAGE_EXCEPTIONS`, so reintroduction is guarded but debt remains active.
- Recommended action: Type the three exact page exceptions and remove them from `TS_NOCHECK_PAGE_EXCEPTIONS`.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
- Closure classification: `closure-ready`

## Closed Prior Findings

- Prior F-004 is closed: stale `PricingAdmin` / `MonitoringAdmin` exports and duplicate admin barrel entries are absent.
- Prior F-005 is closed: `/today`, `/natal-chart`, and `/birth-profile` aliases are absent.
- Prior F-006 is closed: `page-architecture` guard is present, exact, and green.

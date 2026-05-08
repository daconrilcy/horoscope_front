<!-- Registre des constats restants apres les stories CS-096 a CS-099. -->

# Finding Register - frontend-react-pages

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | frontend-react-pages/admin-prompts | E-004, E-005, E-007, E-012 | `AdminPromptsPage.tsx` is reduced and guarded, but it still owns large catalog, consumption, and release route sections that CS-096 explicitly classified as remaining slices. | Extract the remaining finite sections into canonical `features/admin-prompts` owners until the page-size exception can be removed or made permanent-route-only. | yes |
| F-002 | Medium | High | missing-canonical-owner | frontend-react-pages/page-size | E-004, E-007 | Page architecture is guarded, but exact size exceptions remain for oversized pages outside the admin-prompts monolith. | Decompose or reclassify each oversized route page exception with a finite closure map and remove stale/near-threshold entries. | yes |
| F-003 | Medium | Medium | duplicate-responsibility | frontend-react-pages/page-helpers | E-008, E-009, E-012 | The named helper-definition debt is closed, but repeated inline date/time formatting still creates drift across pages and bypasses the canonical date utility owner. | Migrate date/time UI formatting hits to `frontend/src/utils/formatDate.ts` helpers or classify exact page-specific exceptions. | yes |

## Finding Details

### F-001 - AdminPromptsPage still has extractable page-owned sections

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-react-pages/admin-prompts
- Evidence: E-004, E-005, E-007, E-012.
- Impact: `AdminPromptsPage.tsx` is reduced and guarded, but it still owns large catalog, consumption, and release route sections that CS-096 explicitly classified as remaining slices.
- Expected rule: a React route page composes route layout and delegates substantial feature/UI sections to canonical feature owners.
- Actual state: CS-096 extracted helpers and modals, but its own after-inventory names catalog, consumption, and release JSX sections as `remaining-next-slice`. Current scans show the page still owns a large local state/effect surface and route-section rendering.
- Recommended action: Extract the remaining finite sections into canonical `features/admin-prompts` owners until the page-size exception can be removed or made permanent-route-only.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: `phased-with-map`

### F-002 - Oversized page exceptions remain outside AdminPrompts

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-react-pages/page-size
- Evidence: E-004, E-007.
- Impact: Page architecture is guarded, but exact size exceptions remain for oversized pages outside the admin-prompts monolith.
- Expected rule: large pages should either be decomposed into route containers plus feature/component owners, or have a documented permanent route-owner rationale with an exact guard.
- Actual state: `PAGE_SIZE_EXCEPTIONS` contains exact entries and exits for these pages. The guard passes, which means growth is controlled, but the debt remains visible.
- Recommended action: Decompose or reclassify each oversized route page exception with a finite closure map and remove stale/near-threshold entries.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: `phased-with-map`

### F-003 - Inline date/time formatting remains duplicated across pages

- Severity: Medium
- Confidence: Medium
- Category: duplicate-responsibility
- Domain: frontend-react-pages/page-helpers
- Evidence: E-008, E-009, E-012.
- Impact: The named helper-definition debt is closed, but repeated inline date/time formatting still creates drift across pages and bypasses the canonical date utility owner.
- Expected rule: shared date/time UI formatting should route through `frontend/src/utils/formatDate.ts`, while retained page-specific formatting should be explicitly classified.
- Actual state: `formatDate.ts` is the canonical helper owner and is tested, yet several page files still directly instantiate dates for UI output.
- Recommended action: Migrate date/time UI formatting hits to `frontend/src/utils/formatDate.ts` helpers or classify exact page-specific exceptions.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal
- Closure classification: `closure-ready`

## Closed Prior Findings

- 10:24 F-002 is closed: direct `apiFetch(` calls are absent from `frontend/src/pages/**`, `DIRECT_API_PAGE_EXCEPTIONS` is empty, and `page-architecture` passes.
- 10:24 F-004 is closed: `@ts-nocheck` is absent from `frontend/src/pages/**`, `TS_NOCHECK_PAGE_EXCEPTIONS` is empty, and `page-architecture` passes.
- 01:23 stale admin barrels and public route aliases remain closed by zero-hit scans and `RG-064`.

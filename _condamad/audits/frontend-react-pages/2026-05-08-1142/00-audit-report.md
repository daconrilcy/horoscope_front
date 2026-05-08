<!-- Rapport d'audit CONDAMAD de continuite des pages React frontend. -->

# CONDAMAD Domain Audit - frontend-react-pages

Date: 2026-05-08 11:42 Europe/Paris

## Domain

- Domain key: `frontend-react-pages`
- Target: `frontend/src/pages/**`, `frontend/src/app/routes.tsx`, page-facing API owners, helper owners, page architecture guards, and directly related CONDAMAD stories.
- Archetypes: `legacy-surface-audit`, `dependency-direction-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Domain Closure Status

Status: `phased-with-map`

The stories implemented after the 10:24 audit closed the four named residual findings in their original form:

1. `CS-096` reduced `AdminPromptsPage.tsx`, extracted helpers/modals into `frontend/src/features/admin-prompts/adminPromptsPageParts.tsx`, and tightened its size exception.
2. `CS-097` removed all direct `apiFetch(` calls from `frontend/src/pages/**` and emptied `DIRECT_API_PAGE_EXCEPTIONS`.
3. `CS-098` centralized the targeted local `formatDate`, `formatPrice`, and `getErrorMessage` helper definitions or classified the remaining one-off helper.
4. `CS-099` removed all page-level `@ts-nocheck` exceptions and emptied `TS_NOCHECK_PAGE_EXCEPTIONS`.

The domain is not fully closed because current evidence still shows three finite residual implementation surfaces:

1. `AdminPromptsPage.tsx` remains a large route file at 2586 lines, with the CS-096 after-inventory itself classifying `catalog`, `consumption`, and `release` JSX sections as `remaining-next-slice`.
2. The page-size guard now contains exact exceptions for other oversized route pages: `AstrologerProfilePage.tsx`, `SubscriptionSettings.tsx`, and `BirthProfilePage.tsx`. `AdminSamplePayloadsAdmin.tsx` remains near the threshold and is still allowlisted.
3. Date/time formatting is still duplicated inline across page files through repeated `new Date(...).toLocaleString()`, `toLocaleDateString()`, and `Intl.DateTimeFormat(...)` calls instead of a canonical page helper owner.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-0123/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/00-audit-report.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/02-finding-register.md`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/03-story-candidates.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-096-decomposer-responsabilites-restantes-admin-prompts/**`
- `_condamad/stories/CS-097-centraliser-appels-api-admin-restants-hors-pages/**`
- `_condamad/stories/CS-098-classer-centraliser-helpers-formatage-pages/**`
- `_condamad/stories/CS-099-typer-pages-react-exclues-typescript/**`

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 10:24 F-001 admin prompts decomposition | `still-active` / superseded by current F-001 | E-004, E-005, E-012 | CS-096 closed one slice, but `remaining-next-slice` is documented and the page remains 2586 lines. |
| 10:24 F-002 admin direct API exceptions | `closed` | E-006, E-007, E-012, RG-064 | Zero `apiFetch(` hits under `frontend/src/pages`; `DIRECT_API_PAGE_EXCEPTIONS` is empty. |
| 10:24 F-003 targeted helper duplication | `closed` / superseded by current F-003 for inline formatting | E-008, E-009, E-012 | The named helper definitions are centralized/classified; inline date formatting remains a distinct DRY surface. |
| 10:24 F-004 page `@ts-nocheck` | `closed` | E-006, E-007, E-012, RG-064 | Zero `@ts-nocheck` hits under `frontend/src/pages`; `TS_NOCHECK_PAGE_EXCEPTIONS` is empty. |
| 01:23 F-004 stale page barrels | `closed` | E-006, E-007, RG-064 | Removed admin exports remain absent and guarded. |
| 01:23 F-005 public route aliases | `closed` | E-006, E-007, RG-064 | `/today`, `/natal-chart`, and `/birth-profile` aliases remain absent and guarded. |
| 01:23 F-006 missing page architecture guard | `closed` | E-006, E-007, RG-064 | `npm run test -- page-architecture` passes. |

## Active Findings Summary

- High: 1
- Medium: 2
- Low: 0

## Exhaustive Remaining Implementation Surfaces

### Current F-001 - Admin prompts route container still has extractable sections

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

Stop condition:

- `AdminPromptsPage.tsx` loses its page-size exception, or its remaining exception documents a permanent route-only owner with no `remaining-next-slice` entries and no extractable catalog, consumption, or release JSX/state responsibility.

### Current F-002 - Oversized page allowlist outside AdminPrompts remains active

Application files:

- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.tsx` only if it remains over the guard threshold after current line-count reconciliation

Governance/test files:

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- Existing or new focused tests for the decomposed pages

Stop condition:

- `PAGE_SIZE_EXCEPTIONS` contains no temporary decomposition debt, or each remaining entry is below threshold and removed, with `npm run test -- page-architecture` green.

### Current F-003 - Inline date/time formatting remains duplicated in pages

Application files:

- Exact selection rule: every `frontend/src/pages/**/*.tsx` hit from `rg -n "new Date\\([^\\n]+\\)\\.toLocale(DateString|String)|Intl\\.DateTimeFormat|\\.toLocaleString\\(" frontend/src/pages -g "*.tsx"` that formats a date/time for UI output.
- Current high-confidence hits include:
  - `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
  - `frontend/src/pages/admin/AdminLogsPage.tsx`
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/pages/admin/AdminSupportPage.tsx`
  - `frontend/src/pages/admin/AdminUserDetailPage.tsx`
  - `frontend/src/pages/admin/AdminUsersPage.tsx`
  - `frontend/src/pages/settings/SubscriptionSettings.tsx`
  - `frontend/src/pages/settings/UsageSettings.tsx`
- Canonical owner: `frontend/src/utils/formatDate.ts`, extended only if existing helpers cannot preserve current output.

Governance/test files:

- `frontend/src/tests/formatDate.test.ts`
- New focused tests only if `formatDate.ts` behavior is extended.

Stop condition:

- Every page date/time formatting hit is either imported from a canonical helper, classified as intentional page-specific formatting with evidence, or outside the date/time UI formatting selection rule.

## Deferred Non-Domain Context

- Broader frontend design-system token and CSS legacy work remains governed by `RG-044` to `RG-063` and is not reopened here.
- Backend/API contract changes are out of domain unless a future frontend page story proves a blocking runtime contract ambiguity.
- `frontend/src/api/support.ts` uses direct `fetch` in an API owner, not in page code; that belongs to a future frontend API-client consistency audit if desired.

## Validation

Read-only evidence collection completed. Targeted frontend validation was run:

- `npm run lint` - PASS.
- `npm run test -- page-architecture` - PASS.
- `npm run test -- formatDate formatPrice` - PASS.

Audit artifact validation was run after report generation; see `01-evidence-log.md`.

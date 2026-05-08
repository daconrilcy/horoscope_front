# Target Files - CS-108

## Must read

- `AGENTS.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/00-audit-report.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`

## Must search

- `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" frontend/src _condamad/stories/CS-107-classer-pages-layout-owner -g "*.tsx" -g "*.ts" -g "*.md"`
- `rg -n "PASS with limitation|TODO|wildcard|compatibility wrapper|shim|alias|fallback|migration-only" _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout _condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`

## Likely modified

- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-before.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden unless directly justified

- `frontend/src/app/routes.tsx` unless a sourced decision approves routing.
- `frontend/src/pages/**/*.tsx` physical deletion in this story.
- `frontend/src/styles/**` and CSS files.
- `backend/**`.
- `frontend/package.json`.

## Existing tests to inspect first

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/BillingSuccessPage.test.tsx`
- `frontend/src/tests/App.test.tsx`

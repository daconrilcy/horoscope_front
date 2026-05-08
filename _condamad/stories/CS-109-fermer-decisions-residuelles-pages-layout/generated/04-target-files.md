# CS-109 - Target files

## Must read

- `_condamad/audits/frontend-layouts/2026-05-08-1914/00-audit-report.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md`
- `frontend/src/app/routes.tsx`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/pages/landing/LandingPage.tsx`
- `backend/app/core/config.py`

## Must search

- `rg -n "HomePage" frontend/src`
- `rg -n "privacy|billing/success|billing/cancel" frontend/src/app/routes.tsx frontend/src/tests/page-architecture-allowlist.ts`
- `rg -n "TestimonialsSection" frontend/src/pages/landing/LandingPage.tsx frontend/src/tests/page-architecture-allowlist.ts`
- stale blocker scan over audit 1914, CS-107, CS-108 and CS-109.

## Likely modified

- CS-109 capsule files.
- CS-109 `closure-before.md` and `closure-after.md`.
- Audit `2026-05-08-1914` active artifacts.
- CS-108 final evidence.
- `story-status.md`.
- Frontend route/test/allowlist files only if verification exposes a gap.

## Forbidden unless justified

- `backend/**` implementation files.
- `frontend/src/layouts/**`.
- `frontend/src/styles/**`.
- `frontend/package.json`.

# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `AnalyticsProvider` excludes the removed provider. | `frontend/src/config/analytics.ts` exposes only `plausible` and `noop`. | `pnpm lint`; `rg -n "matomo" frontend/src/config/analytics.ts` exit 1. | PASS |
| AC2 | Removed provider queue is absent from active hook source. | `frontend/src/hooks/useAnalytics.ts` no longer declares or uses the provider queue branch. | `rg -n "_paq" frontend/src/hooks/useAnalytics.ts` exit 1. | PASS |
| AC3 | `noop` remains the local default. | Config normalizes unprepared providers to `noop`; test covers default and unsupported provider. | `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics`. | PASS |
| AC4 | Plausible still receives sanitized props. | Plausible branch remains in `useAnalytics` and still uses `sanitizeAnalyticsProps`. | `vitest run useAnalytics`; redaction assertion in `useAnalytics.test.tsx`. | PASS |
| AC5 | Direct provider calls stay centralized. | No changes outside canonical hook/config/test surfaces. | `rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api` exit 1. | PASS |
| AC6 | Active docs/config omit removed provider option. | `.env.example` already documents empty local provider and Plausible only; no active doc update needed. | `rg -n "matomo|_paq" frontend/src .env.example docs` exit 1. | PASS |
| AC7 | Redaction runtime remains covered. | Existing sensitive-field catalog kept canonical; no duplicate redaction list added. | `vitest run useAnalytics natalInterpretation natalChartApi`; sensitive-field scan recorded. | PASS |
| AC8 | No backend provider path exists. | Backend untouched. | `rg -n "matomo|_paq" backend` exit 1. | PASS |
| AC9 | Persistent evidence artifacts exist. | Evidence folder contains before/after scans, audit and validation log. | Capsule evidence files created; `condamad_validate.py` rerun after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

<!-- Rapport d'audit CONDAMAD de continuite sur la hierarchie des layouts frontend. -->

# CONDAMAD Domain Audit - frontend-layouts continuity

Date: 2026-05-08 19:14 Europe/Paris

## Domain

- Domain key: `frontend-layouts`
- Target: `frontend/src/app/routes.tsx`, `frontend/src/layouts/**`, `frontend/src/app/guards/LandingRedirect.tsx`, `frontend/src/tests/page-architecture-*`, `frontend/src/pages/**/*.tsx`, and CS-108 decision artifacts.
- Archetypes: `legacy-surface-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Expected Rules

- `RootLayout` remains the route-level master layout.
- `LandingLayout`, `AuthLayout`, `AppLayout`, and nested section layouts remain explicit owners for their route families.
- No page under `frontend/src/pages/**/*.tsx` can be unclassified.
- `needs-user-decision` pages must not be routed until their decision is named, source-backed, and reflected in the executable registry.
- `dead/unmounted-page-candidate` entries must not be reattached or imported by runtime code until a retention, removal, or product decision is recorded.
- No compatibility route, redirect, alias, shim, fallback, wildcard allowlist, or duplicate layout owner is allowed.

## Domain Closure Status

Status: `closed-by-CS-109`

The implementation surface audited by `2026-05-08-1405` remains closed:

- `RootLayout` is still mounted as the root route element.
- `LandingLayout` owns the landing wrapper; `LandingRedirect` remains a redirect/content guard and does not own `.landing-layout`.
- `/login` and `/register` remain under `AuthLayout`.
- `AppLayout` does not own the master background shell.
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` still covers every current `frontend/src/pages/**/*.tsx` file.
- The targeted frontend validations pass.

CS-109 applied the user decisions from 2026-05-08 and closes the residual
decision surface:

- `pages/PrivacyPolicyPage.tsx` is routed at `/privacy` under `LandingLayout`.
- `pages/billing/BillingSuccessPage.tsx` is routed at `/billing/success` under `AppLayout`.
- `pages/billing/BillingCancelPage.tsx` is routed at `/billing/cancel` under `AppLayout`.
- `pages/HomePage.tsx` is removed with no route, wrapper, alias, fallback or re-export.
- `pages/landing/sections/TestimonialsSection.tsx` is owned by `LandingPage`.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-layouts/2026-05-08-1405/**`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/**`
- `_condamad/stories/CS-103-converger-layout-maitre-frontend/**`
- `_condamad/stories/CS-104-monter-landing-via-layout-principal/**`
- `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/**`
- `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/**`
- `_condamad/stories/CS-107-classer-pages-layout-owner/**`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/**`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails Consulted

- `RG-064` - page architecture guards remain exact.
- `RG-066` - page-size exceptions must not broaden.
- `RG-067` - date/time formatting ownership remains outside this layout audit.
- `RG-068` - `RootLayout` remains master; route families keep explicit layout owners; page files keep exact classification.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 2026-05-08-1405 F-001 | `closed` | E-001, E-002, E-007, E-008 | `RootLayout` is still root route owner and `AppLayout` has no master background shell. |
| 2026-05-08-1405 F-002 | `closed` | E-001, E-003, E-008 | Landing route remains under `LandingLayout`; bypass symbols are absent from runtime owner. |
| 2026-05-08-1405 F-003 | `closed` | E-001, E-004, E-008 | Auth routes remain nested under `AuthLayout`. |
| 2026-05-08-1405 F-004 | `closed` | E-005, E-006, E-007 | Guards and targeted tests still enforce layout hierarchy and page ownership. |
| 2026-05-08-1405 F-005 | `closed` | E-005, E-009, E-010, CS-109 | Every page file is classified and the residual files have final decisions. |
| 2026-05-08-1532 F-101 | `closed-by-CS-109` | E-009, E-010, E-011, CS-109 | CS-109 supersedes the CS-108 residual decision blockers. |
| 2026-05-08-1532 F-102 | `closed` | E-012 | CS-103 through CS-108 are marked `done` in story status and story headers. |

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

## Closure Analysis

Active implementation findings: none.

Active decision findings: none.

Closed decision findings:

- F-201: the five residual page decisions are closed by CS-109.

Closed implementation surfaces:

- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`

Exhaustive closed decision surfaces:

- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`

Governance files with pending work:

- none for implementation.
- CS-109 is the current closure evidence for the former residual decisions.

Deferred non-domain context:

- Legal copy maintenance for privacy publication.
- External Stripe dashboard override outside repository if it diverges from backend defaults.
- Design-system CSS debt, unrelated to this layout ownership audit.

## Validation

- `npm run test -- page-architecture layout` from `frontend/`: PASS, 3 files passed, 29 tests passed.
- `npm run test -- App router BillingSuccessPage BillingCancelPage` from `frontend/`: PASS, 7 files passed, 83 tests passed. React Router future-flag warnings are non-blocking.
- `npm run test -- LandingPage visual-smoke` from `frontend/`: PASS, 1 file passed, 18 tests passed.
- `npm run test` from `frontend/`: PASS, 122 files passed, 1301 tests passed, 8 skipped.
- `npm run lint` from `frontend/`: PASS.
- Audit artifact validation and lint were run with the repository venv active; see `01-evidence-log.md`.

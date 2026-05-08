<!-- Rapport d'audit CONDAMAD de suivi sur la hierarchie des layouts frontend. -->

# CONDAMAD Domain Audit - frontend-layouts follow-up

Date: 2026-05-08 15:32 Europe/Paris

## Domain

- Domain key: `frontend-layouts`
- Target: `frontend/src/app/routes.tsx`, `frontend/src/app/guards/LandingRedirect.tsx`, `frontend/src/layouts/**`, `frontend/src/tests/page-architecture-*`, and page ownership classifications for `frontend/src/pages/**/*.tsx`.
- Archetypes: `legacy-surface-audit`, `dependency-direction-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Audit artifacts and `_condamad/stories/regression-guardrails.md` were written; CS-103 to CS-107 story headers were updated in a governance-only status sync.

## Expected Rules

- Every rendered page must be reached through a layout owner.
- One mounted master layout owns the global background shell.
- Landing, auth-public, application and admin route families must have explicit layout ownership.
- Page files under `frontend/src/pages/**/*.tsx` must be routed, nested-routed, page-adjacent, dead/unmounted candidate, or `needs-user-decision`.
- Guards must prevent unmounted `RootLayout`, landing layout bypasses, direct auth routes, broad page exceptions, and unclassified page files.

## Domain Closure Status

Status: `blocked`

The implementation work from the previous audit is materially closed for runtime layout hierarchy and guards:

- `RootLayout` is mounted at `/` and owns `StarfieldBackground`, `.app-shell app-bg`, and `.app-bg-container`.
- `AppLayout` no longer owns the global background shell.
- `/` is nested under `LandingLayout`; `LandingRedirect` only owns token cleanup/redirect and lazy landing content rendering.
- `/login` and `/register` are nested under `AuthLayout`.
- `page-architecture-guards.test.ts` now guards root layout, app layout background ownership, landing bypass, auth direct routes, and page-file classification.
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` classifies every current `frontend/src/pages/**/*.tsx` file.

The domain is not `closed` because the remaining page ownership registry contains explicit decision blockers:

- `pages/PrivacyPolicyPage.tsx` is `needs-user-decision`.
- `pages/billing/BillingSuccessPage.tsx` is `needs-user-decision`.
- `pages/billing/BillingCancelPage.tsx` is `needs-user-decision`.
- `pages/HomePage.tsx` and `pages/landing/sections/TestimonialsSection.tsx` are `dead/unmounted-page-candidate`, kept pending a removal decision/story.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-layouts/2026-05-08-1405/**`
- `_condamad/stories/CS-103-converger-layout-maitre-frontend/**`
- `_condamad/stories/CS-104-monter-landing-via-layout-principal/**`
- `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/**`
- `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/**`
- `_condamad/stories/CS-107-classer-pages-layout-owner/**`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails Consulted

- `RG-064` protects page architecture guards.
- `RG-065` protects AdminPrompts ownership.
- `RG-066` protects page-size exception closure.
- `RG-067` protects page date/time formatting ownership.
- `RG-068` was added by this audit to persist the now-enforced frontend layout hierarchy invariant.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 2026-05-08-1405 F-001 | `closed` | E-001, E-002, E-006, E-007, RG-068 | `RootLayout` is the root route element and `AppLayout` no longer renders the master background. |
| 2026-05-08-1405 F-002 | `closed` | E-001, E-003, E-006, E-007, RG-068 | Landing route is under `LandingLayout`; bypass symbols are absent from `LandingRedirect`. |
| 2026-05-08-1405 F-003 | `closed` | E-001, E-004, E-006, E-007, RG-068 | Auth routes are children of `AuthLayout`, not direct root children. |
| 2026-05-08-1405 F-004 | `closed` | E-005, E-006, E-007, RG-068 | Deterministic guards now cover layout hierarchy and page inventory. |
| 2026-05-08-1405 F-005 | `closed-with-blocked-residual-decisions` | E-005, E-006, E-008, E-009, RG-068 | Every page file is classified; public/dead candidates remain intentionally blocked by decision. |

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 0 |
| Info | 0 |

## Closure Analysis

Active implementation findings: none.

Active decision findings:

- F-101: decide the public/dead page candidates recorded by CS-107.

Closed governance findings:

- F-102: CS-103 to CS-107 story statuses now use `Status: done`.

Closed implementation surfaces:

- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`

Exhaustive remaining decision surfaces:

- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/landing/sections/TestimonialsSection.tsx`

Governance files with pending work: none.

Deferred non-domain context:

- Legal content for the privacy page.
- Stripe/billing callback product contract and external URLs.
- Design-system CSS debt unrelated to layout ownership.

## Validation

- `npm run lint` from `frontend/`: PASS.
- `npm run test -- page-architecture layout` from `frontend/`: PASS, 3 files passed, 23 tests passed.
- `npm run test -- App router BillingSuccessPage` from `frontend/`: PASS, 6 files passed, 80 tests passed.
- Audit artifact validation and lint were run after report generation; see `01-evidence-log.md`.

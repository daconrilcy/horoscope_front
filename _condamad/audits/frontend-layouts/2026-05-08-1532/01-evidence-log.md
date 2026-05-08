<!-- Journal des preuves de l'audit CONDAMAD de suivi frontend-layouts. -->

# Evidence Log - frontend-layouts follow-up

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | source-inspection | `Get-Content frontend/src/app/routes.tsx` | `frontend/src/app/routes.tsx` | PASS | Route root uses `RootLayout`; landing/auth/app branches are nested under it. |
| E-002 | source-inspection | `Get-Content frontend/src/layouts/RootLayout.tsx` and `Get-Content frontend/src/layouts/AppLayout.tsx` | `RootLayout.tsx`, `AppLayout.tsx` | PASS | `RootLayout` owns master background; `AppLayout` owns secondary navigation shell only. |
| E-003 | source-inspection | `Get-Content frontend/src/app/guards/LandingRedirect.tsx` and `Get-Content frontend/src/layouts/LandingLayout.tsx` | `LandingRedirect.tsx`, `LandingLayout.tsx` | PASS | `LandingRedirect` no longer imports `LandingLayout.css`, no `ScopedLandingPage`, no `.landing-layout` wrapper. |
| E-004 | source-inspection | `Get-Content frontend/src/layouts/AuthLayout.tsx` and route tree inspection | `AuthLayout.tsx`, `routes.tsx` | PASS | `AuthLayout` exposes `Outlet`; `/login` and `/register` are children. |
| E-005 | source-inspection | `Get-Content frontend/src/tests/page-architecture-guards.test.ts` and `page-architecture-allowlist.ts` | `frontend/src/tests/page-architecture-*` | PASS | Guards cover root, app, landing, auth, and exact page ownership inventory. |
| E-006 | targeted-test | `npm run test -- page-architecture layout` from `frontend/` | Vitest page/layout guards | PASS | 3 files passed, 23 tests passed. |
| E-007 | targeted-test | `npm run test -- App router BillingSuccessPage` from `frontend/` | App/router/billing tests | PASS | 6 files passed, 80 tests passed. React Router future flag warnings are non-blocking. |
| E-008 | targeted-scan | `rg --files frontend/src/pages -g "*.tsx"` | `frontend/src/pages/**/*.tsx` | PASS | Current inventory contains 50 page TSX files. |
| E-009 | targeted-scan | targeted rg scan for residual page candidate symbols | page candidates and tests | PASS | Billing success has tests; public/dead candidates remain un-routed or test-only and classified in allowlist. |
| E-010 | targeted-scan | targeted rg scan for landing and master background symbols | `frontend/src/**/*.tsx` | PASS | Master background symbols appear in `RootLayout` and tests/components only; `LandingLayout.css` import is in `LandingLayout` and tests. |
| E-011 | targeted-scan | `rg -n 'landing-layout' frontend/src -g '*.tsx'` | `frontend/src/**/*.tsx` | PASS | Runtime owner is `LandingLayout.tsx`; other hits are tests. |
| E-012 | lint | `npm run lint` from `frontend/` | TypeScript projects | PASS | TypeScript lint/build checks passed. |
| E-013 | governance-source | `_condamad/stories/CS-103` to `CS-107` `*-after.md` artifacts | story evidence artifacts | PASS | After artifacts claim all route/layout guards implemented and passing. |
| E-014 | governance-source | status scan for CS-103 to CS-107 story headers | story source files | PASS | No stale `ready-to-dev` status remains for CS-103 to CS-107; each story now uses `Status: done`. |
| E-015 | guardrail-source | `_condamad/stories/regression-guardrails.md` | shared guardrail registry | PASS | `RG-068` added to preserve enforced frontend layout hierarchy invariant. |

## Evidence Details

### E-001 - Route table inventory

`frontend/src/app/routes.tsx` mounts `RootLayout` as the root route element. `LandingLayout`, `AuthLayout`, and the authenticated `AppLayout` branch are children of that master route.

### E-002 - Master layout ownership

`RootLayout` renders the global background shell and `StarfieldBackground`. `AppLayout` renders header/sidebar/bottom navigation and no longer contains the master background symbols.

### E-003 - Landing layout ownership

`LandingRedirect` no longer contains `LandingLayout.css`, `ScopedLandingPage`, or a local `landing-layout` wrapper. `LandingLayout` remains the only runtime owner of `.landing-layout`.

### E-004 - Auth layout ownership

`AuthLayout` renders an `Outlet`, and `/login` plus `/register` are nested under that layout in the route tree.

### E-005 - Guard inventory

`page-architecture-guards.test.ts` imports the route tree and checks root layout, app shell ownership, landing bypass prevention, auth route nesting, and page classification.

### E-006 - Layout guard tests

`npm run test -- page-architecture layout` passed with 3 test files and 23 tests.

### E-007 - App/router tests

`npm run test -- App router BillingSuccessPage` passed with 6 test files and 80 tests.

### E-008 - Page file inventory

`rg --files frontend/src/pages -g "*.tsx"` listed the current page surface used by the classification guard.

### E-009 - Residual page candidate scan

The scan confirmed the remaining decision files exist and are not silently routed by the audit.

### E-010 - Forbidden symbol scan

The master background and landing layout symbols are present only in their canonical owners or tests.

### E-011 - Landing wrapper scan

The only runtime `landing-layout` class owner is `LandingLayout.tsx`.

### E-012 - Frontend lint

`npm run lint` passed.

### E-013 - Story after artifacts

CS-103 through CS-107 after artifacts exist and describe completed route/layout/guard work.

### E-014 - Stale story status scan

CS-103 through CS-107 `00-story.md` files no longer advertise `Status: ready-to-dev`.

### E-015 - Regression guardrail registry

`RG-068` records the enforced layout hierarchy invariant for future stories.

## Runtime / Structural Evidence Summary

- Runtime route structure is represented by the exported `RouteObject[]` and consumed by Vitest guards.
- The guard suite inspects the actual route objects, not only string scans.
- Static scans were used only to verify forbidden bypass symbols and residual decision surfaces.

## Known Limitations

- The audit did not start the local Vite dev server because this was a read-only follow-up audit and targeted route/render tests passed.
- The audit did not decide whether privacy and billing callback pages should become public routes; that is a product/contract decision.

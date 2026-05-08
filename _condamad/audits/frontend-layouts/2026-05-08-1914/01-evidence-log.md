<!-- Journal des preuves de l'audit CONDAMAD de continuite frontend-layouts. -->

# Evidence Log - frontend-layouts continuity

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | source-inspection | `Get-Content frontend/src/app/routes.tsx` | `frontend/src/app/routes.tsx` | PASS | Root route uses `RootLayout`; landing, auth, and protected branches are children. |
| E-002 | source-inspection | `Get-Content frontend/src/layouts/RootLayout.tsx` and `Get-Content frontend/src/layouts/AppLayout.tsx` | `RootLayout.tsx`, `AppLayout.tsx` | PASS | Master background shell is owned by `RootLayout`, not `AppLayout`. |
| E-003 | targeted-scan | targeted landing bypass scan for `landing-layout`, `ScopedLandingPage`, and `LandingLayout.css` | landing route/layout surfaces | PASS | Runtime landing wrapper owner is `LandingLayout`; test hits are non-runtime evidence. |
| E-004 | source-inspection | route tree inspection and `AuthLayout` guard imports | `routes.tsx`, `AuthLayout.tsx` | PASS | Login/register remain nested under `AuthLayout`. |
| E-005 | source-inspection | `Get-Content frontend/src/tests/page-architecture-allowlist.ts` and `page-architecture-guards.test.ts` | `frontend/src/tests/page-architecture-*` | PASS | Classification registry is exact and guard rejects unclassified, routed-blocked, anonymous-decision, and reattached dead entries. |
| E-006 | targeted-test | `npm run test -- page-architecture layout` from `frontend/` | Vitest page/layout guards | PASS | 3 files passed, 29 tests passed after CS-109 closure guards. |
| E-007 | lint | `npm run lint` from `frontend/` | TypeScript projects | PASS | TypeScript lint projects passed. |
| E-008 | targeted-test | `npm run test -- App router BillingSuccessPage BillingCancelPage` from `frontend/` | App/router/billing tests | PASS | 7 files passed, 83 tests passed. React Router future warnings are non-blocking. |
| E-009 | targeted-scan | `rg --files frontend/src/pages -g "*.tsx"` | `frontend/src/pages/**/*.tsx` | PASS | Current inventory contains 50 page TSX files. |
| E-010 | targeted-scan | targeted residual symbol scan for privacy, billing, home, and testimonials surfaces | residual decision files and owners | PASS | Privacy and billing hits are expected in route tree and allowlist; `HomePage` has no active route/barrel/allowlist hit; `TestimonialsSection` is imported by `LandingPage` and classified there. |
| E-011 | governance-source | `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md`, `generated/10-final-evidence.md`, and CS-109 closure evidence | CS-108/CS-109 artifacts | PASS | CS-109 supersedes the former CS-108 residual blockers with final routed/deleted/owned decisions. |
| E-012 | governance-source | `_condamad/stories/story-status.md` and CS-108 story header | story status registry | PASS | CS-103 through CS-108 are recorded as `done`. |
| E-013 | guardrail-source | `_condamad/stories/regression-guardrails.md` | shared guardrail registry | PASS | `RG-068` is the active frontend-layouts invariant. |
| E-014 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/frontend-layouts/2026-05-08-1914` | audit artifact set | PASS | Validator passed with venv active. |
| E-015 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/frontend-layouts/2026-05-08-1914` | audit artifact set | PASS | Lint passed with venv active. |
| E-016 | targeted-test | `npm run test -- LandingPage visual-smoke` from `frontend/` | Landing visual-smoke tests | PASS | 1 file passed, 18 tests passed. |
| E-017 | regression-test | `npm run test` from `frontend/` | Full Vitest suite | PASS | 122 files passed; 1301 passed, 8 skipped. |
| E-018 | story-validation | CS-109 story validate/lint commands with venv active | CS-109 story file | PASS | Validate, explain-contracts, lint and strict lint passed. |

## Evidence Details

### E-001 - Route table inventory

The exported `routes` object still mounts `RootLayout` at `/` and nests `LandingLayout`, `AuthLayout`, and the authenticated `AppLayout` branch below it.

### E-002 - Master layout ownership

`RootLayout` remains the owner of the global background shell and `StarfieldBackground`. `AppLayout` remains a secondary navigation shell.

### E-003 - Landing ownership scan

The landing wrapper class is owned by `LandingLayout.tsx`. `LandingRedirect` does not import `LandingLayout.css` and does not recreate the wrapper.

### E-004 - Auth ownership

`/login` and `/register` are children of the `AuthLayout` branch and are not direct root children.

### E-005 - Guard inventory

The page architecture guard verifies route ownership, page classification coverage, blocked page routing, dead candidate reattachment, and structured decision metadata.

### E-006 - Layout guard tests

`npm run test -- page-architecture layout` passed with 29 tests.

### E-007 - Frontend lint

`npm run lint` passed.

### E-008 - App/router tests

`npm run test -- App router BillingSuccessPage BillingCancelPage` passed. The only stderr output was React Router future-flag warning text from the existing test harness.

### E-009 - Page file inventory

The current `frontend/src/pages/**/*.tsx` inventory contains 50 files. No missing classification was found by the guard suite.

### E-010 - Residual decision scan

Residual symbols now match CS-109 decisions: privacy and billing callbacks are routed, `HomePage` is absent from active surfaces, and `TestimonialsSection` is attached to `LandingPage`.

### E-011 - CS-108 / CS-109 decision artifacts

CS-108 is historical evidence for the original decision-blocker scope. CS-109 is the active closure evidence for the routed/deleted/owned final state.

### E-012 - Story status source

The story status registry reports layout stories through CS-109 and is synchronized during CS-109 closure.

### E-013 - Guardrail registry

`RG-068` is the applicable invariant tying `RootLayout`, route family owners, and exact page file classification together.

## Runtime / Structural Evidence Summary

- Runtime route structure is represented by `frontend/src/app/routes.tsx` and inspected by Vitest guards.
- Static scans support No Legacy and residual-decision checks.
- Governance artifacts point to CS-109 as the active closure evidence.

## Known Limitations

- The audit did not start the local Vite dev server; targeted route/render tests, full Vitest suite and lint passed.
- External Stripe dashboard configuration is outside repository scope if it overrides backend defaults.

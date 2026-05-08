<!-- Journal des preuves de l'audit CONDAMAD frontend-layouts post-CS-109. -->

# Evidence Log - frontend-layouts post-CS-109

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | source-inspection | `Get-Content frontend/src/app/routes.tsx` | `frontend/src/app/routes.tsx` | PASS | `RootLayout` owns `/`; landing, auth, privacy, app and billing callback branches are nested under explicit layouts. |
| E-002 | source-inspection | `Get-Content frontend/src/tests/page-architecture-allowlist.ts` | `frontend/src/tests/page-architecture-allowlist.ts` | PASS | Privacy, billing callbacks, and `TestimonialsSection` have CS-109 decision sources; no active `HomePage` row exists. |
| E-003 | targeted-test | `npm run test -- page-architecture layout` | `frontend/` | PASS | 3 files passed, 29 tests passed. |
| E-004 | targeted-test | `npm run test -- css-fallback inline-style design-system` | `frontend/` | PASS | 3 files passed, 27 tests passed; existing allowlists accept `TwoColumnLayout.tsx` inline style. |
| E-005 | targeted-scan | targeted scan for malformed padding, sidebar width inline style, and CS-109 status tokens | layouts and CS-109 status files | FAIL | Found invalid `PageLayout.css` padding, `TwoColumnLayout` inline style, and CS-109 status drift. |
| E-006 | source-inspection | `Get-Content frontend/src/layouts/PageLayout.css` | `frontend/src/layouts/PageLayout.css` | FAIL | Active declaration has an extra closing parenthesis: `padding: var(--layout-page-padding));`. |
| E-007 | source-inspection | `Get-Content frontend/src/layouts/TwoColumnLayout.tsx`, `TwoColumnLayout.css`, inline-style allowlists | `frontend/src/layouts/TwoColumnLayout.*`, `frontend/src/tests/*allowlist.ts` | LIMITATION | Inline style is exact and guarded, but remains an in-layout exception against the repo no-inline-style rule. |
| E-008 | governance-source | `_condamad/stories/story-status.md` and CS-109 story header | `_condamad/stories/**` | FAIL | Canonical registry says CS-109 is `done`; source story header says `Status: ready-to-dev`. |
| E-009 | governance-source | CS-109 `closure-after.md` and `generated/10-final-evidence.md` | `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/**` | PASS | Runtime closure evidence exists and marks ACs PASS. |
| E-010 | regression-test | `npm run test` | `frontend/` | PASS | 122 files passed; 1301 passed, 8 skipped. Warnings are existing React Router/jsdom harness output. |
| E-011 | lint | `npm run lint` | `frontend/` | PASS | TypeScript lint projects passed. |
| E-012 | targeted-test | `npm run test -- App router BillingSuccessPage BillingCancelPage LandingPage visual-smoke` | `frontend/` | PASS | 8 files passed, 101 tests passed. |
| E-013 | targeted-scan | `rg --files frontend/src/pages -g "*.tsx" \| rg "HomePage"` | `frontend/src/pages` | PASS | Exit 1 expected zero-hit; no `HomePage.tsx` file remains. |
| E-014 | guardrail-source | `_condamad/stories/regression-guardrails.md` | shared guardrail registry | PASS | `RG-047`, `RG-050`, `RG-064`, and `RG-068` apply. |
| E-015 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/frontend-layouts/2026-05-08-2026` | audit artifact set | PASS | Validator passed with venv active. |
| E-016 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/frontend-layouts/2026-05-08-2026` | audit artifact set | PASS | Lint passed with venv active. |

## Evidence Details

### E-001 - Route hierarchy

`RootLayout` remains mounted as the root route element. `LandingLayout` owns `/` and `/privacy`, `AuthLayout` owns `/login` and `/register`, and `AppLayout` owns protected routes including `/billing/success` and `/billing/cancel`.

### E-002 - Page ownership registry

`PAGE_LAYOUT_OWNER_CLASSIFICATIONS` still covers the page inventory. CS-109 decision sources are attached to privacy, billing callbacks, and testimonials. `HomePage` is absent from the active registry.

### E-005 / E-006 - CSS syntax risk

`frontend/src/layouts/PageLayout.css` contains an active malformed declaration. Current lint and Vitest checks pass, proving the existing guard set does not catch this class of layout CSS syntax error.

### E-007 - Inline style exception

`TwoColumnLayout.tsx` sets `--sidebar-width` through `style={{ '--sidebar-width': sidebarWidth }}`. This is currently listed in `design-system-allowlist.ts` and `inline-style-allowlist.ts`, so the guard suite treats it as accepted. The repository-level rule says no inline style, so this remains an explicit residual decision or remediation target.

### E-008 / E-009 - CS-109 governance drift

CS-109 runtime closure evidence exists and the global story registry says the story is `done`, but the source story header remains `Status: ready-to-dev`. This is not a runtime route defect, but it weakens the audit trail for the just-closed layout finding.

## Runtime / Structural Evidence Summary

- The route hierarchy and page ownership closure from CS-103 through CS-109 is structurally intact.
- Full frontend tests pass.
- Residual issues are limited to layout primitive cleanup and governance status alignment.

## Known Limitations

- The audit did not start the local Vite dev server; Vitest route/render coverage and full frontend tests passed.
- The CSS syntax issue was identified by source inspection/static scan, not by a parser-based CSS lint because no such guard currently fails.

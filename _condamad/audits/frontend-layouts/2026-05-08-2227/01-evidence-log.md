<!-- Journal des preuves de l'audit CONDAMAD de fermeture frontend-layouts. -->

# Evidence Log - frontend-layouts closure

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | source-inspection | `Get-Content frontend/src/app/routes.tsx` | `frontend/src/app/routes.tsx` | PASS | Prior route hierarchy remains guarded by tests; root, landing, auth, app and billing route ownership is unchanged from the closed state. |
| E-002 | targeted-test | `npm run test -- page-architecture layout` | `frontend/` | PASS | 3 files passed, 29 tests passed. |
| E-003 | source-inspection | `Get-Content frontend/src/tests/page-architecture-allowlist.ts` and `rg --files frontend/src/pages -g "*.tsx"` | `frontend/src/tests/page-architecture-allowlist.ts`, `frontend/src/pages` | PASS | Page inventory is covered by exact classifications; no active `HomePage` file appears in the page file list. |
| E-004 | governance-source | `rg -n "CS-109\|Status:" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | `_condamad/stories/**` | PASS | CS-109 is `done` in both the canonical registry and source story header. |
| E-005 | targeted-scan | targeted `rg` scan for malformed `PageLayout.css` padding, `style=`, and `--sidebar-width` in `frontend/src/layouts` | `frontend/src/layouts` | PASS | Exit 1 expected zero-hit; no inline `style=`, `--sidebar-width`, or malformed `PageLayout.css` padding remains in layout sources. |
| E-006 | targeted-scan | targeted No Legacy layout/page scans for blocked classifications, `HomePage`, landing bypasses, and master shell ownership | `frontend/src/app`, `frontend/src/layouts`, `frontend/src/pages`, page architecture registry | PASS | Runtime hits are limited to expected canonical owners (`RootLayout`, `LandingLayout`) and type-only registry classifications; no active bypass or stale page decision remains. |
| E-007 | targeted-test | `npm run test -- css-fallback inline-style design-system` | `frontend/` | PASS | 3 files passed, 28 tests passed; layout CSS syntax guard and inline-style policy are active. |
| E-008 | lint | `npm run lint` | `frontend/` | PASS | TypeScript lint projects passed. |
| E-009 | guardrail-source | `_condamad/stories/regression-guardrails.md` | shared guardrail registry | PASS | `RG-047`, `RG-050`, `RG-064`, and `RG-068` apply. |
| E-010 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/frontend-layouts/2026-05-08-2227` | audit artifact set | PASS | Validator passed with venv active. |
| E-011 | validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/frontend-layouts/2026-05-08-2227` | audit artifact set | PASS | Lint passed with venv active. |

## Evidence Details

### E-002 - Layout and page architecture guard

`npm run test -- page-architecture layout` passed with 29 tests. The suite covers `RootLayout` mounting, `AppLayout` background ownership, landing bypass prevention, auth route ownership, privacy and billing callback routes, page file classification, and `HomePage` reintroduction prevention.

### E-005 - Prior residual implementation findings

The targeted scan confirms the three implementation symptoms from audit `2026-05-08-2026` no longer exist in layout implementation files:

- malformed `padding: var(--layout-page-padding));` is absent;
- `TwoColumnLayout.tsx` has no `style=` attribute;
- `--sidebar-width` is no longer written from React.

### E-007 - Design-system and inline-style guards

`npm run test -- css-fallback inline-style design-system` passed with 28 tests. This confirms the layout CSS syntax guard and exact inline-style allowlist policy currently accept the closed state.

## Runtime / Structural Evidence Summary

- The route hierarchy and page ownership closure from CS-103 through CS-109 remains structurally intact.
- The layout primitive cleanup from CS-110 and CS-111 remains present.
- The governance alignment from CS-112 remains present.

## Known Limitations

- The audit did not start the local Vite dev server because no application code was changed during this audit and targeted route/layout tests passed.
- Broader design-system debt outside `frontend-layouts` was intentionally deferred to the frontend design-system audit chain.

<!-- Rapport d'audit CONDAMAD de continuite sur les layouts frontend apres CS-109. -->

# CONDAMAD Domain Audit - frontend-layouts post-CS-109

Date: 2026-05-08 20:26 Europe/Paris

## Domain

- Domain key: `frontend-layouts`
- Target: `frontend/src/app/routes.tsx`, `frontend/src/layouts/**`, `frontend/src/components/layout/**`, `frontend/src/tests/page-architecture-*`, `frontend/src/tests/*style*`, and prior `frontend-layouts` CONDAMAD evidence.
- Archetypes: `test-guard-coverage-audit`, `legacy-surface-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Expected Rules

- `RootLayout` remains the route-level master layout.
- `LandingLayout`, `AuthLayout`, `AppLayout`, and nested section layouts remain explicit route-family owners.
- Every `frontend/src/pages/**/*.tsx` file remains classified by the executable page-owner registry.
- Layout primitives must not introduce invalid CSS declarations, duplicate layout ownership, wildcard allowlists, stale blockers, compatibility wrappers, or inline styles outside exact policy.
- Governance evidence for completed layout stories must not contradict the canonical story status.

## Domain Closure Status

Status: `open`

The route hierarchy and page ownership work from audits `2026-05-08-1405`, `2026-05-08-1532`, and `2026-05-08-1914` remains closed by current code and guards.

Residual in-domain work remains in layout primitives and governance:

- `frontend/src/layouts/PageLayout.css` contains an invalid active declaration: `padding: var(--layout-page-padding));`.
- `frontend/src/layouts/TwoColumnLayout.tsx` still owns a dynamic inline style for `--sidebar-width`; this is exact and guarded, but it conflicts with the repository rule "Aucun style inline" and should be retired or explicitly re-decided.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` still says `Status: ready-to-dev` while `_condamad/stories/story-status.md` records CS-109 as `done`.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-layouts/2026-05-08-1405/**`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/**`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/**`
- `_condamad/stories/CS-103-converger-layout-maitre-frontend/**`
- `_condamad/stories/CS-104-monter-landing-via-layout-principal/**`
- `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/**`
- `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/**`
- `_condamad/stories/CS-107-classer-pages-layout-owner/**`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/**`
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/**`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails Consulted

- `RG-047` - static inline styles are forbidden; dynamic exceptions must stay exact.
- `RG-050` - design-system exceptions must remain exact and source-backed.
- `RG-064` - page architecture guardrails must remain exact.
- `RG-068` - `RootLayout` remains master and page files keep exact layout-owner classifications.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 2026-05-08-1405 F-001 | `closed` | E-001, E-003, E-010 | `RootLayout` is still root route owner and route guards pass. |
| 2026-05-08-1405 F-002 | `closed` | E-001, E-003, E-010 | Landing route remains under `LandingLayout`; local wrapper bypass is guarded. |
| 2026-05-08-1405 F-003 | `closed` | E-001, E-003, E-010 | `/login` and `/register` remain under `AuthLayout`. |
| 2026-05-08-1405 F-004 | `closed` | E-003, E-004, E-010 | Layout hierarchy and page-owner guards pass. |
| 2026-05-08-1405 F-005 | `closed` | E-002, E-003, E-010 | Page files remain covered by `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`. |
| 2026-05-08-1532 F-101 | `closed` | E-002, E-008, E-009 | CS-109 closes privacy, billing callback, home, and testimonials decisions. |
| 2026-05-08-1532 F-102 | `closed` | E-008 | Story registry records CS-103 through CS-109. |
| 2026-05-08-1914 F-201 | `closed` | E-001, E-002, E-008, E-009 | Runtime decisions and CS-109 closure evidence remain aligned, except source-story status drift captured as F-303. |

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 1 |
| Info | 0 |

## Closure Analysis

Active implementation findings:

- F-301: invalid CSS declaration in `PageLayout.css`.
- F-302: dynamic inline style remains in `TwoColumnLayout.tsx`.

Active governance findings:

- F-303: CS-109 source-story status does not match canonical `story-status.md`.

Implementation files with pending work:

- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`

Governance/test files with pending work:

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts` or a narrower CSS syntax guard
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`

Deferred non-domain context:

- Broader design-system debt outside `frontend/src/layouts/**`.
- React Router future-flag warnings and jsdom canvas/navigation warnings from the test harness.
- External Stripe dashboard configuration outside the repository.

## Validation

- `npm run lint` from `frontend/`: PASS.
- `npm run test -- page-architecture layout` from `frontend/`: PASS, 3 files passed, 29 tests passed.
- `npm run test -- css-fallback inline-style design-system` from `frontend/`: PASS, 3 files passed, 27 tests passed.
- `npm run test -- App router BillingSuccessPage BillingCancelPage LandingPage visual-smoke` from `frontend/`: PASS, 8 files passed, 101 tests passed.
- `npm run test` from `frontend/`: PASS, 122 files passed, 1301 passed, 8 skipped.
- Audit artifact validation and lint were run with the repository venv active; see `01-evidence-log.md`.


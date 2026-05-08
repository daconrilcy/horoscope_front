<!-- Rapport d'audit CONDAMAD de fermeture sur les layouts frontend apres CS-110 a CS-112. -->

# CONDAMAD Domain Audit - frontend-layouts closure

Date: 2026-05-08 22:27 Europe/Paris

## Domain

- Domain key: `frontend-layouts`
- Target: `frontend/src/app/routes.tsx`, `frontend/src/layouts/**`, `frontend/src/tests/page-architecture-*`, `frontend/src/tests/*style*`, `frontend/src/tests/design-system-*`, and prior `frontend-layouts` CONDAMAD evidence.
- Archetypes: `test-guard-coverage-audit`, `legacy-surface-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Expected Rules

- `RootLayout` remains the route-level master layout.
- `LandingLayout`, `AuthLayout`, `AppLayout`, and nested section layouts remain explicit route-family owners.
- Every `frontend/src/pages/**/*.tsx` file remains classified by the executable page-owner registry.
- Layout primitives must not introduce invalid CSS declarations, duplicate layout ownership, wildcard allowlists, stale blockers, compatibility wrappers, or inline styles outside exact policy.
- Governance evidence for completed layout stories must agree with the canonical story status.

## Domain Closure Status

Status: `closed`

The route hierarchy and page ownership work from audits `2026-05-08-1405`, `2026-05-08-1532`, and `2026-05-08-1914` remains closed by current code and guards.

The three residual findings from audit `2026-05-08-2026` are also closed:

- `frontend/src/layouts/PageLayout.css` now uses `padding: var(--layout-page-padding);`.
- `frontend/src/layouts/TwoColumnLayout.tsx` no longer uses an inline `style` attribute or runtime `--sidebar-width` write.
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` now says `Status: done`, matching `_condamad/stories/story-status.md`.

No active in-domain implementation, test, or governance finding remains for `frontend-layouts`.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-layouts/2026-05-08-1405/**`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/**`
- `_condamad/audits/frontend-layouts/2026-05-08-1914/**`
- `_condamad/audits/frontend-layouts/2026-05-08-2026/**`
- `_condamad/stories/CS-103-converger-layout-maitre-frontend/**`
- `_condamad/stories/CS-104-monter-landing-via-layout-principal/**`
- `_condamad/stories/CS-105-rattacher-routes-auth-publiques-layout/**`
- `_condamad/stories/CS-106-ajouter-guards-hierarchie-layout-frontend/**`
- `_condamad/stories/CS-107-classer-pages-layout-owner/**`
- `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/**`
- `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/**`
- `_condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/**`
- `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/**`
- `_condamad/stories/CS-112-aligner-statut-source-cs109-cloture/**`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails Consulted

- `RG-047` - static inline styles are forbidden; dynamic exceptions must stay exact.
- `RG-050` - design-system exceptions must remain exact and source-backed.
- `RG-064` - page architecture guardrails must remain exact.
- `RG-068` - `RootLayout` remains master and page files keep exact layout-owner classifications.

No new durable invariant was added to `_condamad/stories/regression-guardrails.md`; the existing invariants already cover the closed layout hierarchy, inline-style policy, and guard suite.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| 2026-05-08-1405 F-001 | `closed` | E-001, E-002, E-006 | `RootLayout` is still root route owner and route guards pass. |
| 2026-05-08-1405 F-002 | `closed` | E-001, E-002, E-006 | Landing route remains under `LandingLayout`; local wrapper bypass is guarded. |
| 2026-05-08-1405 F-003 | `closed` | E-001, E-002, E-006 | `/login` and `/register` remain under `AuthLayout`. |
| 2026-05-08-1405 F-004 | `closed` | E-002, E-006, E-007 | Layout hierarchy and page-owner guards pass. |
| 2026-05-08-1405 F-005 | `closed` | E-002, E-003, E-006 | Page files remain covered by `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`. |
| 2026-05-08-1532 F-101 | `closed` | E-002, E-003, E-006 | CS-109 decisions remain applied; no blocked/dead page decision is active. |
| 2026-05-08-1532 F-102 | `closed` | E-004 | Story registry records CS-103 through CS-112. |
| 2026-05-08-1914 F-201 | `closed` | E-001, E-002, E-003, E-004, E-006 | Runtime decisions and CS-109 closure evidence remain aligned. |
| 2026-05-08-2026 F-301 | `closed` | E-005, E-007 | `PageLayout.css` malformed padding is absent and layout CSS syntax guard is covered by design-system tests. |
| 2026-05-08-2026 F-302 | `closed` | E-005, E-007 | `TwoColumnLayout.tsx` has no inline `style=` hit and no `--sidebar-width` source hit remains. |
| 2026-05-08-2026 F-303 | `closed` | E-004 | CS-109 source story status matches canonical `done` registry state. |

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

Active governance findings: none.

Closed implementation surfaces:

- `frontend/src/app/routes.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/inline-style-allowlist.ts`

Exhaustive files to modify for active findings:

- Application files: none.
- Governance/test files: none.

Deferred non-domain context:

- Broader design-system inline-style exceptions outside `frontend/src/layouts/**`.
- React Router future-flag warnings and jsdom canvas/navigation warnings from the test harness.
- External Stripe dashboard configuration outside the repository.

## Validation

- `npm run lint` from `frontend/`: PASS.
- `npm run test -- page-architecture layout` from `frontend/`: PASS, 3 files passed, 29 tests passed.
- `npm run test -- css-fallback inline-style design-system` from `frontend/`: PASS, 3 files passed, 28 tests passed.
- Audit artifact validation and lint were run with the repository venv active; see `01-evidence-log.md`.

# Audit Report - frontend-ux-natal-projections - 2026-05-26-0622

## Scope

- Domain key: `frontend-ux-natal-projections`
- Audited domain: `/natal` frontend UX after B2C projection wiring.
- Source story: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md`.
- Source brief: `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md`.
- Archetype selected: custom frontend UX audit using `test-guard-coverage-audit`, `legacy-surface-audit`, and No Legacy / DRY dimensions as supporting contracts.
- Read-only mode: yes for application code. Only audit artifacts under `_condamad/audits/**` were created.

## Domain Closure Status

Status: `open`.

The audited implementation is visually stable for the success state and structurally guarded, but one in-domain remediation remains: projection panel wording should be closed through the existing CS-308 wording story or an equivalent wording-ownership story. No code correction was applied during this audit.

## Prior Audit And Story History Consulted

| Source | Status under current evidence | Evidence | Notes |
|---|---|---|---|
| `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` | closed | E-004 | Projection wiring, state tests, central API ownership already proven. |
| `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/10-final-evidence.md` | closed | E-004 | Desktop and mobile browser proof exists; this audit adds tablet evidence. |
| `_condamad/audits/frontend-components/2026-05-09-1101` | closed | E-005 | Component ownership guard is still relevant and passes. |
| `_condamad/audits/frontend-layouts/2026-05-08-2227` | closed | E-005 | Layout findings are not reopened by `/natal` projection evidence. |
| `_condamad/audits/frontend-design-system/2026-05-08-0054` | closed | E-005 | Token/CSS ownership remains relevant; no new inline style issue found. |
| `_condamad/audits/frontend-api/2026-05-10-1850` | partially non-domain | E-005, E-009, E-012 | Broader frontend API transport findings exist, but `/natal` projections use central `apiFetch`. |
| `_condamad/stories/CS-308-revoir-wording-beginner-summary-client-interpretation/00-story.md` | still-active related story | E-020 | Existing story matches the remaining wording-ownership remediation. |

## Evidence Summary

- Browser QA: `browser-qa-ledger.json` and screenshots under `screenshots/` prove `/natal` success projections and disclaimers are visible on desktop, tablet, and mobile with no overlap against primary controls or disclaimer block (E-019).
- Tests: targeted `natalInterpretation` and `NatalChartPage` tests pass; architecture/API guard tests pass; full frontend Vitest passes (E-015, E-016, E-017).
- Static guards: no inline styles in audited TSX owners; no direct `fetch` or `axios` call to `/v1/astrology/projections`; disclaimer copy remains app-owned (E-011, E-012, E-014).
- Typecheck: direct TypeScript lint-equivalent commands pass; `pnpm lint` hit a Windows lockfile limitation before invoking TypeScript (E-018).

## Findings

| Finding | Severity | Status | Summary |
|---|---|---|---|
| F-001 | Medium | active | Projection panel wording is readable but not closed by a canonical wording owner because labels/state messages are hardcoded in the rendering component. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/pages/NatalChartPage.tsx` | used | E-006, E-015, E-019 | `/natal` page composition owner renders `NatalInterpretationSection` and is covered by page tests and browser QA. | Browser QA uses controlled API responses, not a real authenticated database session. |
| `frontend/src/features/natal-chart/NatalInterpretation.tsx` / `NatalInterpretationSection` | used | E-006, E-013, E-015, E-016 | Feature owner orchestrates interpretation and projection query state; architecture tests preserve ownership. | None for audited scope. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` / `InterpretationContent` | used | E-007, E-010, E-014, E-015, E-019 | Presentational owner renders interpretation content, projections, and app-owned disclaimer footer. | Wording ownership remains open in F-001. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` / `AstrologyProjectionsPanel` | used | E-007, E-010, E-015, E-019 | Projection panel renders loading, entitlement, API error, empty, and success states. | Labels and state copy are hardcoded French strings pending CS-308-style closure. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` / `ProjectionCard` | used | E-007, E-010, E-015, E-019 | Projection cards render `beginner_summary_v1` and `client_interpretation_projection_v1` payloads. | Product tone and localization closure pending F-001. |
| `frontend/src/features/natal-chart/NatalInterpretation.css` / `.ni-projections*` | used | E-008, E-011, E-019 | Existing CSS owner handles projection layout and browser evidence shows no overlap across audited viewports. | No visual diff was needed because this run is read-only. |
| `frontend/src/api/astrologyProjections.ts` / `requestAstrologyProjection` | used | E-009, E-012, E-013, E-016, E-019 | Central API transport owner for `/v1/astrology/projections`; browser requests confirm both B2C projection POSTs. | Broader frontend-api audit remains outside this domain. |
| `frontend/src/i18n/natalChart.ts` / `disclaimerTitle`, `legalNoticeLines` | used | E-010, E-014, E-015, E-019 | Disclaimer is app-owned and visible; tests assert payload disclaimer is not used. | Projection panel copy is not yet equally i18n-owned. |
| `frontend/src/tests/natalInterpretation.test.tsx` | test-only | E-015 | Test owner covers projection success/loading/empty/API error/entitlement/degraded/disclaimer states. | DOM tests do not replace browser QA for layout. |
| `frontend/src/tests/NatalChartPage.test.tsx` | test-only | E-015, E-016 | Page tests cover `/natal` routing and integration states. | Browser-specific visual issues require E-019. |
| `frontend/src/tests/component-architecture-guards.test.ts` | test-only | E-016 | Guard owner blocks old component ownership paths and API ownership drift under presentational components. | None for audited scope. |
| `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/00-story.md` | out-of-domain | E-001 | Story contract source only; not modified by this audit. | Story remains `ready-to-dev` because this run produced audit artifacts, not implementation evidence. |
| `_story_briefs/cs-307-audit-ux-natal-apres-wiring-projections.md` | out-of-domain | E-002 | Brief source only; not modified by this audit. | File was already untracked before this audit. |
| `_condamad/stories/regression-guardrails.md` | out-of-domain | E-003 | Consulted for applicable invariants; no update justified. | No new durable invariant was added. |

## Closure Analysis

Active implementation findings after current evidence:

- F-001 remains active for wording ownership and product clarity.

Findings closed by current evidence:

- Layout overlap for success projections is closed for desktop, tablet, and mobile under controlled browser evidence (E-019).
- Projection transport bypass is closed for the audited surface by negative scan and source ownership evidence (E-009, E-012, E-013).
- Inline-style regression is closed for audited TSX owners by negative scan (E-011).
- Disclaimer visibility and app ownership are closed for current implementation by source, tests, and browser evidence (E-010, E-014, E-015, E-019).

Exhaustive active surface for F-001:

- Application files: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`; `frontend/src/i18n/natalChart.ts`; `frontend/src/features/natal-chart/NatalInterpretation.css` only if copy changes cause wrapping defects.
- Governance/test files: `frontend/src/tests/natalInterpretation.test.tsx`; `frontend/src/tests/NatalChartPage.test.tsx`; `frontend/src/tests/astrology-i18n.test.ts` if i18n ownership changes require coverage.
- Deferred non-domain concerns: plan differentiation (CS-309), manual profile diversity (CS-310), analytics/degraded observability (CS-311), backend payload wording.

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: no duplicate projection transport or rendering owner was found; symbols are routed through API owner, feature owner, presentational owner, and tests (E-013).
- No Legacy: no shim, alias, fallback renderer, or direct endpoint bypass was found in the audited surface (E-011, E-012, E-013).
- Mono-domain: `/natal` UX remains in existing page, feature, component, CSS, API, and test owners. Backend and plan policy remain out of domain.
- Dependency direction: presentational rendering does not own API transport; `NatalInterpretationSection` owns query orchestration and passes view state down (E-006, E-007, E-016).

## Validation Commands

| Command | Result | Evidence |
|---|---|---|
| `node _condamad/audits/frontend-ux-natal-projections/2026-05-26-0622/browser-qa.mjs` | PASS | E-019 |
| `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage` | PASS | E-015 |
| `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi` | PASS | E-016 |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | PASS | E-017 |
| `.\node_modules\.bin\tsc.cmd --noEmit -p tsconfig.lint.json` | PASS | E-018 |
| `.\node_modules\.bin\tsc.cmd --noEmit -p tsconfig.node.json` | PASS | E-018 |
| `pnpm lint` | LIMITATION | E-018 |


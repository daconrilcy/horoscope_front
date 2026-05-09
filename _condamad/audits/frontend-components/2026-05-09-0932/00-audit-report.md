<!-- Rapport du nouvel audit CONDAMAD frontend components. -->

# Audit Report - frontend-components

## Scope

- Domain key: `frontend-components`
- Audit date: `2026-05-09-0932`
- Archetype: `dependency-direction-audit`, `legacy-surface-audit`, `test-guard-coverage-audit`, plus mandatory No Legacy / DRY checks.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`.
- Audited surface: follow-up surfaces from `_condamad/audits/frontend-components/2026-05-09-0031`: exact API-owning component containers, CS-117 auth relocation, CS-118 natal relocation, CS-119 test-only component deletion, component allowlists, component guards, and targeted validation commands.
- Explicit non-goal: this is not a full fresh semantic review of all 77 current TSX files under `frontend/src/components/**`.

## Expected Responsibility

`frontend/src/components/**` should remain a reusable component layer. Runtime API/feature orchestration should live in feature, page, layout, or route-owner namespaces. Any temporary exception must be exact, guarded, and have an exit condition. Deleted test-only surfaces must not return through files, tests, imports, CSS, wrappers, aliases, fallbacks, or allowlist entries.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-components/2026-05-09-0031`
- `_condamad/stories/CS-117-migrer-containers-auth-api-vers-feature-auth`
- `_condamad/stories/CS-118-relocate-natal-interpretation-feature-owner`
- `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime`
- `_condamad/stories/regression-guardrails.md`

Applicable guardrails: `RG-069`, `RG-070`, `RG-071`, `RG-072`, `RG-073`, `RG-074`, plus design-system guardrails touched by CS-119 (`RG-047`, `RG-048`, `RG-050`, `RG-056`, `RG-057`).

## Closure Ledger

| Prior item | Classification | Current evidence | Guardrail |
|---|---|---|---|
| 2026-05-09-0031 F-001 auth slice | `closed` | E-003, E-011, E-015, E-017 | RG-069, RG-070 |
| 2026-05-09-0031 F-001 non-auth runtime API-owner slices | `still-active` | E-010, E-011, E-015 | RG-069 |
| 2026-05-09-0031 F-003 / natal relocation | `closed` | E-004, E-006, E-007, E-014, E-015 | RG-071, RG-073 |
| 2026-05-09-0031 F-004 / test-only surfaces | `closed` | E-005, E-008, E-009, E-016 | RG-072, RG-074 |
| Component `@ts-nocheck` risk | `closed` | E-013, E-015 | RG-070 |

## Domain Closure Status

Domain closure status: `phased-with-map`.

The corrected auth, natal, and test-only deletion surfaces are closed. The component domain is not fully closed because active API/feature imports remain under `frontend/src/components/**`. The full remaining map is finite and listed in `03-story-candidates.md`.

## Executive Finding Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 0 |
| Low | 0 |
| Info | 3 |

## Active Findings

One active implementation finding remains:

- `F-001`: remaining API-owning component surfaces are still active.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/features/auth/SignInForm.tsx` | used | E-003, E-017 | Canonical auth feature owner after CS-117. | Out-of-components target inspected to prove closure. |
| `frontend/src/features/auth/SignUpForm.tsx` | used | E-003, E-017 | Canonical auth feature owner after CS-117. | Out-of-components target inspected to prove closure. |
| `frontend/src/features/auth/SignUpForm.css` | used | E-003, E-017 | CSS colocated with canonical auth feature owner. | Out-of-components target inspected to prove closure. |
| `frontend/src/components/SignInForm.tsx` | delete-candidate | E-003 | Old auth component path is deleted and has canonical replacement `frontend/src/features/auth/SignInForm.tsx`. | File absent; row records closure of prior surface. |
| `frontend/src/components/SignUpForm.tsx` | delete-candidate | E-003 | Old auth component path is deleted and has canonical replacement `frontend/src/features/auth/SignUpForm.tsx`. | File absent; row records closure of prior surface. |
| `frontend/src/components/SignUpForm.css` | delete-candidate | E-003 | Old auth CSS path is deleted and has canonical replacement under `features/auth`. | File absent; row records closure of prior surface. |
| `frontend/src/features/natal-chart/NatalInterpretation.tsx` | used | E-004, E-014, E-015 | Canonical natal feature owner after CS-118; page/tests import this path. | Out-of-components target inspected to prove closure. |
| `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` | used | E-004, E-014, E-015 | Canonical API/feature-consuming persona selector after CS-118. | Out-of-components target inspected to prove closure. |
| `frontend/src/features/natal-chart/NatalInterpretation.css` | used | E-004 | CSS colocated with canonical natal feature owner. | Out-of-components target inspected to prove closure. |
| `frontend/src/components/NatalInterpretation.tsx` | delete-candidate | E-004, E-006, E-007 | Old natal component owner is deleted with canonical replacement under `features/natal-chart`; no shim or stale allowlist row remains. | File absent; row records closure of prior surface. |
| `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | delete-candidate | E-004, E-006, E-007 | Old API/feature-consuming selector path is deleted with canonical replacement under `features/natal-chart`. | File absent; row records closure of prior surface. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | used | E-004, E-015 | Presentational child remains API-free and consumed by canonical feature owner. | This audit did not re-review rendering semantics. |
| `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx` | used | E-004, E-015 | Presentational child remains API-free and tested. | This audit did not re-review rendering semantics. |
| `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx` | used | E-004, E-015 | Presentational child remains API-free and consumed by canonical feature owner. | This audit did not re-review rendering semantics. |
| `frontend/src/components/AdminGuard.tsx` | used | E-010, E-011, E-015 | Active exact API-owning component exception; must move to route/admin owner to close F-001. | Runtime consumer classification inherited from prior guarded exception and current passing tests. |
| `frontend/src/components/B2BReconciliationPanel.tsx` | used | E-010, E-011, E-015 | Active exact enterprise/B2B API-owning component exception. | Runtime consumer classification inherited from prior guarded exception and current passing tests. |
| `frontend/src/components/EnterpriseCredentialsPanel.tsx` | used | E-010, E-011, E-015 | Active exact enterprise API-owning component exception. | Runtime consumer classification inherited from prior guarded exception and current passing tests. |
| `frontend/src/components/SupportOpsPanel.tsx` | used | E-010, E-011, E-015 | Active exact admin ops/support API-owning component exception. | Runtime consumer classification inherited from prior guarded exception and current passing tests. |
| `frontend/src/components/dashboard/useDashboardAstroSummary.ts` | used | E-010, E-011, E-015 | Active exact dashboard API hook exception under components. | Should move with dashboard summary owner. |
| `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` | used | E-010, E-015 | Container depends on dashboard hook path and remains part of the dashboard slice. | Text scan hit is through `refetch`; audit ties it to `useDashboardAstroSummary`. |
| `frontend/src/components/layout/BottomNav.tsx` | used | E-010, E-011, E-015 | Active exact layout auth-state API exception. | Should become API-free or move to layout owner. |
| `frontend/src/components/layout/Header.tsx` | used | E-010, E-011, E-015 | Active exact layout auth-state API exception. | Should become API-free or move to layout owner. |
| `frontend/src/components/layout/Sidebar.tsx` | used | E-010, E-011, E-015 | Active exact layout auth-state API exception. | Should become API-free or move to layout owner. |
| `frontend/src/components/settings/DeleteAccountModal.tsx` | used | E-010, E-011, E-015 | Active exact settings/privacy API-owning component exception. | Should move to settings/privacy owner. |
| `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | test-only | E-010, E-011, E-015 | Test-only type import from API billing remains as exact exception. | Should extract neutral type or adjust fixture in F-001 closure. |
| `frontend/src/components/dashboard/DashboardCard.tsx` | intentional-public-export | E-012, E-016 | Current usage allowlist classifies it as public dashboard/UI export. | Runtime consumer may remain absent by design. |
| `frontend/src/components/icons/DashboardIcons.tsx` | intentional-public-export | E-012, E-016 | Current usage allowlist classifies named icons as public dashboard icon export. | Runtime consumer may remain absent by design. |
| `frontend/src/components/ui/Form/FormField.tsx` | intentional-public-export | E-012, E-016 | Current usage allowlist classifies it as public Form primitive export. | Runtime consumer may remain absent by design. |
| `frontend/src/components/ui/Card/Card.tsx` | intentional-public-export | E-012, E-016 | Current usage allowlist classifies it as public Card primitive export. | Runtime consumer may remain absent by design. |
| `frontend/src/components/B2BAstrologyPanel.tsx` and CS-119 deleted peers | delete-candidate | E-005, E-008, E-009, E-016 | Deleted after user decision; zero active symbol/import/CSS hits and no stale allowlist rows. | Row groups deleted peers listed exactly in CS-119 after artifact. |
| `frontend/src/components/prediction/DayPredictionCard.tsx` and `TurningPointsList.tsx` | delete-candidate | E-005, E-008, E-009, E-016 | Deleted prediction test-only surfaces; zero active hits. | File absent; row records closure of prior surface. |

## Exhaustive Active Surface

Application files with pending implementation work are exactly the F-001 surfaces listed in `03-story-candidates.md`.

Governance/test files with pending implementation work:

- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- tests for each moved feature/page slice

Deferred non-domain context: none. Implementation may split by target owner, but the component-domain closure map is complete for current evidence.

## Validation

Executed successfully:

- `npm run test -- component-usage component-architecture natalInterpretation NatalChartPage`
- `npm run test -- component-usage component-architecture design-system visual-smoke`
- `npm run lint`

Audit validation was executed after creating these artifacts; see final response for status.

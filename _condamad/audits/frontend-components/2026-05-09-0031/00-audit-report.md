<!-- Rapport d'audit CONDAMAD de continuite du domaine frontend components. -->

# Audit Report - frontend-components

## Scope

- Domain key: `frontend-components`
- Audit date: `2026-05-09-0031`
- Archetype: `dependency-direction-audit`, `legacy-surface-audit`, `test-guard-coverage-audit`, and mandatory No Legacy / DRY checks.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`.
- Audited surface: continuity closure surfaces from `CS-113` to `CS-116`: component API/feature exceptions, component `@ts-nocheck` suppressions, `NatalInterpretation` split files, component usage exceptions, representative deleted surfaces, related component guard tests under `frontend/src/tests/**`, and story evidence artifacts.
- Explicit non-goal: this is not a fresh exhaustive re-audit of every file under `frontend/src/components/**`. Untouched component files outside the prior findings remain covered by the existing guard suites and should be re-audited only in a new full-domain audit.

## Expected Responsibility

`frontend/src/components` remains a reusable UI/component layer. API-owning or feature-owning components may remain only when exact, owned, tested, and guarded with a documented exit condition. Unused-looking component files must be runtime-used, public library exports, test-only, removed, or explicitly blocked by a user decision.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-components/2026-05-08-2303`
- `_condamad/stories/CS-113-classer-converger-composants-consommateurs-api`
- `_condamad/stories/CS-114-supprimer-suppressions-typescript-composants`
- `_condamad/stories/CS-115-decomposer-natal-interpretation-owner`
- `_condamad/stories/CS-116-classer-fermer-composants-non-consommes`
- `_condamad/stories/regression-guardrails.md`

Applicable guardrails: `RG-069`, `RG-070`, `RG-071`, `RG-072`, plus styling guardrails `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-056`, and `RG-057`.

## Closure Ledger

| Prior finding | Classification | Current evidence | Guardrail |
|---|---|---|---|
| 2026-05-08-2303 F-001 | `closed-with-guarded-residuals` | E-001, E-003, E-006, E-007 | RG-069 |
| 2026-05-08-2303 F-002 | `closed` | E-002, E-006, E-007 | RG-070 |
| 2026-05-08-2303 F-003 | `closed` | E-004, E-006, E-007 | RG-071 |
| 2026-05-08-2303 F-004 | `still-closed` | E-006, E-007 | RG-047 to RG-050 |
| 2026-05-08-2303 F-005 | `closed-with-classified-residuals` | E-005, E-006, E-007, E-008 | RG-072 |

## Domain Closure Status

Domain closure status: `closed` for the audited continuity scope only.

Full-domain status: not assessed in this follow-up audit. A fresh exhaustive `frontend-components` audit would need to inventory every current component file separately.

No in-domain implementation story remains required to close the active findings from the 2026-05-08 component audit. Remaining API/feature imports and unused-looking files inside the audited continuity surface are exact, owned, guarded, and have exit conditions. They are residual convergence debt, not unclassified implementation findings in this continuity audit.

## Executive Finding Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 1 |
| Info | 4 |

## Active Findings

No active in-domain implementation finding remains.

The only new item is `F-001`, a Low convergence note: 20 exact API/feature-owning runtime component surfaces plus 1 test type-only exception remain by design in `COMPONENT_API_IMPORT_EXCEPTIONS`. Their guard is passing, but their exit conditions point to future feature/page relocation when those owners are available.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/components/AdminGuard.tsx` | used | E-001, E-003, E-006, E-011 | Exact API-owning container exception, owner `admin routing`, guarded by component architecture tests and imported by runtime routes. | Future relocation to route-level guard remains an exit condition. |
| `frontend/src/components/B2BAstrologyPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as enterprise dashboard test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/B2BBillingPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as enterprise dashboard test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/B2BEditorialPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as enterprise dashboard test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/B2BReconciliationPanel.tsx` | used | E-001, E-003, E-006, E-011 | Exact API-owning container exception for enterprise dashboard reconciliation; runtime page import exists. | Runtime behavior beyond import reachability was covered by existing focused tests, not browser execution. |
| `frontend/src/components/B2BUsagePanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as enterprise dashboard test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/EnterpriseCredentialsPanel.tsx` | used | E-001, E-003, E-006, E-011 | Exact API-owning container exception, owner `enterprise dashboard`, imported by runtime routes. | Future feature owner is not yet created. |
| `frontend/src/components/NatalInterpretation.tsx` | used | E-001, E-004, E-006, E-011 | Narrow container remains the classified API/runtime owner for natal interpretation and is imported by `NatalChartPage`. | Exit condition remains relocation to a natal feature owner. |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | used | E-004, E-006 | Presentational child extracted from `NatalInterpretation`; architecture guard verifies no API/feature ownership. | None. |
| `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx` | used | E-004, E-006 | Extracted evidence helpers/tags with focused tests. | None. |
| `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx` | used | E-004, E-006 | Extracted menu/modal/skeleton/error rendering, API-free by guard. | None. |
| `frontend/src/components/natal-interpretation/NatalInterpretationPersonaSelector.tsx` | used | E-001, E-004, E-006 | Exact sub-container exception for astrologer selection. | Exit condition follows natal feature relocation. |
| `frontend/src/components/OpsMonitoringPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as admin operations test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/OpsPersonaPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as admin operations test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/PrivacyPanel.tsx` | test-only | E-001, E-005, E-006 | Exact API exception and usage exception; retained as settings privacy test-only surface. | Product may later decide to restore runtime navigation or delete. |
| `frontend/src/components/SignInForm.tsx` | used | E-001, E-003, E-006, E-011 | Exact auth form container exception, imported by `LoginPage`. | Exit condition is relocation under auth feature. |
| `frontend/src/components/SignUpForm.tsx` | used | E-001, E-003, E-006, E-011 | Exact auth form container exception, imported by `RegisterPage`. | Exit condition is relocation under auth feature. |
| `frontend/src/components/SupportOpsPanel.tsx` | used | E-001, E-003, E-006, E-011 | Exact API-owning container exception, owner `admin operations`, imported by runtime routes. | Future feature owner is not yet created. |
| `frontend/src/components/dashboard/useDashboardAstroSummary.ts` | used | E-001, E-003, E-006, E-011 | Exact dashboard hook exception with owner and runtime consumer in `DashboardHoroscopeSummaryCardContainer`. | Exit condition is relocation under dashboard hooks/feature. |
| `frontend/src/components/layout/Header.tsx` | used | E-001, E-003, E-006, E-011 | Exact layout container exception for auth state and imported by `AppLayout`. | Exit condition is provider/props from route-level layout. |
| `frontend/src/components/layout/Sidebar.tsx` | used | E-001, E-003, E-006, E-011 | Exact layout container exception for auth state and imported by `AppLayout`. | Exit condition is provider/props from route-level layout. |
| `frontend/src/components/layout/BottomNav.tsx` | used | E-001, E-003, E-006, E-011 | Exact layout container exception for auth state and imported by `AppLayout`. | Exit condition is provider/props from route-level layout. |
| `frontend/src/components/settings/DeleteAccountModal.tsx` | used | E-001, E-003, E-006, E-011 | Exact settings privacy container exception and imported by `AccountSettings`. | Exit condition is relocation under settings/privacy. |
| `frontend/src/components/DailyInsightsSection.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this daily UI surface as test-only with owner and exit condition. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/MiniInsightCard.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this daily UI surface as test-only through `DailyInsightsSection`. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/ConstellationSVG.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this visual surface as test-only through `HeroHoroscopeCard`. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/HeroHoroscopeCard.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this dashboard/daily UI surface as test-only with owner and exit condition. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/TodayHeader.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this daily/dashboard UI surface as test-only with owner and exit condition. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/prediction/DayPredictionCard.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this prediction component as test-only. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/prediction/TurningPointsList.tsx` | test-only | E-005, E-006 | Usage allowlist classifies this prediction component as test-only. | Product may later decide whether to reattach or remove. |
| `frontend/src/components/dashboard/DashboardCard.tsx` | intentional-public-export | E-005, E-006 | Usage allowlist classifies this as a dashboard public library/barrel export. | Runtime consumers may still be absent. |
| `frontend/src/components/icons/DashboardIcons.tsx` | intentional-public-export | E-005, E-006 | Usage allowlist classifies named dashboard icons as a public export surface. | Runtime consumers may still be absent. |
| `frontend/src/components/ui/Card/Card.tsx` | intentional-public-export | E-005, E-006 | Usage allowlist classifies this as a UI primitive public export. | Runtime consumers may still be absent. |
| `frontend/src/components/ui/Form/FormField.tsx` | intentional-public-export | E-005, E-006 | Usage allowlist classifies this as a Form primitive public export. | Runtime consumers may still be absent. |

## Closed Deleted Surfaces

These are not active file usage classifications because the files no longer exist in the repository. They are closure evidence for `CS-116`.

| Surface | Closure status | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/components/prediction/CategoryGrid.tsx` | deleted | E-008, E-010 | Representative remove-classified prediction component is absent. | Representative sample; complete deletion list remains in CS-116 artifacts. |
| `frontend/src/components/prediction/DayPredictionCardContainer.tsx` | deleted | E-008, E-010 | Representative remove-classified prediction component is absent. | Representative sample; complete deletion list remains in CS-116 artifacts. |
| `frontend/src/components/prediction/DecisionWindowsSection.tsx` | deleted | E-008, E-010 | Representative remove-classified prediction component is absent. | Representative sample; complete deletion list remains in CS-116 artifacts. |

## Exhaustive Active Surface

Application files with pending implementation work: none.

Governance/test files with pending implementation work: none.

Deferred non-domain context:

- Feature/page relocation of exact component containers belongs to future `frontend-features`, `frontend-auth`, `frontend-settings`, `frontend-layouts`, or route-owner work.
- Product decisions about reattaching or deleting test-only UI panels are deferred until those pages/features are actively scoped.

## Validation

Executed successfully:

- `npm run test -- component-architecture component-usage natalInterpretation components`
- `npm run lint`

Audit validation was executed after creating these artifacts; see final response for status.

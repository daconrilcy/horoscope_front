<!-- Candidats stories issus de l'audit CONDAMAD frontend components. -->

# Story Candidates - frontend-components

## Exhaustive Files To Modify

### F-001

Application files selected by the full affected surface rule:

- Every `frontend/src/components/**/*.ts` and `frontend/src/components/**/*.tsx` file matching `from "../api"`, `from "../../api"`, `from "@api"`, `apiFetch(`, `fetch(`, `axios`, `from "../features"`, `from "../../features"`, or `from "@features"`.
- Current exact hits: `AdminGuard.tsx`, `B2BAstrologyPanel.tsx`, `B2BBillingPanel.tsx`, `B2BEditorialPanel.tsx`, `B2BReconciliationPanel.tsx`, `B2BUsagePanel.tsx`, `EnterpriseCredentialsPanel.tsx`, `NatalInterpretation.tsx`, `OpsMonitoringPanel.tsx`, `OpsPersonaPanel.tsx`, `PrivacyPanel.tsx`, `SignInForm.tsx`, `SignUpForm.tsx`, `SupportOpsPanel.tsx`, `dashboard/useDashboardAstroSummary.ts`, `layout/Header.tsx`, `layout/Sidebar.tsx`, `layout/BottomNav.tsx`, `settings/DeleteAccountModal.tsx`.

Governance/test files:

- `frontend/src/tests/component-architecture-allowlist.ts` or equivalent.
- `frontend/src/tests/component-architecture-guards.test.ts` or equivalent.

### F-002

Application files:

- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/components/OpsMonitoringPanel.tsx`
- `frontend/src/components/SupportOpsPanel.tsx`
- `frontend/src/components/ui/Form/Form.tsx`

Test files:

- `frontend/src/components/ui/Form/Form.test.tsx`

Governance/test files:

- `frontend/src/tests/component-architecture-allowlist.ts` or equivalent.
- `frontend/src/tests/component-architecture-guards.test.ts` or equivalent.

### F-003

Application files:

- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/NatalInterpretation.css`
- New files under a canonical natal interpretation feature or component subfolder if chosen by the implementation story.

Tests:

- `frontend/src/tests/natalInterpretation.test.tsx`
- Any new focused tests for extracted helpers/components.

### F-005

Application files with no external non-test runtime reference in E-011:

- `frontend/src/components/B2BAstrologyPanel.tsx`
- `frontend/src/components/B2BBillingPanel.tsx`
- `frontend/src/components/B2BEditorialPanel.tsx`
- `frontend/src/components/B2BUsagePanel.tsx`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/components/HeroHoroscopeCard.tsx`
- `frontend/src/components/OpsMonitoringPanel.tsx`
- `frontend/src/components/OpsPersonaPanel.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCardContainer.tsx`
- `frontend/src/components/prediction/DecisionWindowsSection.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/components/PrivacyPanel.tsx`
- `frontend/src/components/TodayHeader.tsx`

Barrel-only files requiring explicit classification:

- `frontend/src/components/ui/Form/FormField.tsx`

Manual-review files requiring export-aware classification:

- `frontend/src/components/icons/DashboardIcons.tsx`

Governance/test files:

- `frontend/src/tests/component-usage-allowlist.ts` or equivalent.
- `frontend/src/tests/component-usage-guards.test.ts` or equivalent.

## Candidate Summary

| Candidate | Source finding | Closure intent | Priority |
|---|---|---|---|
| SC-001 | F-001 | phased-with-map | High |
| SC-002 | F-002 | full-closure | High |
| SC-003 | F-003 | full-closure | Medium |
| SC-004 | F-005 | full-closure | Medium |

## SC-001 - Classify or relocate API-owning component containers

- Source finding: F-001
- Suggested story title: Classer et converger les composants frontend consommateurs d'API
- Suggested archetype: component-boundary-convergence
- Primary domain: frontend-components
- Required contracts: `no-legacy-dry-audit-contract`, dependency-direction guard, `RG-050`, `RG-064`, `RG-068`
- Draft objective: Turn the current API-consuming component surface into either explicitly classified containers with exact ownership or relocated feature/page containers, while keeping reusable shared components free of feature/API ownership.
- Closure intent: phased-with-map.
- Must include:
  - Build an exact inventory before and after using the F-001 selection rule.
  - For each hit, choose one route: move to `features/**`, move to page-adjacent owner, split into container plus presentational component, or document a temporary component-container exception.
  - No wildcard allowlist is allowed; each retained exception must name file, owner, reason, exit condition, and validation command.
  - Do not reintroduce legacy barrels, aliases, compatibility wrappers, or duplicate API hooks.
  - Preserve applicable guardrails `RG-050`, `RG-064`, `RG-068`.
- Validation hints:
  - `npm run test -- component-architecture components`
  - `npm run test -- design-system inline-style legacy-style`
  - `npm run lint`
  - Targeted scan: `rg -n 'from ["''](\\.\\./api|\\.\\./\\.\\./api|@/api|@api|\\.\\./features|\\.\\./\\.\\./features|@/features)|apiFetch\\(|fetch\\(|axios' frontend/src/components -g '*.ts' -g '*.tsx'`
- Blockers: Stop if a component's canonical owner cannot be determined; mark that exact file `needs-user-decision` rather than broad-allowlisting the folder.
- Before/after evidence artifacts required:
  - `component-api-imports-before.md`
  - `component-api-imports-after.md`
  - exact allowlist diff or zero-hit scan.
- Ownership routing decisions expected:
  - Admin and B2B panels route to admin or enterprise feature owners unless product chooses shared containers.
  - Auth forms route to auth feature or remain exact container exceptions.
  - Layout auth consumers route to layout domain if they are intentionally shell containers.
- Reintroduction guard requirements:
  - Guard fails for new API or feature imports in `frontend/src/components/**` unless listed in an exact allowlist.
- Stop condition proving no follow-up story is needed:
  - The targeted scan is zero-hit or every hit is exact, owned, tested, and has a dated exit condition.

## SC-002 - Remove or guard component `@ts-nocheck` suppressions

- Source finding: F-002
- Suggested story title: Supprimer les suppressions TypeScript non gardees dans les composants
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-components
- Required contracts: `report-output-contract`, `no-legacy-dry-audit-contract`, `RG-050`
- Draft objective: Remove `@ts-nocheck` from component code and tests, or classify any truly temporary exception with a deterministic guard.
- Closure intent: full-closure.
- Must include:
  - Attempt direct typing fixes in `EnterpriseCredentialsPanel.tsx`, `OpsMonitoringPanel.tsx`, `SupportOpsPanel.tsx`, `ui/Form/Form.tsx`, and `ui/Form/Form.test.tsx`.
  - If a suppression remains, add exact owner, reason, exit condition, and no wildcard exception.
  - Guard `frontend/src/components/**` against any new `@ts-nocheck`.
  - Do not weaken `tsconfig.lint.json` or hide errors through broad `any` conversions.
- Validation hints:
  - `npm run test -- Form EnterpriseCredentialsPanel OpsMonitoringPanel SupportOpsPanel component-architecture`
  - `npm run lint`
  - Targeted scan: `rg -n '@ts-nocheck' frontend/src/components -g '*.ts' -g '*.tsx'`
- Blockers: Stop if a third-party generic typing defect requires a design decision; keep only an exact temporary exception with owner and exit condition.
- Before/after evidence artifacts required:
  - `component-ts-nocheck-before.md`
  - `component-ts-nocheck-after.md`
- Ownership routing decisions expected:
  - Shared UI primitive typing remains under `components/ui`.
  - Ops and enterprise panel typing follows their final owner from SC-001 if relocation occurs first.
- Reintroduction guard requirements:
  - A component architecture test must fail on unallowlisted `@ts-nocheck`.
- Stop condition proving no follow-up story is needed:
  - Zero `@ts-nocheck` under `frontend/src/components/**`, or only exact allowlisted entries with expiring exits and passing guard.

## SC-003 - Decompose `NatalInterpretation` into a bounded owner

- Source finding: F-003
- Suggested story title: Decomposer le composant NatalInterpretation et clarifier son owner
- Suggested archetype: duplicate-responsibility-removal
- Primary domain: frontend-components
- Required contracts: `no-legacy-dry-audit-contract`, component-boundary guard, `RG-050`, `RG-057`
- Draft objective: Split `NatalInterpretation.tsx` into a narrow container and focused presentational/helper modules, reducing duplicate ownership between API hooks, feature selection, formatting and rendering.
- Closure intent: full-closure.
- Must include:
  - Extract evidence formatting helpers such as `formatEvidenceId` and `_categorizeEvidence` into a tested helper module.
  - Extract modal/menu, version selector, evidence tags, content blocks, and skeleton/error states into focused components.
  - Decide whether the container belongs under `frontend/src/components/**` as a classified container or under a natal feature owner.
  - Keep `NatalInterpretation.css` or split CSS by extracted component without inline styles.
  - Avoid default-export compatibility aliases and stale re-export paths.
- Validation hints:
  - `npm run test -- natalInterpretation NatalChartPage design-system inline-style legacy-style`
  - `npm run lint`
  - Targeted line-count and import scans for `NatalInterpretation.tsx`.
- Blockers: Stop if product must decide whether natal interpretation is a reusable component or a feature module.
- Before/after evidence artifacts required:
  - `natal-interpretation-before.md`
  - `natal-interpretation-after.md`
  - import ownership diff.
- Ownership routing decisions expected:
  - API orchestration either remains in one classified container or moves to a natal feature owner.
  - Presentational components stay API-free.
- Reintroduction guard requirements:
  - Add component architecture guard coverage for API imports and file-size exception if retained.
- Stop condition proving no follow-up story is needed:
  - `NatalInterpretation.tsx` no longer owns helper formatting, modal internals, feature grid selection and rendering in one file, and all retained responsibility is classified by the component architecture guard.

## SC-004 - Classify and close unused component files

- Source finding: F-005
- Suggested story title: Verifier et fermer les composants frontend non consommes
- Suggested archetype: dead-code-removal
- Primary domain: frontend-components
- Required contracts: `no-legacy-dry-audit-contract`, component usage guard, `RG-050`
- Draft objective: Ensure every component under `frontend/src/components` is either used at runtime, intentionally exported as a public primitive, or removed with tests and imports updated.
- Closure intent: full-closure.
- Must include:
  - Re-run a static usage inventory before changes and save it as evidence.
  - Use symbol/export-aware checks for files whose public exports do not match the filename, especially `DashboardIcons.tsx`.
  - Check named exports, barrels, route imports, dynamic imports, and non-test runtime consumers before deletion.
  - For each F-005 file, classify as `runtime-used`, `public-library-export`, `test-only`, `remove`, or `needs-user-decision`.
  - Remove files classified `remove`, including stale CSS, barrels and tests when applicable.
  - For intentional public exports such as primitive subcomponents, add exact owner and consumer rationale.
  - No wildcard allowlist is allowed; every retained unused-looking file must be listed exactly.
- Validation hints:
  - `npm run test -- components component-usage design-system`
  - `npm run lint`
  - Targeted static inventory over `frontend/src/components/**/*.tsx`, excluding tests and the file itself.
  - Import-aware scan for named exports from barrel files, including `components/icons/index.ts` and `components/ui/Form/index.ts`.
- Blockers: Stop if product must decide whether a panel is temporarily hidden or should be restored to navigation.
- Before/after evidence artifacts required:
  - `component-usage-before.md`
  - `component-usage-after.md`
  - exact remove/retain classification table.
- Ownership routing decisions expected:
  - B2B and ops panels need admin or enterprise owner decisions if retained.
  - Prediction display components need page or prediction feature owner decisions if retained.
  - Barrel-only primitives need explicit public-library classification or removal.
- Reintroduction guard requirements:
  - Guard fails for component files with no runtime reference unless exact allowlist entry exists with owner and exit condition.
- Stop condition proving no follow-up story is needed:
  - Zero unclassified unused or barrel-only component files remain under the usage inventory.

## Deferred Non-Component Context

- Bundle-size warnings belong to a separate `frontend-performance` audit.
- Page route ownership remains in `frontend-react-pages`.
- Layout route hierarchy remains in `frontend-layouts`.

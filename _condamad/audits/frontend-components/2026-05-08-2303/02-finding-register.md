<!-- Registre des constats de l'audit CONDAMAD frontend components. -->

# Finding Register - frontend-components

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | boundary-violation | frontend-components | E-003, E-009 | `frontend/src/components` acts as a second owner for API and feature orchestration instead of staying a reusable component layer. | Classify or relocate API-consuming component containers behind feature or page owners, leaving shared components presentational or explicitly allowlisted. | yes |
| F-002 | High | High | missing-guard | frontend-components | E-004, E-008 | Component files can keep or reintroduce `@ts-nocheck` without a component-domain architecture guard, so TypeScript can silently skip critical surfaces. | Remove the suppressions or create an exact temporary allowlist with owner, reason, exit condition, and a failing guard for new component suppressions. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-components | E-003, E-005, E-009 | `NatalInterpretation.tsx` concentrates API hooks, feature composition, entitlement workflow, formatting, modal behavior, and rendering in one oversized component. | Extract a natal interpretation feature/container boundary and smaller presentational components with focused tests. | yes |
| F-004 | Info | High | missing-test-coverage | frontend-components | E-006, E-007, E-010 | Positive invariant: component styling guardrails for inline styles, CSS fallbacks, No Legacy vocabulary, and UI primitive literals are active and passing. | Keep the existing design-system guardrails mandatory for future component changes. | no |
| F-005 | Medium | Medium | legacy-surface | frontend-components | E-001, E-011 | Component files can stay in the shared component layer even when no runtime consumer exists, creating dead-code and stale-barrel risk. | Classify each unreferenced, barrel-only, or manual-review component as mounted, intentional library export, test-only fixture, remove candidate, or needs-user-decision, then add a guard preventing silent growth. | yes |

## Finding Details

### F-001 - Components own API and feature orchestration

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: frontend-components
- Evidence: E-003, E-009.
- Expected rule: shared components should not become canonical owners for API orchestration or feature workflow unless explicitly classified as containers with guards.
- Actual state: `frontend/src/components` imports API hooks and feature modules from files including `AdminGuard.tsx`, `B2BAstrologyPanel.tsx`, `B2BBillingPanel.tsx`, `B2BEditorialPanel.tsx`, `B2BReconciliationPanel.tsx`, `B2BUsagePanel.tsx`, `EnterpriseCredentialsPanel.tsx`, `NatalInterpretation.tsx`, `OpsMonitoringPanel.tsx`, `OpsPersonaPanel.tsx`, `PrivacyPanel.tsx`, `SignInForm.tsx`, `SignUpForm.tsx`, `SupportOpsPanel.tsx`, `dashboard/useDashboardAstroSummary.ts`, `layout/Header.tsx`, `layout/Sidebar.tsx`, `layout/BottomNav.tsx`, and `settings/DeleteAccountModal.tsx`.
- Impact: `frontend/src/components` acts as a second owner for API and feature orchestration instead of staying a reusable component layer.
- Recommended action: Classify or relocate API-consuming component containers behind feature or page owners, leaving shared components presentational or explicitly allowlisted.
- Story candidate: yes
- Suggested archetype: dependency-direction-audit

### F-002 - Component `@ts-nocheck` suppressions are unguarded

- Severity: High
- Confidence: High
- Category: missing-guard
- Domain: frontend-components
- Evidence: E-004, E-008.
- Expected rule: TypeScript suppressions in component code should be absent or governed by an exact, expiring allowlist and architecture guard.
- Actual state: `EnterpriseCredentialsPanel.tsx`, `OpsMonitoringPanel.tsx`, `SupportOpsPanel.tsx`, and `ui/Form/Form.tsx` contain `@ts-nocheck`; `ui/Form/Form.test.tsx` also contains `@ts-nocheck`. Existing page architecture guardrails keep page suppressions empty, but do not cover component files.
- Impact: Component files can keep or reintroduce `@ts-nocheck` without a component-domain architecture guard, so TypeScript can silently skip critical surfaces.
- Recommended action: Remove the suppressions or create an exact temporary allowlist with owner, reason, exit condition, and a failing guard for new component suppressions.
- Story candidate: yes
- Suggested archetype: test-guard-coverage-audit

### F-003 - `NatalInterpretation` is an oversized multi-owner component

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-components
- Evidence: E-003, E-005, E-009.
- Expected rule: a component may compose UI, but durable workflow decisions, API calls, feature selection and formatting helpers should have narrow owners and focused tests.
- Actual state: `NatalInterpretation.tsx` has 1131 lines, imports multiple API hooks and `../features/astrologers`, defines local data selection helpers, modal/menu components, evidence formatting, entitlement workflow behavior, PDF actions, history deletion, and rendering. `NatalInterpretation.css` has 913 lines.
- Impact: `NatalInterpretation.tsx` concentrates API hooks, feature composition, entitlement workflow, formatting, modal behavior, and rendering in one oversized component.
- Recommended action: Extract a natal interpretation feature/container boundary and smaller presentational components with focused tests.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-004 - Component styling guards are active

- Severity: Info
- Confidence: High
- Category: missing-test-coverage
- Domain: frontend-components
- Evidence: E-006, E-007, E-010.
- Expected rule: component inline-style, CSS fallback, legacy vocabulary, and UI primitive design-system exceptions should remain exact and executable.
- Actual state: the targeted style scans found no unclassified component CSS fallback and only exact inline-style exceptions; `npm run test -- components design-system inline-style legacy-style` passed.
- Impact: Positive invariant: component styling guardrails for inline styles, CSS fallbacks, No Legacy vocabulary, and UI primitive literals are active and passing.
- Recommended action: Keep the existing design-system guardrails mandatory for future component changes.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-005 - Component usage inventory is not closed

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: frontend-components
- Evidence: E-001, E-011.
- Expected rule: every component file in `frontend/src/components` should have a runtime consumer, an intentional public library export, or an explicit classification and exit condition.
- Actual state: the reproducible static inventory in `06-component-usage-inventory.md` found no external non-test reference for `B2BAstrologyPanel`, `B2BBillingPanel`, `B2BEditorialPanel`, `B2BUsagePanel`, `DailyInsightsSection`, `HeroHoroscopeCard`, `OpsMonitoringPanel`, `OpsPersonaPanel`, `CategoryGrid`, `DayPredictionCardContainer`, `DecisionWindowsSection`, `TurningPointsList`, `PrivacyPanel`, and `TodayHeader`. `FormField` is referenced only through `components/ui/Form/index.ts`. `DashboardIcons.tsx` needs manual export-aware review because it exports named icons and has a same-name `SettingsIcon` collision in `pages/AdminPage.tsx`.
- Impact: Component files can stay in the shared component layer even when no runtime consumer exists, creating dead-code and stale-barrel risk.
- Recommended action: Classify each unreferenced, barrel-only, or manual-review component as mounted, intentional library export, test-only fixture, remove candidate, or needs-user-decision, then add a guard preventing silent growth.
- Story candidate: yes
- Suggested archetype: dead-code-removal

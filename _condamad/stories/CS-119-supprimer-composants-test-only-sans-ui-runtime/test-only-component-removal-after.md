<!-- Inventaire apres suppression CS-119 des composants frontend test-only. -->

# CS-119 Test-only Component Removal - After

## Deleted Component Surfaces

| Item | Status | Proof |
|---|---|---|
| `components/B2BAstrologyPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/B2BBillingPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/B2BEditorialPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/B2BUsagePanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/OpsMonitoringPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/OpsPersonaPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/PrivacyPanel.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/DailyInsightsSection.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/MiniInsightCard.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/ConstellationSVG.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/HeroHoroscopeCard.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/TodayHeader.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/prediction/DayPredictionCard.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |
| `components/prediction/TurningPointsList.tsx` | deleted | `Test-Path` => `False`; symbol scan zero-hit |

## Deleted CSS

| Item | Status | Proof |
|---|---|---|
| `components/HeroHoroscopeCard.css` | deleted | `Test-Path` => `False`; CSS scan zero-hit |
| `components/MiniInsightCard.css` | deleted | `Test-Path` => `False`; CSS scan zero-hit |
| `components/prediction/DayPredictionCard.css` | deleted | `Test-Path` => `False`; CSS scan zero-hit |
| `components/prediction/TurningPointsList.css` | deleted | `Test-Path` => `False`; CSS scan zero-hit |

## Deleted Focused Tests

| Item | Status |
|---|---|
| `B2BAstrologyPanel.test.tsx` | deleted |
| `B2BBillingPanel.test.tsx` | deleted |
| `B2BEditorialPanel.test.tsx` | deleted |
| `B2BUsagePanel.test.tsx` | deleted |
| `OpsMonitoringPanel.test.tsx` | deleted |
| `OpsPersonaPanel.test.tsx` | deleted |
| `PrivacyPanel.test.tsx` | deleted |
| `HeroHoroscopeCard.test.tsx` | deleted |
| `MiniInsightCard.test.tsx` | deleted |
| `TodayHeader.test.tsx` | deleted |
| `TurningPointsEnriched.test.tsx` | deleted |
| `day-prediction-card-tone.test.ts` | deleted |

## Adapted Guards And Consumers

- `frontend/src/hooks/useDailyInsights.ts` owns local
  `DailyInsightCardType`; no type-only import from deleted `MiniInsightCard`.
- `frontend/src/tests/component-usage-allowlist.ts` no longer contains
  `test-only` exceptions for deleted files.
- `frontend/src/tests/component-architecture-allowlist.ts` no longer contains
  B2B/ops/privacy API exceptions for deleted files.
- `frontend/src/tests/component-usage-guards.test.ts` rejects reintroduction of
  deleted component, CSS and focused test files.
- `frontend/src/tests/design-system-guards.test.ts` no longer reads deleted CSS
  or deleted source files.
- `frontend/src/tests/visual-smoke.test.tsx` keeps remaining smoke assertions
  without importing deleted components or CSS.
- `frontend/src/App.css` no longer carries the orphan `TodayHeader` style block
  and related variables.

## Preserved Keep Surfaces

The story's explicit keep list remains untouched:

- `frontend/src/components/B2BReconciliationPanel.tsx`
- `frontend/src/components/EnterpriseCredentialsPanel.tsx`
- `frontend/src/components/SupportOpsPanel.tsx`
- `frontend/src/components/settings/DeleteAccountModal.tsx`
- `frontend/src/components/dashboard/DashboardCard.tsx`
- `frontend/src/components/icons/DashboardIcons.tsx`
- `frontend/src/components/ui/Card/Card.tsx`
- `frontend/src/components/ui/Form/FormField.tsx`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/PageErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/SectionErrorBoundary.tsx`
- `frontend/src/components/ErrorBoundary/index.ts`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
- `frontend/src/components/natal-interpretation/**`

## Closure Status

Source finding closure status: `full-closure`.

Known residual in-domain work for CS-119: none. The remaining component-domain
convergence debt concerns runtime-used owners or public-library exports outside
this story scope.

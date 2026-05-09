<!-- Inventaire before des owners API/feature sous components pour CS-120. -->

# Component API Remaining Before - CS-120

Captured before frontend relocation work in this execution, from source audit
`E-010` and pre-edit targeted `rg` output.

## Current API / Feature Owners Under `frontend/src/components/**`

| Batch | Component surface before | API / feature dependency | Known first-party consumers before | Current tests before | Proposed canonical owner |
|---|---|---|---|---|---|
| admin-guard | `frontend/src/components/AdminGuard.tsx` | `useAccessTokenSnapshot`, `useAuthMe`, `Navigate`, route auth orchestration | `frontend/src/app/routes.tsx` | `frontend/src/tests/router.test.tsx` | `frontend/src/app/guards/AdminGuard.tsx` |
| enterprise-b2b | `frontend/src/components/B2BReconciliationPanel.tsx` | `../api/b2bReconciliation`, admin i18n, mutation/query orchestration | `frontend/src/pages/admin/ReconciliationAdmin.tsx`, tests | `frontend/src/tests/B2BReconciliationPanel.test.tsx` | `frontend/src/features/enterprise/components/B2BReconciliationPanel.tsx` |
| enterprise-b2b | `frontend/src/components/EnterpriseCredentialsPanel.tsx` | `../api/enterpriseCredentials`, credentials query/mutations | `frontend/src/app/routes.tsx`, tests | `frontend/src/tests/EnterpriseCredentialsPanel.test.tsx` | `frontend/src/features/enterprise/components/EnterpriseCredentialsPanel.tsx` |
| support-ops | `frontend/src/components/SupportOpsPanel.tsx` | `@api` support ops hooks and mutation orchestration | `frontend/src/app/routes.tsx`, tests | `frontend/src/tests/SupportOpsPanel.test.tsx` | `frontend/src/features/support/components/SupportOpsPanel.tsx` |
| settings-privacy | `frontend/src/components/settings/DeleteAccountModal.tsx` | `../../api/privacy`, auth token clearing, router navigation | `frontend/src/pages/settings/AccountSettings.tsx` | Settings targeted tests from story plan | `frontend/src/pages/settings/components/DeleteAccountModal.tsx` |
| dashboard-summary | `frontend/src/components/dashboard/useDashboardAstroSummary.ts` | `../../api/useDailyPrediction`, `../../api/useBirthData`, auth subject parsing | `DashboardHoroscopeSummaryCardContainer` | `DashboardPage` targeted tests from story plan | `frontend/src/features/dashboard/hooks/useDashboardAstroSummary.ts` |
| dashboard-summary | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` | `useAccessTokenSnapshot`, TanStack query prefetch and dashboard hook | `frontend/src/pages/DashboardPage.tsx` | `DashboardPage` targeted tests from story plan | `frontend/src/features/dashboard/components/DashboardHoroscopeSummaryCardContainer.tsx` |
| layout-auth | `frontend/src/components/layout/BottomNav.tsx` | `useAccessTokenSnapshot`, `useAuthMe`, role-based nav | `frontend/src/layouts/AppLayout.tsx`, tests | `frontend/src/tests/BottomNavPremium.test.tsx` | layout owner or prop-driven presentational component |
| layout-auth | `frontend/src/components/layout/Header.tsx` | `useAccessTokenSnapshot`, `useAuthMe`, user menu state | `frontend/src/layouts/AppLayout.tsx`, tests | `frontend/src/tests/layout/Header.test.tsx` | layout owner or prop-driven presentational component |
| layout-auth | `frontend/src/components/layout/Sidebar.tsx` | `useAccessTokenSnapshot`, `useAuthMe`, TanStack query prefetch | `frontend/src/layouts/AppLayout.tsx`, tests | `frontend/src/tests/layout/Sidebar.test.tsx` | layout owner or prop-driven presentational component |
| ui-test-type | `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | Type-only `UpgradeHint` import from `../../../api/billing` | Test only | `UpgradeCTA` tests | Local structural fixture or neutral UI billing test contract |

## Exception Register Before

`frontend/src/tests/component-architecture-allowlist.ts` contained exact rows
for:

- `components/AdminGuard.tsx`
- `components/B2BReconciliationPanel.tsx`
- `components/EnterpriseCredentialsPanel.tsx`
- `components/SupportOpsPanel.tsx`
- `components/dashboard/useDashboardAstroSummary.ts`
- `components/layout/BottomNav.tsx`
- `components/layout/Header.tsx`
- `components/layout/Sidebar.tsx`
- `components/settings/DeleteAccountModal.tsx`
- `components/ui/UpgradeCTA/UpgradeCTA.test.tsx`

No wildcard or folder-wide exception was observed before implementation.

## Pre-Edit Evidence Commands

- `git status --short` showed CS-120 and the audit folder as pre-existing
  untracked story/audit work.
- Targeted symbol scan found old component imports in `app/routes.tsx`,
  `pages/admin/ReconciliationAdmin.tsx`, `pages/DashboardPage.tsx`,
  `pages/settings/AccountSettings.tsx`, and panel/layout tests.
- `rg --files frontend/src/components | rg "AdminGuard|B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel|DeleteAccountModal|useDashboardAstroSummary|DashboardHoroscopeSummaryCardContainer"`
  listed the old component owner files before deletion work.

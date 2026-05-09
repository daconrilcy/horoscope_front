<!-- Carte de migration des owners API/feature components pour CS-120. -->

# Component API Owner Migration - CS-120

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `frontend/src/components/AdminGuard.tsx` | route guard | historical-facade after repoint | `app/routes.tsx` | `frontend/src/app/guards/AdminGuard.tsx` | delete | router tests pass; old-path scan zero-hit | low |
| `frontend/src/components/AdminGuard.css` | CSS colocated with old guard | historical-facade after repoint | old guard only | `frontend/src/app/guards/AdminGuard.css` | delete | lint and route tests pass | low |
| `frontend/src/components/B2BReconciliationPanel.tsx` | enterprise panel container | historical-facade after repoint | `pages/admin/ReconciliationAdmin.tsx`, tests | `frontend/src/features/enterprise/B2BReconciliationPanel.tsx` | delete | panel tests pass; old-path scan zero-hit | low |
| `frontend/src/components/EnterpriseCredentialsPanel.tsx` | enterprise credentials container | historical-facade after repoint | `app/routes.tsx`, tests | `frontend/src/features/enterprise/EnterpriseCredentialsPanel.tsx` | delete | panel tests pass; old-path scan zero-hit | low |
| `frontend/src/components/SupportOpsPanel.tsx` | support ops container | historical-facade after repoint | `app/routes.tsx`, tests | `frontend/src/features/support/SupportOpsPanel.tsx` | delete | support test pass; old-path scan zero-hit | low |
| `frontend/src/components/dashboard/useDashboardAstroSummary.ts` | dashboard API hook | historical-facade after repoint | dashboard container | `frontend/src/features/dashboard/hooks/useDashboardAstroSummary.ts` | delete | Dashboard tests pass; old-path scan zero-hit | low |
| `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` | dashboard container | historical-facade after repoint | `pages/DashboardPage.tsx` | `frontend/src/features/dashboard/components/DashboardHoroscopeSummaryCardContainer.tsx` | delete | Dashboard tests pass; old-path scan zero-hit | low |
| `frontend/src/components/layout/BottomNav.tsx` | layout navigation | historical-facade after repoint | `layouts/AppLayout.tsx`, tests | `frontend/src/layouts/components/BottomNav.tsx` | delete | BottomNavPremium and layout tests pass | low |
| `frontend/src/components/layout/Header.tsx` | layout header | historical-facade after repoint | `layouts/AppLayout.tsx`, tests | `frontend/src/layouts/components/Header.tsx` | delete | Header tests pass | low |
| `frontend/src/components/layout/Header.css` | layout header CSS | historical-facade after repoint | old header only | `frontend/src/layouts/components/Header.css` | delete | design-system and layout tests pass | low |
| `frontend/src/components/layout/Sidebar.tsx` | layout sidebar | historical-facade after repoint | `layouts/AppLayout.tsx`, tests | `frontend/src/layouts/components/Sidebar.tsx` | delete | Sidebar tests pass | low |
| `frontend/src/components/layout/Sidebar.css` | layout sidebar CSS | historical-facade after repoint | old sidebar only | `frontend/src/layouts/components/Sidebar.css` | delete | design-system and layout tests pass | low |
| `frontend/src/components/settings/DeleteAccountModal.tsx` | settings privacy mutation modal | historical-facade after repoint | `pages/settings/AccountSettings.tsx` | `frontend/src/pages/settings/components/DeleteAccountModal.tsx` | delete | Settings tests pass; old-path scan zero-hit | low |
| `frontend/src/components/settings/DeleteAccountModal.css` | settings modal CSS | historical-facade after repoint | old modal only | `frontend/src/pages/settings/components/DeleteAccountModal.css` | delete | design-system and settings tests pass | low |
| `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` API type import | test type dependency | canonical-active test with neutral fixture | UpgradeCTA test only | `NonNullable<ReturnType<typeof useUpgradeHint>>` local fixture type | replace-consumer | UpgradeCTA tests pass; API type import scan zero-hit | low |

## Closure Result

No batch is `needs-user-decision`. No external import blocker was found. The
old component owner paths were not preserved through wrappers, aliases,
fallbacks, barrels or re-exports.

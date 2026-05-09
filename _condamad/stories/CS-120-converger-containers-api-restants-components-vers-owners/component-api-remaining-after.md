<!-- Inventaire after des owners API/feature sous components pour CS-120. -->

# Component API Remaining After - CS-120

Captured after frontend relocation and main-session validation.

## Final Decisions

| Batch | Old component surface | Final owner | Decision | Proof |
|---|---|---|---|---|
| admin-guard | `frontend/src/components/AdminGuard.tsx` | `frontend/src/app/guards/AdminGuard.tsx` | `delete` old path | `npm run test -- router DashboardPage SettingsPage BottomNavPremium`; zero old-path scan. |
| enterprise-b2b | `frontend/src/components/B2BReconciliationPanel.tsx` | `frontend/src/features/enterprise/B2BReconciliationPanel.tsx` | `delete` old path | `npm run test -- B2BReconciliationPanel EnterpriseCredentialsPanel SupportOpsPanel UpgradeCTA`; zero old-path scan. |
| enterprise-b2b | `frontend/src/components/EnterpriseCredentialsPanel.tsx` | `frontend/src/features/enterprise/EnterpriseCredentialsPanel.tsx` | `delete` old path | Same targeted panel tests; zero old-path scan. |
| support-ops | `frontend/src/components/SupportOpsPanel.tsx` | `frontend/src/features/support/SupportOpsPanel.tsx` | `delete` old path | Targeted support panel test; zero old-path scan. |
| settings-privacy | `frontend/src/components/settings/DeleteAccountModal.tsx` | `frontend/src/pages/settings/components/DeleteAccountModal.tsx` | `delete` old path | `npm run test -- router DashboardPage SettingsPage BottomNavPremium`; zero old-path scan. |
| dashboard-summary | `frontend/src/components/dashboard/useDashboardAstroSummary.ts` | `frontend/src/features/dashboard/hooks/useDashboardAstroSummary.ts` | `delete` old path | Dashboard tests and zero old-path scan. |
| dashboard-summary | `frontend/src/components/dashboard/DashboardHoroscopeSummaryCardContainer.tsx` | `frontend/src/features/dashboard/components/DashboardHoroscopeSummaryCardContainer.tsx` | `delete` old path | Dashboard tests and zero old-path scan. |
| layout-auth | `frontend/src/components/layout/BottomNav.tsx` | `frontend/src/layouts/components/BottomNav.tsx` | `delete` old path | `npm run test -- Header Sidebar AppShell`; `BottomNavPremium` targeted test. |
| layout-auth | `frontend/src/components/layout/Header.tsx` | `frontend/src/layouts/components/Header.tsx` | `delete` old path | Header tests and zero old-path scan. |
| layout-auth | `frontend/src/components/layout/Sidebar.tsx` | `frontend/src/layouts/components/Sidebar.tsx` | `delete` old path | Sidebar tests and zero old-path scan. |
| ui-test-type | `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | local inferred hook return fixture | `replace-consumer` type-only dependency | UpgradeCTA tests and zero-hit `UpgradeHint` API import scan. |

## Allowlist After

`COMPONENT_API_IMPORT_EXCEPTIONS` is an empty exact array. No wildcard,
folder-wide or stale row remains.

## Required Negative Scans

All listed commands were run from `frontend/`; exit code `1` means zero hits and
is expected for these scans.

| Command | Result |
|---|---|
| `rg -n "from [\"'](?:@components/)?(?:B2BReconciliationPanel\|EnterpriseCredentialsPanel\|SupportOpsPanel)[\"']" src -g "*.ts" -g "*.tsx"` | PASS zero-hit |
| `rg -n "components/(?:AdminGuard\|B2BReconciliationPanel\|EnterpriseCredentialsPanel\|SupportOpsPanel)" src -g "*.ts" -g "*.tsx"` | PASS zero-hit |
| `rg -n "components/settings/DeleteAccountModal\|components/dashboard/useDashboardAstroSummary\|components/dashboard/DashboardHoroscopeSummaryCardContainer" src -g "*.ts" -g "*.tsx"` | PASS zero-hit |
| `rg -n "components/(AdminGuard\|B2BReconciliationPanel\|EnterpriseCredentialsPanel\|SupportOpsPanel)" src/tests/component-architecture-allowlist.ts` | PASS zero-hit |
| `rg -n "components/(dashboard/useDashboardAstroSummary\|dashboard/DashboardHoroscopeSummaryCardContainer)" src/tests/component-architecture-allowlist.ts` | PASS zero-hit |
| `rg -n "components/settings/DeleteAccountModal" src/tests/component-architecture-allowlist.ts` | PASS zero-hit |
| `rg -n "import type \\{ UpgradeHint \\} from ['\"]\\.\\.\\/\\.\\.\\/\\.\\.\\/api\\/billing['\"]" src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` | PASS zero-hit |
| `rg -n "apiFetch\\(\|fetch\\(\|axios\|from [\"'](?:@api\|@/api\|.*\\/api\|.*\\/features)" src/components -g "*.ts" -g "*.tsx"` | PASS zero-hit |
| `rg -n "@ts-nocheck" src/components -g "*.ts" -g "*.tsx"` | PASS zero-hit |
| `rg -n "frontend/src/components/AdminGuard\.tsx\|src/components/EnterpriseCredentialsPanel\.tsx\|components/(AdminGuard\|EnterpriseCredentialsPanel\|B2BReconciliationPanel\|SupportOpsPanel\|settings/DeleteAccountModal\|dashboard/useDashboardAstroSummary\|dashboard/DashboardHoroscopeSummaryCardContainer)" docs frontend -g "*.md" -g "*.ts" -g "*.tsx" -g "*.json"` | PASS zero-hit after review fixes |

## Classified Non-Blocking Scan Hits

- `rg -n "style=" src/components src/layouts src/features src/pages/settings -g "*.tsx"`
  returned pre-existing dynamic/style-primitive hits in
  `components/DomainRankingCard.tsx`, `components/prediction/DayTimelineSectionV4.tsx`
  and `components/ui/Skeleton/Skeleton.tsx`. These files were not modified by
  CS-120, and `npm run test -- design-system visual-smoke` passed.
- `rg --files src/components | rg "AdminGuard|B2BReconciliationPanel|EnterpriseCredentialsPanel|SupportOpsPanel|DeleteAccountModal|useDashboardAstroSummary|DashboardHoroscopeSummaryCardContainer|BottomNav|Header|Sidebar"`
  returned `DailyPageHeader` files only; these are unrelated prediction header
  surfaces, not old CS-120 owners.

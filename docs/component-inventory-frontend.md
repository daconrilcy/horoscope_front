# Component Inventory - Frontend

## Pages
- `HomePage.tsx`
- `ChatPage.tsx`
- `NatalChartPage.tsx`

## Core Shell
- `AppShell.tsx`

## Product Feature Panels
- `BillingPanel.tsx`
- `PrivacyPanel.tsx`
- `SupportOpsPanel.tsx`
- `OpsMonitoringPanel.tsx`
- `OpsPersonaPanel.tsx`

## B2B Panels
- `B2BAstrologyPanel.tsx`
- `B2BBillingPanel.tsx`
- `B2BEditorialPanel.tsx`
- `B2BReconciliationPanel.tsx`
- `B2BUsagePanel.tsx`
- `EnterpriseCredentialsPanel.tsx`

## Supporting UI Infrastructure
- API modules in `src/api/` split by domain
- App providers in `src/state/providers.tsx`
- Auth helper in `src/utils/authToken.ts`

## Reuse Notes
- Panel-centric organization favors feature reuse and targeted testing.
- API/domain split in `src/api` is aligned with backend router domains.

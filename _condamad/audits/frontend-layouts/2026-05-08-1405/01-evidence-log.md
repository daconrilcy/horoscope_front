<!-- Journal des preuves de l'audit CONDAMAD sur les layouts frontend. -->

# Evidence Log - frontend-layouts

| ID | Evidence type | Command / Source | Inspected path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | route_table_inventory | `Get-Content frontend/src/app/routes.tsx` and targeted `rg -n` route/layout scan | `frontend/src/app/routes.tsx` | FAIL | Root route maps `/` to `LandingRedirect`, `/login` to `LoginPage`, `/register` to `RegisterPage`; protected branch maps to `AppLayout`; admin branch maps to `AdminPage`. No `RootLayout` or `LandingLayout` route mount is present. |
| E-002 | targeted_forbidden_symbol_scan | `rg -n` scan for `ScopedLandingPage`, `landing-layout`, `LandingPage`, and `Suspense` | `frontend/src/app/guards/LandingRedirect.tsx` | FAIL | `LandingRedirect` imports `LandingPage` and returns a local `.landing-layout` wrapper instead of rendering `LandingLayout`. |
| E-003 | dependency_direction_scan | `rg -n` scan for layout symbols across app, pages, layouts, components and features | `frontend/src/**` | FAIL | `RootLayout` and `LandingLayout` are exported but not route-mounted; `AppLayout` is directly route-mounted; `AdminLayout` is used inside `AdminPage`. |
| E-004 | architecture_guard_inventory | `Get-Content frontend/src/tests/page-architecture-guards.test.ts` and targeted `rg -n` guard scan | `frontend/src/tests/**` | FAIL | Existing guards cover page architecture, CSS and smoke expectations, but no test enforces master layout, principal layout families, or no direct page route without layout. |
| E-005 | test_coverage_inventory | `_condamad/stories/regression-guardrails.md` and `_condamad/audits/frontend-react-pages/2026-05-08-1323/**` | CONDAMAD prior artifacts | PASS | Existing guardrails `RG-064` to `RG-067` remain relevant context but do not close layout hierarchy ownership. |
| E-006 | test_coverage_inventory | `npm run test -- page-architecture App` | `frontend/` | PASS | 5 test files passed, 68 tests passed. This proves current guards pass while the layout hierarchy gap remains unguarded. |
| E-007 | architecture_guard_inventory | `npm run lint` | `frontend/` | PASS | TypeScript lint passes. |
| E-008 | repo_state | `git status --short` | repository root | LIMITATION | Pre-existing user/worktree change observed: `D frontend/lint_output.txt`. Audit artifacts are the only new intended writes. |
| E-009 | route_table_inventory | `rg --files frontend/src/pages -g '*.tsx'` and targeted symbol scan for page files not imported by `routes.tsx` | `frontend/src/pages/**` | FAIL | `HomePage`, `PrivacyPolicyPage`, `billing/BillingSuccessPage`, `billing/BillingCancelPage`, support ticket components, and `AdminPricingPanel` are not route-mounted in `routes.tsx` or explicitly classified as page-adjacent components. |

## Evidence Details

### E-001 - Route table inventory

Relevant source lines:

- `frontend/src/app/routes.tsx:145-146` maps `/` to `<LandingRedirect />`.
- `frontend/src/app/routes.tsx:150` maps `/login` directly to `<LoginPage />`.
- `frontend/src/app/routes.tsx:154` maps `/register` directly to `<RegisterPage />`.
- `frontend/src/app/routes.tsx:157-160` maps a protected `/` branch to `<AppLayout />`.
- `frontend/src/app/routes.tsx:285-287` maps `admin` through `<AdminPage />`.

### E-002 - Landing layout bypass

Relevant source lines:

- `frontend/src/app/guards/LandingRedirect.tsx:5` imports `LandingLayout.css`.
- `frontend/src/app/guards/LandingRedirect.tsx:9-13` declares `ScopedLandingPage` and recreates the `.landing-layout` wrapper.
- `frontend/src/layouts/LandingLayout.tsx:14` exports `LandingLayout`, but the route table does not mount it.

### E-003 - Layout dependency and ownership scan

Relevant source lines:

- `frontend/src/layouts/RootLayout.tsx:4` exports `RootLayout`.
- `frontend/src/layouts/AppLayout.tsx:10-35` owns app shell markup and `StarfieldBackground` directly.
- `frontend/src/layouts/AppLayout.tsx:38-43` exports `AppLayout`.
- `frontend/src/pages/AdminPage.tsx:111-117` wraps admin children in `AdminLayout`.
- `frontend/src/components/layout/EnterpriseLayout.tsx:4-11` is a secondary layout under application routes.

### E-004 - Guard inventory

Relevant source lines:

- `frontend/src/tests/page-architecture-guards.test.ts:26-95` guards `@ts-nocheck`, direct `apiFetch`, public aliases, admin barrel exports and page size.
- `frontend/src/tests/App.test.tsx:160-161` asserts `.landing-layout` exists for `/`, but does not assert `LandingLayout` ownership.
- `frontend/src/tests/visual-smoke.test.tsx:231-232` asserts landing CSS tokens, not route hierarchy.

### E-009 - Page file ownership inventory

Relevant source lines:

- `frontend/src/pages/index.ts:13` exports `HomePage`, but `routes.tsx` does not import or mount it.
- `frontend/src/pages/PrivacyPolicyPage.tsx:9` exports `PrivacyPolicyPage`, but `routes.tsx` does not import or mount it.
- `frontend/src/pages/billing/BillingSuccessPage.tsx:9` exports `BillingSuccessPage`, and `frontend/src/tests/BillingSuccessPage.test.tsx:4` imports it directly, but `routes.tsx` does not mount it.
- `frontend/src/pages/billing/BillingCancelPage.tsx:8` exports `BillingCancelPage`, but `routes.tsx` does not mount it.
- `frontend/src/pages/support/SupportTicketList.tsx`, `SupportTicketForm.tsx`, and `SupportCategorySelect.tsx` live under `pages/support` but are imported by `HelpPage` as components.
- `frontend/src/pages/admin/AdminPricingPanel.tsx:8` exports `AdminPricingPanel`, but it is used by `AdminBillingPage` as a panel, not as a routed page.

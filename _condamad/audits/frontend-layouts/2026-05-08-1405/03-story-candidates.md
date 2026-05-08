<!-- Candidats de stories issus de l'audit CONDAMAD sur les layouts frontend. -->

# Story Candidates - frontend-layouts

## Candidate Summary

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Converger le layout maitre frontend | architecture-guard-hardening | frontend-layouts | none |
| SC-002 | F-002 | Monter la landing via son layout principal | legacy-facade-removal | frontend-layouts | none |
| SC-003 | F-003 | Rattacher les routes auth publiques a un layout | ownership-routing-refactor | frontend-layouts | Decide whether auth belongs to the landing principal family or to an auth secondary layout under landing/application. |
| SC-004 | F-004 | Ajouter les guards de hierarchie layout frontend | architecture-guard-hardening | frontend-layouts | none |
| SC-005 | F-005 | Classer tous les fichiers pages sous un layout owner | ownership-routing-refactor | frontend-layouts | Decide whether billing and privacy pages must be public routes and which principal layout family owns them. |

## SC-001 - Converger le layout maitre frontend

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Converger le layout maitre frontend
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`, existing guardrails `RG-064` to `RG-067`.
- Draft objective: make `RootLayout` the single route-level master layout used by landing, admin and application branches.
- Closure intent: `phased-with-map`
- Must include:
  - Mount `RootLayout` in `frontend/src/app/routes.tsx`.
  - Remove duplicated master shell/background responsibility from principal layouts or make the dependency explicit.
  - Preserve authenticated route behavior and redirects.
  - Preserve `AppLayout` sidebar/header/bottom-nav behavior for application routes.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture App router`
  - New or updated layout hierarchy guard.
- Blockers: none.

## SC-002 - Monter la landing via son layout principal

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Monter la landing via son layout principal
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`.
- Draft objective: remove the active `LandingLayout` bypass and make the public landing route render through `LandingLayout`.
- Closure intent: `full-closure`
- Must include:
  - Replace `ScopedLandingPage` ownership in `LandingRedirect` with a route structure where `LandingLayout` owns the landing wrapper.
  - Keep token-expired cleanup and authenticated redirect behavior.
  - Ensure navbar/footer behavior is intentional for the landing route, or document an explicit product decision if it should not render.
- Validation hints:
  - `npm run test -- App visual-smoke`
  - A targeted scan proving `LandingRedirect` no longer imports `LandingLayout.css` or creates `.landing-layout`.
- Blockers: none.

## SC-003 - Rattacher les routes auth publiques a un layout

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Rattacher les routes auth publiques a un layout
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`.
- Draft objective: ensure `/login` and `/register` have a layout ancestor under the master route.
- Closure intent: `blocked`
- Must include:
  - Decide target ownership for auth pages: landing principal layout, application principal layout, or `AuthLayout` as a secondary layout under one principal family.
  - Route `/login` and `/register` through the selected layout.
  - Keep register/login navigation behavior.
- Validation hints:
  - `npm run test -- App router`
  - New layout hierarchy guard proves no direct page route remains for login/register.
- Blockers: user/product decision needed if auth pages must not show landing navbar/footer and must not share application shell.

## SC-004 - Ajouter les guards de hierarchie layout frontend

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Ajouter les guards de hierarchie layout frontend
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-layouts
- Required contracts: `report-output-contract`, `no-legacy-dry-audit-contract`.
- Draft objective: make the target layout architecture executable as a regression guard.
- Closure intent: `full-closure`
- Must include:
  - Guard that every route leaf rendering a page has a master layout ancestor and one accepted principal layout family.
  - Guard that `RootLayout` is mounted.
  - Guard that `LandingLayout` is not bypassed by local `.landing-layout` wrappers.
  - Exact allowlist only; no wildcard folder exception.
- Validation hints:
  - `npm run test -- page-architecture layout`
  - Targeted scans for `LandingLayout.css` imports outside `LandingLayout.tsx` and `.landing-layout` wrappers outside the layout owner.
- Blockers: none.

## SC-005 - Classer tous les fichiers pages sous un layout owner

- Candidate ID: SC-005
- Source finding: F-005
- Suggested story title: Classer tous les fichiers pages sous un layout owner
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-layouts
- Required contracts: `no-legacy-dry-audit-contract`, `report-output-contract`.
- Draft objective: make every `frontend/src/pages/**/*.tsx` file auditable against the layout rule by routing it, relocating it out of `pages`, or classifying it as an intentional page-adjacent component.
- Closure intent: `phased-with-map`
- Must include:
  - Build an inventory of `frontend/src/pages/**/*.tsx`.
  - Classify each file as `routed-page`, `nested-routed-page`, `page-adjacent-component`, `dead/unmounted-page-candidate`, or `needs-user-decision`.
  - Route true public pages such as billing return and privacy pages under a principal layout family, or document why they are intentionally not reachable.
  - Relocate support/admin panel components out of `pages/**` or add exact ownership classification with a stop condition.
  - Add an exact guard; no wildcard folder allowlist.
- Validation hints:
  - `npm run lint`
  - `npm run test -- page-architecture App router BillingSuccessPage`
  - New inventory guard proving every `pages/**/*.tsx` file is classified.
- Blockers: user/product decision needed for privacy and billing return route visibility if those pages are intended public entrypoints.

## Exhaustive Files To Modify

For `F-001`:

Application files:

- `frontend/src/app/routes.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/AdminLayout.tsx`
- `frontend/src/pages/AdminPage.tsx`

Governance/test files:

- `frontend/src/tests/page-architecture-guards.test.ts`
- Optional: `frontend/src/tests/layout-architecture-guards.test.ts`

For `F-002`:

Application files:

- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/layouts/LandingLayout.tsx`

Governance/test files:

- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- New or extended layout architecture guard.

For `F-003`:

Application files:

- `frontend/src/app/routes.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`

Governance/test files:

- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/router.test.tsx`
- New or extended layout architecture guard.

For `F-004`:

Application files: none.

Governance/test files:

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- Optional: `frontend/src/tests/layout-architecture-guards.test.ts`

For `F-005`:

Application files:

- `frontend/src/app/routes.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/pages/support/SupportTicketForm.tsx`
- `frontend/src/pages/support/SupportCategorySelect.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`
- Any additional `frontend/src/pages/**/*.tsx` file found by the inventory and not already classified.

Governance/test files:

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- Optional: `frontend/src/tests/layout-architecture-guards.test.ts`
- Optional: a page ownership inventory artifact if the project keeps one.

## Required Before / After Evidence

- Before: route inventory proving current direct routes and missing `RootLayout` mount.
- After: route inventory proving root master route and accepted principal layout ancestors.
- Before: scan proving `LandingRedirect` owns a `.landing-layout` wrapper.
- After: scan proving `LandingRedirect` no longer bypasses `LandingLayout`.
- Before: tests pass without enforcing layout hierarchy.
- After: targeted layout guard fails on a local bypass and passes on the final tree.
- Before: page file inventory includes unclassified page files.
- After: every page file is routed, relocated, or exactly classified.

## Deferred Non-Domain Context

- Design-system CSS tokens and fallbacks remain outside this implementation story unless touched by layout markup changes.
- Admin section permissions and admin feature decomposition remain owned by their existing page/admin stories.

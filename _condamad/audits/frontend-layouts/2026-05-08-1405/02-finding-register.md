<!-- Registre des constats de l'audit CONDAMAD sur les layouts frontend. -->

# Finding Register - frontend-layouts

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | frontend-layouts | E-001, E-003 | The master layout rule is not implemented: `RootLayout` exists but no route uses it, and `AppLayout` owns shell/background responsibilities directly. | Mount `RootLayout` as the route-level master layout and move shared shell/background ownership out of principal layouts. | yes |
| F-002 | High | High | duplicate-responsibility | frontend-layouts | E-001, E-002, E-003 | Landing has two active owners: `LandingLayout` exists, while `LandingRedirect` recreates a landing wrapper and bypasses the layout component. | Route landing through `LandingLayout`; keep redirect logic separate from layout ownership. | yes |
| F-003 | High | High | boundary-violation | frontend-layouts | E-001, E-003 | `/login` and `/register` render pages directly, so not every page is backed by a layout owner. | Assign auth/public pages to a principal layout family under the master layout, or classify a dedicated auth secondary layout under that family. | yes |
| F-004 | Medium | High | missing-guard | frontend-layouts | E-004, E-005, E-006, E-007 | Current tests can pass while the requested layout hierarchy is violated. | Add a deterministic guard for master layout usage, principal layout ancestors, and direct page route exceptions. | yes |
| F-005 | High | High | missing-canonical-owner | frontend-layouts | E-001, E-009 | Several `frontend/src/pages/**/*.tsx` files are neither route-mounted nor classified as page-adjacent components, so the "all pages use layouts" rule is not exhaustively enforceable. | Add a page-file ownership inventory and either route, relocate, or explicitly classify every page file. | yes |

## Finding Details

### F-001 - Master layout exists but is not mounted

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-layouts
- Evidence: E-001, E-003.
- Expected rule: all principal layouts rely on one master layout.
- Actual state: `RootLayout` is exported from `frontend/src/layouts/RootLayout.tsx`, but `frontend/src/app/routes.tsx` mounts `LandingRedirect`, direct auth pages, and `AppLayout` branches without `RootLayout`. `AppLayout` directly renders `.app-shell`, `.app-bg`, `StarfieldBackground`, and `.app-bg-container`.
- Impact: The master layout rule is not implemented: `RootLayout` exists but no route uses it, and `AppLayout` owns shell/background responsibilities directly.
- Recommended action: Mount `RootLayout` as the route-level master layout and move shared shell/background ownership out of principal layouts.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
- Closure classification: phased-with-map

### F-002 - Landing layout is bypassed by a local wrapper

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-layouts
- Evidence: E-001, E-002, E-003.
- Expected rule: the landing page uses the landing principal layout.
- Actual state: `LandingLayout` exports the layout and includes navbar, main and footer, but the `/` route renders `LandingRedirect`; `LandingRedirect` lazily imports `LandingPage`, imports only `LandingLayout.css`, and creates its own `.landing-layout` wrapper.
- Impact: Landing has two active owners: `LandingLayout` exists, while `LandingRedirect` recreates a landing wrapper and bypasses the layout component.
- Recommended action: Route landing through `LandingLayout`; keep redirect logic separate from layout ownership.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal
- Closure classification: phased-with-map

### F-003 - Auth routes are direct page routes

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: frontend-layouts
- Evidence: E-001, E-003.
- Expected rule: every page relies on a layout.
- Actual state: `/login` maps directly to `<LoginPage />` and `/register` maps directly to `<RegisterPage />`. `AuthLayout` exists and `NotFoundPage` uses it, but the auth routes do not.
- Impact: `/login` and `/register` render pages directly, so not every page is backed by a layout owner.
- Recommended action: Assign auth/public pages to a principal layout family under the master layout, or classify a dedicated auth secondary layout under that family.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: phased-with-map

### F-004 - No guard enforces the requested layout hierarchy

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-layouts
- Evidence: E-004, E-005, E-006, E-007.
- Expected rule: architecture tests fail if pages bypass layouts or layouts bypass the master layout.
- Actual state: `page-architecture` guards page smells and route aliases, while App and visual smoke tests assert rendered CSS/classes. None validates the route ancestor chain or principal layout ownership.
- Impact: Current tests can pass while the requested layout hierarchy is violated.
- Recommended action: Add a deterministic guard for master layout usage, principal layout ancestors, and direct page route exceptions.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
- Closure classification: phased-with-map

### F-005 - Page file inventory is not fully classified

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-layouts
- Evidence: E-001, E-009.
- Expected rule: every page file is either route-mounted under a layout, a nested route page under a layout, or explicitly classified as page-adjacent/non-route code.
- Actual state: `HomePage`, `PrivacyPolicyPage`, billing return pages, support ticket components, and `AdminPricingPanel` live under `frontend/src/pages/**` without an explicit layout ownership classification. Some are true page components, while others are components stored in a page namespace.
- Impact: Several `frontend/src/pages/**/*.tsx` files are neither route-mounted nor classified as page-adjacent components, so the "all pages use layouts" rule is not exhaustively enforceable.
- Recommended action: Add a page-file ownership inventory and either route, relocate, or explicitly classify every page file.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure classification: phased-with-map

## Closed Prior Findings

No prior `frontend-layouts` audit folder existed. Prior `frontend-react-pages` findings remain closed for their own domain and are not reopened here.

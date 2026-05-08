<!-- Rapport d'audit CONDAMAD sur la hierarchie des layouts frontend. -->

# CONDAMAD Domain Audit - frontend-layouts

Date: 2026-05-08 14:05 Europe/Paris

## Domain

- Domain key: `frontend-layouts`
- Target: `frontend/src/app/routes.tsx`, `frontend/src/app/guards/LandingRedirect.tsx`, `frontend/src/layouts/**`, `frontend/src/components/layout/**`, and pages directly impacted by route-level layout ownership.
- Archetypes: `legacy-surface-audit`, `dependency-direction-audit`, `test-guard-coverage-audit`, `no-legacy-dry-audit-contract`.
- Mode: read-only application audit. Only audit artifacts were written.

## Expected Rules

- Every rendered page must be reached through a layout owner.
- Every layout must rely on one master layout.
- The three principal layout families must be explicit and route-mounted: landing page, admin, and application.
- Secondary layouts may exist only under one of those families, with a clear owner.

## Domain Closure Status

Status: `phased-with-map`

The current route tree partially satisfies the target: authenticated application pages are mounted through `AppLayout`, and admin pages are mounted through `AdminPage` plus `AdminLayout`. The layout hierarchy is not closed because:

1. `RootLayout` exists but is not mounted by the router, while `AppLayout` recreates the shell and background itself.
2. `LandingLayout` exists but is bypassed by `LandingRedirect`, which imports only `LandingLayout.css` and recreates a `.landing-layout` wrapper.
3. `/login` and `/register` render page components directly, with no route-level layout owner.
4. Several files under `frontend/src/pages/**` are not route-mounted or classified as page-adjacent components, so the rule "all pages rely on layouts" is not exhaustively auditable.
5. No guard currently proves the mandatory layout hierarchy.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-react-pages/2026-05-08-0123/**`
- `_condamad/audits/frontend-react-pages/2026-05-08-1024/**`
- `_condamad/audits/frontend-react-pages/2026-05-08-1142/**`
- `_condamad/audits/frontend-react-pages/2026-05-08-1323/**`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-095-ajouter-guards-anti-drift-pages-frontend/**`
- `_condamad/stories/CS-100-fermer-sections-restantes-admin-prompts/**`
- `_condamad/stories/CS-101-decomposer-pages-volumineuses-allowlistees/**`
- `_condamad/stories/CS-102-centraliser-formatage-date-heure-pages/**`

## Regression Guardrails Consulted

- `RG-064` protects existing page architecture rules, but does not cover route-to-layout hierarchy.
- `RG-065` protects AdminPrompts ownership under feature owners.
- `RG-066` protects page-size exception closure.
- `RG-067` protects page date/time formatting ownership.

No new durable invariant was added to `_condamad/stories/regression-guardrails.md` because this audit is reporting an unimplemented target state, not an invariant already enforced by the current implementation.

## Prior Finding Closure Ledger

| Prior finding | Current classification | Current evidence | Notes |
|---|---|---|---|
| frontend-react-pages 13:23 F-001 | `still-active-as-related-guard-context` | E-006, E-007 | Existing page guards pass, but they do not enforce the newly audited layout hierarchy. |
| Prior frontend-react-pages implementation findings | `non-domain` | E-006, E-007, RG-064 to RG-067 | They remain closed for page architecture and are not reopened by this layout audit. |

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 4 |
| Medium | 1 |
| Low | 0 |
| Info | 0 |

## Closure Map

Implementation slice 1: converge route-level hierarchy.

- Mount `RootLayout` as the root route element.
- Move the current protected app branch under `RootLayout`.
- Route public landing through `LandingLayout`, not through a duplicated wrapper.
- Assign `/login` and `/register` to the selected principal family, most likely landing/auth under the master layout.

Implementation slice 2: normalize principal layout ownership.

- Make `AdminLayout` a true admin-family layout below the master layout.
- Keep application pages under `AppLayout`.
- Decide whether `EnterpriseLayout`, `ConsultationLayout`, `SettingsLayout`, and `PageLayout` are secondary layouts or page sections under the application family, then document the rule in tests.

Implementation slice 3: add layout architecture guards.

- Add a deterministic frontend test that walks `routes` and proves each leaf page has one accepted principal layout ancestor.
- Add a guard that blocks active `LandingLayout` bypasses such as importing only `LandingLayout.css` and recreating `.landing-layout` outside `LandingLayout`.
- Add a guard that blocks `RootLayout` remaining unmounted while layouts duplicate its shell/background responsibility.
- Add an inventory guard that classifies every `frontend/src/pages/**/*.tsx` file as a routed page, nested route page, page-adjacent component, or dead/unmounted page candidate.

Stop condition: the layout audit is closed when the route tree has one mounted master layout, exactly the approved principal layout families are route owners, direct page routes without a layout owner are absent or explicitly classified, every `frontend/src/pages/**/*.tsx` file has an owner classification, and `npm run test -- page-architecture layout` or an equivalent targeted guard fails on reintroduction.

## Exhaustive Remaining Implementation Surfaces

Application files:

- `frontend/src/app/routes.tsx`
- `frontend/src/app/guards/LandingRedirect.tsx`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/AdminLayout.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/layouts/AuthLayout.tsx`
- `frontend/src/components/layout/EnterpriseLayout.tsx`
- `frontend/src/features/consultations/components/ConsultationLayout.tsx`
- `frontend/src/layouts/SettingsLayout.tsx`
- `frontend/src/layouts/PageLayout.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/PrivacyPolicyPage.tsx`
- `frontend/src/pages/billing/BillingSuccessPage.tsx`
- `frontend/src/pages/billing/BillingCancelPage.tsx`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/pages/support/SupportTicketForm.tsx`
- `frontend/src/pages/support/SupportCategorySelect.tsx`
- `frontend/src/pages/admin/AdminPricingPanel.tsx`

Governance/test files:

- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/tests/page-architecture-allowlist.ts`
- Optional: a dedicated `frontend/src/tests/layout-architecture-guards.test.ts`.
- Optional: a page file ownership allowlist if page-adjacent components remain under `frontend/src/pages/**`.

Deferred non-domain context:

- CSS token, fallback, inline-style, and legacy-style debt remains governed by the frontend design-system audit chain.
- Page component decomposition remains governed by the frontend-react-pages audit chain.

## Validation

- `npm run lint` from `frontend/`: PASS.
- `npm run test -- page-architecture App` from `frontend/`: PASS, 5 files passed, 68 tests passed.
- Audit artifact validation and lint were run after report generation; see `01-evidence-log.md`.

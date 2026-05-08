<!-- Drafts detailles des stories proposees par l'audit frontend-layouts avant redaction finale. -->

# Detailed Story Drafts - frontend-layouts

## Drafting Principles

- Source audit: `_condamad/audits/frontend-layouts/2026-05-08-1405`.
- Domain unique for all drafts: `frontend-layouts`.
- Sequential stories allocated from `_condamad/stories/story-status.md`: `CS-103` to `CS-107`.
- Regression registry consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-064` to `RG-067`.
- Existing route evidence consulted:
  - `frontend/src/app/routes.tsx` mounts `/`, `/login`, `/register`, and the protected `AppLayout` branch without `RootLayout`.
  - `frontend/src/app/guards/LandingRedirect.tsx` imports `LandingLayout.css` and recreates `.landing-layout`.
  - `frontend/src/layouts/RootLayout.tsx` owns `.app-shell`, `.app-bg`, `StarfieldBackground`, `.app-bg-container`, and `Outlet`.
  - `frontend/src/layouts/AppLayout.tsx` currently duplicates `.app-shell`, `.app-bg`, `StarfieldBackground`, and `.app-bg-container`.
  - `frontend/src/tests/page-architecture-guards.test.ts` has page guards but no route-to-layout hierarchy guard.

## CS-103 Draft - Converger le layout maitre frontend

- Source candidate: `SC-001`; source finding: `F-001`.
- Story key: `converger-layout-maitre-frontend`.
- Archetype: `architecture-guard-hardening`.
- Closure status: `phased-with-map`, because the master layout can be mounted without resolving all page-file classification and public route ownership in the same story.
- Primary implementation decision:
  - `RootLayout` becomes the route-level master ancestor in `frontend/src/app/routes.tsx`.
  - `AppLayout` stops owning duplicated master shell/background responsibility, or the dependency on `RootLayout` is made explicit through route nesting.
- Detailed scope:
  - Capture a before route/layout inventory.
  - Mount the protected app branch under `RootLayout`.
  - Preserve redirects, auth guard behavior, application sidebar/header/bottom-nav, admin nested routing, and 404 behavior.
  - Add or extend a guard proving `RootLayout` is mounted and `AppLayout` no longer duplicates master-only shell/background ownership.
- Explicit non-scope:
  - Do not decide auth layout ownership.
  - Do not classify all page files.
  - Do not redesign CSS or layout visuals beyond ownership correction.
- Stop condition:
  - `RootLayout` is mounted, application routes still pass, and remaining layout audit gaps are exactly SC-002 to SC-005.

## CS-104 Draft - Monter la landing via son layout principal

- Source candidate: `SC-002`; source finding: `F-002`.
- Story key: `monter-landing-via-layout-principal`.
- Archetype: `legacy-facade-removal`.
- Closure status: `full-closure`.
- Primary implementation decision:
  - `LandingRedirect` remains responsible for token cleanup/authenticated redirect only.
  - `LandingLayout` owns the landing route wrapper, navbar, main, footer, and `.landing-layout`.
- Detailed scope:
  - Remove `ScopedLandingPage` or any equivalent local landing wrapper from `LandingRedirect`.
  - Route the landing page under `LandingLayout` in `frontend/src/app/routes.tsx`.
  - Preserve expired-token cleanup and authenticated redirect to `/dashboard`.
  - Add negative scans/guards that fail if `LandingRedirect` imports `LandingLayout.css` or creates `.landing-layout`.
- Explicit non-scope:
  - Do not change landing copy, pricing sections, navbar product behavior, or CSS tokens.
  - Do not add an alternate public landing wrapper.
- Stop condition:
  - `/` renders through `LandingLayout`, no local `.landing-layout` wrapper remains outside `LandingLayout`, and App/visual smoke tests prove the public route still renders.

## CS-105 Draft - Rattacher les routes auth publiques a un layout

- Source candidate: `SC-003`; source finding: `F-003`.
- Story key: `rattacher-routes-auth-publiques-layout`.
- Archetype: `ownership-routing-refactor`.
- Closure status: `blocked`.
- Required user/product decision:
  - Decide whether `/login` and `/register` belong under `LandingLayout`, under a dedicated `AuthLayout` secondary route, or under another explicit principal family.
- Implementation contract after decision:
  - Route `/login` and `/register` through the selected layout ancestor under `RootLayout`.
  - Preserve login/register navigation, redirects, and form behavior.
  - Add a hierarchy guard proving there are no direct auth page routes.
- Explicit non-scope:
  - Do not invent a visual redesign for auth pages.
  - Do not add a second active auth shell for compatibility.
  - Do not modify authentication API contracts.
- Stop condition:
  - If the product decision is unavailable, implementation stops and records the blocker.
  - If the product decision is available, both auth routes have an explicit layout owner and the guard blocks direct page reintroduction.

## CS-106 Draft - Ajouter les guards de hierarchie layout frontend

- Source candidate: `SC-004`; source finding: `F-004`.
- Story key: `ajouter-guards-hierarchie-layout-frontend`.
- Archetype: `architecture-guard-hardening`.
- Closure status: `full-closure`.
- Primary implementation decision:
  - Add deterministic Vitest/AST guards over the frontend route table and layout wrappers.
- Detailed scope:
  - Guard that `RootLayout` is mounted.
  - Guard that every route leaf rendering a page has one accepted principal layout ancestor or exact classification.
  - Guard that `LandingLayout` is not bypassed by importing only `LandingLayout.css` or recreating `.landing-layout` outside the layout owner.
  - Guard that exceptions are exact; no wildcard or folder-wide allowlist.
- Explicit non-scope:
  - Do not restructure application routes except as required by tests if a precondition story has not landed.
  - Do not resolve all page inventory debt; CS-107 owns that.
- Stop condition:
  - The guard fails for local bypass examples and passes against the final route tree.

## CS-107 Draft - Classer tous les fichiers pages sous un layout owner

- Source candidate: `SC-005`; source finding: `F-005`.
- Story key: `classer-pages-layout-owner`.
- Archetype: `ownership-routing-refactor`.
- Closure status: `phased-with-map`.
- Primary implementation decision:
  - Every `frontend/src/pages/**/*.tsx` file must be classified as `routed-page`, `nested-routed-page`, `page-adjacent-component`, `dead/unmounted-page-candidate`, or `needs-user-decision`.
- Detailed scope:
  - Build a persisted inventory from `rg --files frontend/src/pages -g "*.tsx"`.
  - Classify files based on `frontend/src/app/routes.tsx` and component imports.
  - Route true public pages such as billing return/privacy under a principal layout, or mark them `needs-user-decision` with explicit blocker.
  - Relocate support/admin panel components out of `pages/**` only if classification proves they are page-adjacent components and a canonical owner exists.
  - Add an exact inventory guard.
- Explicit non-scope:
  - Do not implement product decisions for public visibility without user decision.
  - Do not change admin permissions, billing API contracts, or privacy copy.
- Stop condition:
  - Every page file has exact classification and no unclassified page-file owner remains.

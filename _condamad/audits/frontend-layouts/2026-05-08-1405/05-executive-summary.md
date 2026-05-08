<!-- Synthese executive de l'audit CONDAMAD sur les layouts frontend. -->

# Executive Summary - frontend-layouts

The frontend does not yet satisfy the requested layout architecture.

Current state:

- Application pages are generally under `AppLayout`.
- Admin pages are under `AdminPage` and `AdminLayout`.
- `RootLayout` exists but is not used by the router.
- `LandingLayout` exists but the landing route bypasses it through `LandingRedirect`.
- `/login` and `/register` render direct page components without a route-level layout.
- Some `frontend/src/pages/**/*.tsx` files are not route-mounted or classified as page-adjacent components.
- Existing tests pass but do not guard the layout hierarchy.

Findings:

- High: 4
- Medium: 1
- Story candidates: 5
- Closure status: `phased-with-map`

Top risks:

- Layout shell/background behavior can diverge because no master layout owns it at runtime.
- Landing can appear visually correct while bypassing `LandingLayout` structure.
- Public auth pages are outside the “all pages use layouts” rule.
- Unclassified page files make the “all pages” rule non-exhaustive.
- Regression guards do not enforce the new architecture target.

Recommended next action:

Implement one coherent frontend-layout story that mounts `RootLayout`, routes landing/admin/application through explicit principal layouts, assigns auth and public utility pages to a layout family, classifies every `pages/**/*.tsx` file, and adds a deterministic layout architecture guard.

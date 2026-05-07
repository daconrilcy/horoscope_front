# Hardcoded Values After

## Scope

- File migrated: `frontend/src/pages/settings/Settings.css`
- Guard updated: `frontend/src/tests/design-system-guards.test.ts`
- Registries changed: none. `--settings-*` and `--usage-progress` were already registered.

## Final Decisions

| Surface | Final decision | Evidence |
|---|---|---|
| Settings accent palette | `registered-semantic-owner` | `--settings-purple*` variables live in `.settings-container`; repeated consumers use `var(--settings-*)`. |
| Settings gold palette | `registered-semantic-owner` | `--settings-gold*` variables own warm plan/badge/progress roles. |
| Settings glass/card surfaces | `registered-semantic-owner` | `--settings-card-*` variables own surfaces, borders and elevations. |
| Settings text colors | `registered-semantic-owner` | `--settings-text-*` variables own page-specific ink roles. |
| Settings page, card and feedback gradients | `registered-semantic-owner` | `--settings-*-bg` variables own the remaining gradient values. |
| Radius values | `registered-semantic-owner` | `--settings-radius-*` variables own Settings-specific card/control/avatar radii; global `--radius-*` remains used where already canonical. |
| Typography values | `registered-semantic-owner` | `--settings-type-*` variables route page-specific sizes/line-heights to global `--type-*`, `--font-*` and `--line-height-*` where equivalent. |
| Runtime usage progress | `runtime-custom-property` | `width: calc(var(--usage-progress, 0) * 1%)` remains the exact dynamic allowlisted fallback. |
| One-off literals remaining in owner block | `kept-one-off-final` | Remaining hex/rgba/gradient/clamp literals are centralized in `.settings-container` as page-scoped semantic declarations, not repeated in selectors. |
| Settings spacing and layout values | `registered-semantic-owner` | Repeated spacings and layout dimensions are centralized under `--settings-page-*`, `--settings-card-*`, `--settings-section-*`, `--settings-overview-*`, `--settings-tab-*`, `--settings-plan-*`, `--settings-usage-*`, `--settings-progress-*`, and related owner variables on `.is-settings-page`. |

## Owner Block Decisions

Every literal that remains after migration is centralized in `.is-settings-page`,
the page-scoped owner for `--settings-*`. Selector-level consumers use variables
or global tokens. The final owner decisions are:

| Owner variables | Decision | Notes |
|---|---|---|
| `--settings-purple*`, `--settings-gold*` | `registered-semantic-owner` | Page accent and warm status palette; repeated selector usage goes through variables. |
| `--settings-card-surface*`, `--settings-card-border*`, `--settings-card-shadow*` | `registered-semantic-owner` | Glass surfaces, borders and elevation roles centralized. |
| `--settings-text*`, `--settings-success-border` | `registered-semantic-owner` | Settings-specific text/status roles centralized. |
| `--settings-*-bg`, `--settings-*-fill-bg` | `registered-semantic-owner` | Gradients centralized in the owner block; rendered selectors consume variables. |
| `--settings-radius-*` | `registered-semantic-owner` | Card/control/avatar radii centralized; global `--radius-*` remains where canonical. |
| `--settings-type-*` | `registered-semantic-owner` | Page-specific typography roles route to global `--type-*`, `--font-*`, and `--line-height-*` where possible. |
| `--settings-page-*`, `--settings-card-*`, `--settings-section-*` spacing variables | `registered-semantic-owner` | Page width/padding, card padding/stacking, section offsets and title rule dimensions. |
| `--settings-overview-*`, `--settings-aside-*`, `--settings-stat-*` | `registered-semantic-owner` | Overview, aside and stat layout spacings. |
| `--settings-tabs-*`, `--settings-tab-*`, `--settings-grid-*`, `--settings-option-*` | `registered-semantic-owner` | Settings navigation and astrologer selection layout. |
| `--settings-badge-*`, `--settings-profile-badge-*`, `--settings-plans-*`, `--settings-plan-*` | `registered-semantic-owner` | Badges and subscription plan spacing, glows, offsets and dimensions. |
| `--settings-actions-*`, `--settings-feedback-*`, `--settings-credits-*` | `registered-semantic-owner` | Action panel, feedback banner and credit section layout. |
| `--settings-usage-*`, `--settings-progress-*`, `--settings-waterline-*`, `--settings-save-feedback-*`, `--settings-sr-only-*` | `registered-semantic-owner` | Usage metrics, progress meters, feedback and screen-reader utility dimensions. |
| Zero reset declarations such as `margin: 0`, `padding: 0`, `inset: 0`, `left: 0`, `bottom: 0`, and `gap: 0` | `kept-one-off-final` | CSS resets/position anchors are not visual scale tokens and are intentionally kept in selectors. |
| `margin: 0 auto`, `margin-top: auto`, `border-radius: inherit`, `width: 100%`, `height: 100%`, `min-width: 0`, `max-width` via variable | `kept-one-off-final` | Functional layout declarations, not repeated visual scale literals. |
| `width: calc(var(--usage-progress, 0) * 1%)` | `runtime-custom-property` | Exact dynamic bridge already allowlisted. |

## Anti-return Guard

- Added test: `bloque le retour des literals Settings migres par CS-084`.
- Mechanism: the test extracts `.settings-container`, removes that owner block, and fails if migrated colors, gradients, shadows, radii or typography literals reappear in rendered selectors.
- Mechanism update after review: the test now extracts `.is-settings-page`, removes that owner block, and fails if migrated colors, gradients, shadows, radii, typography or spacing literals reappear in rendered selectors.
- The guard also asserts `--settings-*` remains registered, `--settings-page-bg` is declared on the common ancestor owner, `.settings-bg-halo` consumes that variable, and `--usage-progress` remains the only expected CSS fallback in guarded Settings selectors.
- Added Settings render smoke coverage in `frontend/src/tests/visual-smoke.test.tsx` for `SettingsLayout`, including the halo inside `.is-settings-page`.

## Final Scans

| Command | Result | Classification |
|---|---|---|
| `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/settings/Settings.css` | Hits only in `.settings-container` semantic owner block. | `registered-semantic-owner` / `kept-one-off-final` |
| `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/settings/Settings.css` | Selector hits use global tokens or `--settings-type-*`; owner block declares final page roles. | `registered-semantic-owner` |
| `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/settings/Settings.css` | Shape/elevation selectors use tokens or `--settings-*`; only `--usage-progress` has a fallback. | `registered-semantic-owner` / `runtime-custom-property` |
| `rg -n "margin|padding|gap|inset|top:|right:|bottom:|left:|outline-offset" src/pages/settings/Settings.css` | Repeatable spacing and offsets are centralized in `.is-settings-page`; remaining selector hits are variable usage or functional zero/auto anchors. | `registered-semantic-owner` / `kept-one-off-final` |
| `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/settings/Settings.css` | Zero hits. | `PASS` |
| `rg -n --glob "*.css" -- "--settings-" src` | CSS hits are scoped to `src/pages/settings/Settings.css`. | `PASS` |

## Allowed Differences

- Visual output may differ only by token indirection and removal of unowned selector-level literals.
- React behavior, routes, stores and API calls are unchanged.
- Existing Vite chunk-size warning remains unrelated and explicitly out of scope.

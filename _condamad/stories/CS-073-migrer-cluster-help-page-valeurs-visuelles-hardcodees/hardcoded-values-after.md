<!-- Decisions finales du cluster HelpPage apres migration CS-073. -->

# Hardcoded Values After

## Scope final

- File: `frontend/src/pages/HelpPage.css`
- Migrated cluster: main help page styles from `.help-page` through `.help-placeholder-card__text`.
- Out of scope and intentionally unchanged: subscription-specific styles after the `Help Subscriptions Page` marker.

## Final decisions

| Category | Final owner | Decision |
|---|---|---|
| Help background, glass surfaces, borders and shadows | `--help-*` declarations scoped to `.help-page` | `registered-semantic-owner` |
| Help ink and accent colors | `--help-*` declarations scoped to `.help-page` | `registered-semantic-owner` |
| Help radii | `--help-radius-*`, plus existing `--radius-*` tokens for global shapes | `registered-semantic-owner` / `migrated` |
| Help typography | existing `--type-*`, `--font-*` and `--line-height-*` tokens where canonical | `migrated` |
| White button text | existing `--color-star-fill` | `migrated` |
| Focus outline in migrated cluster | existing `--color-primary` | `migrated` |
| Remaining geometric one-offs in migrated cluster | `50%`, media-query clamp values, ticket subject display size | `kept-one-off-final` because they are local layout or editorial scale decisions |
| Subscription block literals | unchanged | out of cluster for CS-073 |

## Registry update

- `frontend/src/styles/token-namespace-registry.md` now classifies `--help-*` as a `semantic-extension` owned by `frontend/src/pages/HelpPage.css`.
- No global token was added.
- No `legacy`, `alias`, `compat`, `shim`, `fallback` or `migration-only` namespace was introduced.

## Anti-return scans

Commands run from `frontend` after implementation:

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/HelpPage.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/HelpPage.css
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/HelpPage.css
rg -n "legacy|Legacy|alias|compat|shim|fallback|migration-only" src/pages/HelpPage.css
```

Results:

- Color/rgba hits in the migrated cluster are centralized under `.help-page` `--help-*` declarations or tokenized usages.
- Typography hits in the migrated cluster use existing typography/font/line-height tokens except final local editorial/display one-offs.
- Box-shadow and border-radius hits in the migrated cluster use `--help-*`, `--radius-*`, or final geometry one-offs.
- Forbidden namespace scan returned zero hits.
- CSS fallback scan returned zero hits for `HelpPage.css`.

Exact migrated literal checks:

| Literal family | After classification |
|---|---|
| `#2f2345`, `#6d56bf`, support status inks | present only as `.help-page` semantic owners |
| `rgba(47, 35, 69, ...)` text inks | present only as `.help-page` semantic owners |
| `rgba(138, 114, 217, ...)` accent roles | present only as `.help-page` semantic owners in the migrated cluster; subscription block remains out of scope |
| `rgba(255, 255, 255, ...)` glass roles | present only as `.help-page` semantic owners in the migrated cluster; subscription block remains out of scope |
| `0 18px 34px rgba(87, 63, 144, 0.1)` | present only as `--help-shadow-card` |
| `border-radius: 999px` | zero active hits in `HelpPage.css`; ticket rail now uses `var(--radius-full)` |

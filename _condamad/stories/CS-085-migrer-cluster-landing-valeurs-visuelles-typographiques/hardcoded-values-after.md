# Hardcoded Values After - CS-085

## Scope

- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/**/*.css`
- `frontend/src/app/guards/LandingRedirect.tsx` only to attach the landing owner scope to `/`.
- Design-system documentation/tests touched only for CS-085 governance.

## Final decisions

| Category | Decision | Evidence |
|---|---|---|
| Repeated landing colors, gradients, translucent surfaces and shadows | `registered-semantic-owner` | Centralized under `.landing-layout` as `--landing-*` in `frontend/src/layouts/LandingLayout.css`; consumed via `var(--landing-*)` by landing CSS. |
| Landing typography scale | `registered-semantic-owner` | Centralized as `--landing-type-*`; `frontend/src/styles/typography-roles.md` documents `landing-marketing`. |
| Premium tokens already canonical | `migrated` | Existing `--premium-*`, `--font-*`, `--radius-*`, `--line-height-*`, `--color-star-fill` and similar global tokens reused where applicable. |
| Rare landing semantic tones | `registered-semantic-owner` | Kept under named `--landing-*` variables such as success/warning/rating/live status and hero device tones. |
| Runtime route owner scope | `migrated` | `LandingRedirect` wraps the lazy landing page in `.landing-layout`, and `App.test.tsx` asserts `.landing-layout .landing-page` at `/`. |
| Page-scoped non-landing namespaces | `migrated` | No `--settings-*`, `--help-*`, `--chat-*` or `--app-*` consumers in landing CSS; guard and scan cover this. |
| CSS fallbacks | `migrated` | No `var(--token, literal)` fallback remains in the landing cluster. |

## After scans

| Category | Command | Result | Classification |
|---|---|---|---|
| Visual values | `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` from `frontend/` | Hits only in `src/layouts/LandingLayout.css` owner declarations. | `registered-semantic-owner` |
| Typography declarations | `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` from `frontend/` | Owner declarations plus `var(--landing-type-*)`, global typography vars and inherited premium/global roles in consumers. | `registered-semantic-owner` / `migrated` |
| Elevation/radius/fallback candidates | `rg -n "box-shadow:\|border-radius:\|var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` from `frontend/` | `box-shadow`/`border-radius` consumers are tokenized; no CSS fallback match. | `migrated` |
| No Legacy vocabulary | `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` from `frontend/` | Zero active hits. | `migrated` |
| Page-scoped namespaces | `rg -n --glob "*.css" -- "--settings-\|--help-\|--chat-\|--app-" src/layouts/LandingLayout.css src/pages/landing` from `frontend/` | Zero hits. | `migrated` |

## Anti-return guard

- `frontend/src/tests/design-system-guards.test.ts` adds `bloque le retour des literals landing migres par CS-085`.
- The guard removes the `.landing-layout` owner block before scanning consumers, blocks raw colors/gradients/typography/fallbacks outside that owner, blocks page-scoped namespace consumption, and requires more than 100 migrated owner values to prevent silent guard shrinkage.
- `frontend/src/tests/visual-smoke.test.tsx` adds a CS-085 smoke assertion for the landing owner and token-backed hero typography.
- `frontend/src/tests/App.test.tsx` asserts that route `/` renders `.landing-layout .landing-page`.

## Final conclusion

Every selected landing literal has a final decision. Repeated values are owned by documented `--landing-*`, existing global/premium tokens, or the `landing-marketing` typography role. No broad allowlist, fallback, compatibility namespace, migration-only namespace or active legacy vocabulary was introduced.

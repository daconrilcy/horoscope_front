# Validation Plan

## Environment assumptions

- Frontend package manager: `npm` (`package-lock.json` present).
- Commands run from `frontend/`.
- No Python command is required for this frontend-only story.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Starfield and background guards | `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system` | `frontend/` | yes | all targeted tests pass |
| Layout route-level scope | `npm run test -- layout` | `frontend/` | yes | layout tests pass |

## Static guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Inline styles in touched React | `rg -n "style=" src/layouts/RootLayout.tsx src/components/StarfieldBackground.tsx` | `frontend/` | yes | zero hits |
| Raster background image in owners | `rg -n "background-image:\s*url\(" src/styles/premium-theme.css src/styles/backgrounds.css src/layouts/LandingLayout.css` | `frontend/` | yes | zero new owner hits |
| Motion/starfield evidence | `rg -n "prefers-reduced-motion|shooting|meteor|starfield" src/components src/styles src/layouts -g "*.tsx" -g "*.css"` | `frontend/` | yes | expected owner hits only |
| Canonical background owners | `rg -n "premium-app-bg|premium-app-bg-atmosphere|app-bg|starfield-bg" src/styles src/layouts src/components -g "*.css" -g "*.tsx"` | `frontend/` | yes | canonical owner hits |
| App.css protected | `rg -n "dark|html\.dark|starfield|premium-app-bg" src/App.css` | `frontend/` | yes | zero active App.css hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint/type checks | `npm run lint` | `frontend/` | yes | exit 0 |
| Build | `npm run build` | `frontend/` | yes | exit 0 |

## Runtime

- Start local app only if validations complete and no existing process blocks it: `npm run dev`.

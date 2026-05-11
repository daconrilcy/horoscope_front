# No Legacy / DRY Guardrails

## Canonical owners

- Global background tokens: `frontend/src/styles/premium-theme.css`
- Global background layers: `frontend/src/styles/backgrounds.css`
- React/SVG starfield: `frontend/src/components/StarfieldBackground.tsx`
- Route-level scope: `frontend/src/layouts/RootLayout.tsx`

## Forbidden

- No new background implementation in page CSS, `App.css`, inline styles or raster assets.
- No compatibility wrapper, duplicate theme provider, alternate route wrapper, alias or fallback background path.
- No new dependency for animation.
- No `style=` in touched React files.

## Required evidence

- Targeted tests for starfield, visual smoke, theme tokens, design-system and layout.
- Negative scans for inline styles, `background-image: url(` in owners, App.css dark/background fixes and page-level competing backgrounds.
- Before/after story artifacts classify existing hits.

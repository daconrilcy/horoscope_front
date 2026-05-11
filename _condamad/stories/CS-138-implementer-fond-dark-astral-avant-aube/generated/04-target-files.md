# Target Files

## Must read

- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/layouts/LandingLayout.tsx`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/components/StarfieldBackground.tsx`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/tests/StarfieldBackground.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`

## Must search

- `rg -n "style=|background-image:\s*url\(|premium-app-bg|starfield|landing-layout" frontend/src`
- `rg -n "prefers-reduced-motion|shooting|meteor|starfield" frontend/src frontend/src/tests -g "*.tsx" -g "*.css" -g "*.ts"`

## Likely modified

- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/components/StarfieldBackground.tsx`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/tests/StarfieldBackground.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppBgStyles.test.ts`
- Story evidence files.

## Forbidden unless justified

- `frontend/src/App.css`
- Backend files
- API/client files
- Page-local background rewrites
- New dependencies or raster background assets

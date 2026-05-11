# Validation plan CS-140

- `rg "Allowed Owner Map" _condamad\stories\CS-139-refactoriser-ownership-css-landing\landing-css-ownership-after.md`
- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`
- `npm run lint`
- `rg -n "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css`

Validation visuelle:
- Playwright local sur desktop/mobile light/dark top, mid-page et menu mobile.

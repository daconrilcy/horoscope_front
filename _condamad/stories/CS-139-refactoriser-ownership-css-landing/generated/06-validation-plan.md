# Validation plan CS-139

Commandes requises depuis `frontend/`:

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`
- `npm run lint`
- `rg -n "app-bg--landing|style=|--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts`
- `rg -n "^\s*--landing-" src/layouts/LandingLayout.css src/pages/landing -g "*.css"`

Validation runtime:
- Playwright local sur `http://127.0.0.1:5173/`.
- Captures desktop/mobile light/dark et métrique `scrollWidth === clientWidth`.

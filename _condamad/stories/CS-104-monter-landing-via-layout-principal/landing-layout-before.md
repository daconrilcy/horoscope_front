# CS-104 - Inventaire landing avant

- Route `/`: `frontend/src/app/routes.tsx` rendait directement `LandingRedirect`.
- `LandingRedirect` importait `../../layouts/LandingLayout.css`.
- `LandingRedirect` declarait `ScopedLandingPage`.
- `ScopedLandingPage` rendait un wrapper local `className="landing-layout"` autour de `LandingPage`.
- `LandingLayout` existait deja et contenait l'owner canonique `LandingNavbar`, `main`, `Outlet`, `LandingFooter` et `.landing-layout`.

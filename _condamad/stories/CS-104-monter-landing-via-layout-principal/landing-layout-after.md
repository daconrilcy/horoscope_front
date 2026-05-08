# CS-104 - Inventaire landing apres

- Route `/`: enfant index de `LandingLayout` sous `RootLayout`.
- `LandingLayout` reste l'unique owner de `className="landing-layout"`.
- `LandingRedirect` ne contient plus `LandingLayout.css`, `ScopedLandingPage` ni wrapper `.landing-layout`.
- `LandingRedirect` conserve seulement la purge de token expire, la redirection token actif vers `/dashboard`, et le chargement de `LandingPage`.
- Guard: `frontend/src/tests/page-architecture-guards.test.ts` echoue si le bypass revient par import CSS, wrapper local ou `ScopedLandingPage`.

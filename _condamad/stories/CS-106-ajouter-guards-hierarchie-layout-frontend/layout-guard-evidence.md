# CS-106 - Evidence des guards layout

- Guard `RootLayout`: importe `routes` et verifie que la route racine utilise `RootLayout`.
- Guard `AppLayout`: verifie que la branche protegee contient `AppLayout` et que `AppLayout.tsx` ne contient plus `StarfieldBackground`, `app-shell app-bg` ni `app-bg-container`.
- Guard landing: verifie que l'index landing est sous `LandingLayout`, que `LandingRedirect` ne contient plus `LandingLayout.css` ni `ScopedLandingPage`, et que seul `LandingLayout.tsx` rend `.landing-layout`.
- Guard auth: verifie que `/login` et `/register` sont enfants de `AuthLayout` et ne sont pas des routes directes au niveau maitre.
- Guard inventaire pages: compare `rg --files src/pages -g "*.tsx"` a `PAGE_LAYOUT_OWNER_CLASSIFICATIONS`.
- Allowlist: aucune entree wildcard ou folder-wide; les classifications sont exactes par fichier.
- Commandes PASS: `npm run test -- page-architecture layout`, `npm run test -- page-architecture App router BillingSuccessPage`, `npm run lint`, `npm run test`.

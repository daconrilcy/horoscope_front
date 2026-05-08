# CS-103 - Inventaire layout maitre avant

- Route tree initiale: `/`, `/login`, `/register` et la branche protegee etaient des routes racine separees dans `frontend/src/app/routes.tsx`.
- `RootLayout` existait dans `frontend/src/layouts/RootLayout.tsx`, mais n'etait pas monte dans la route tree.
- `AppLayout` rendait `StarfieldBackground`, `.app-shell app-bg` et `.app-bg-container`, dupliquant la responsabilite maitre.
- Garde initiale: `frontend/src/tests/page-architecture-guards.test.ts` couvrait les pages React, pas la hierarchie route-to-layout.
- Gaps explicitement phases: landing `CS-104`, auth `CS-105`, guards `CS-106`, inventaire pages `CS-107`.

# CS-106 - Etat des guards layout avant

- `page-architecture-guards.test.ts` couvrait `@ts-nocheck`, `apiFetch`, aliases publics retires, exports admin retires et exceptions de taille.
- Aucun test ne prouvait que `RootLayout` etait monte.
- Aucun test ne prouvait l'absence de bypass `LandingLayout`.
- Aucun test ne bloquait les routes auth directes.
- Aucun inventaire executable ne couvrait tous les fichiers `frontend/src/pages/**/*.tsx`.

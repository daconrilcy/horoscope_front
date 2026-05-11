# Execution brief CS-139

Objectif: fermer `F-001` en remplaçant l'owner CSS landing fourre-tout par une carte finie de groupes `--landing-*`, owners canoniques et consommateurs audités.

Périmètre autorisé:
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/**`
- tests frontend de guards design-system, smoke visuel et architecture.

Non-objectifs:
- pas de changement de route, `RootLayout`, `LandingLayout.tsx`, `App.css` ou backend;
- pas de `app-bg--landing`;
- pas de styles inline.

Guardrails applicables: `RG-083`, `RG-084`, `RG-086`, `RG-087`.

Statut implementation: complète, en attente de revue finale propre.

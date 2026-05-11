# CS-146 - No Legacy / DRY guardrails

## Interdits

- Pas de `app-bg--landing`.
- Pas de `style=` sous `frontend/src/pages/landing` ou `frontend/src/layouts`.
- Pas de correction via `App.css`.
- Pas de dependance modal/drawer.
- Pas de deuxieme navbar ou composant modal generique non reutilise.

## Guardrails applicables

- `RG-083` dark mode routes frontend auditees.
- `RG-084` fond global canonique.
- `RG-085` fond dark astral global.
- `RG-086` absence de variante `app-bg--landing`.
- `RG-087` fond viewport-fixed.
- `RG-088` complexite visuelle motion/filter landing bornee.

## Evidence attendue

- Tests `LandingPage`, `visual-smoke`, `design-system`, `AppBgStyles`, `page-architecture`.
- Scans interdits.
- Artefact after avec mesures runtime.


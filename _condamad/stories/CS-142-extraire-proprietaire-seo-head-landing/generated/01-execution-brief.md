# Execution brief CS-142

Objectif: fermer `F-004` en extrayant les mutations `document.*` de `LandingPage.tsx` vers un owner local `LandingHead.tsx`.

Périmètre:
- `LandingPage.tsx`
- `LandingHead.tsx`
- `LandingPage.test.tsx`
- allowlist page architecture pour le nouvel owner local.

Non-objectifs:
- pas de dependance head-management;
- pas de changement route, contenu, CSS ou backend.

<!-- Inventaire final des surfaces CSS legacy apres classification CS-031. -->

# Legacy Style Surfaces After

Ajouts:

- Registre `frontend/src/styles/legacy-style-surface-registry.md`.
- Audit `_condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/legacy-style-removal-audit.md`.
- Test `frontend/src/tests/legacy-style-policy.test.ts`.

Guard: `npm run test -- legacy-style`.

Resultat: chaque famille de selecteur legacy detectee est rattachee au registre.

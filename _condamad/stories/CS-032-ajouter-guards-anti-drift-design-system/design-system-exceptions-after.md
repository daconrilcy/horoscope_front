<!-- Snapshot final des exceptions design-system apres suite CS-032. -->

# Design System Exceptions After

Suite executable: `npm run test -- design-system`.

Exceptions sourcees:

- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/inline-style-allowlist.ts`

Resultat: les exceptions sont reliees a des fichiers, symboles ou families
exactes et verifiees par Vitest.

<!-- Brief d'execution genere pour CS-082. -->

# Execution Brief

Story: CS-082 migrer-cluster-app-valeurs-visuelles-hardcodees.

Objectif: migrer un lot borne de valeurs visuelles dans `frontend/src/App.css`
vers un namespace semantique documente, sans modifier React ni les routes.

In scope:

- `frontend/src/App.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- artefacts CONDAMAD CS-082

Non-goals:

- pas de changement `App.tsx`;
- pas de modification backend;
- pas de dependance nouvelle;
- pas de migration des autres clusters CSS.

Done conditions:

- namespace `--app-*` documente;
- garde anti-retour executable;
- tests design-system et build frontend verts;
- preuves finales completees.


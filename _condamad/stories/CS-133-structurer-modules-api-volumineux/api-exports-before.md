<!-- Inventaire before des exports publics API volumineux CS-133. -->

# CS-133 - Exports before

## Fichiers volumineux initiaux

- `frontend/src/api/adminPrompts.ts`: 1107+ lignes, types, requetes, hooks et
  helpers dans un seul module.
- `frontend/src/api/natalChart.ts`: 556+ lignes, types, requetes, hooks et
  effets navigateur dans un seul module.

## Consommateurs publics a preserver

- `@api` via `frontend/src/api/index.ts`.
- Imports directs existants depuis `../api/adminPrompts`,
  `../api/natalChart` et `@api`.

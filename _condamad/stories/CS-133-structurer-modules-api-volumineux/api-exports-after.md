<!-- Inventaire after des exports publics API volumineux CS-133. -->

# CS-133 - Exports after

## Structure finale

- `frontend/src/api/adminPrompts.ts` reste l'entrypoint public stable et exporte
  `./admin-prompts`.
- `frontend/src/api/admin-prompts/index.ts` porte l'implementation du domaine.
- `frontend/src/api/natalChart.ts` reste l'entrypoint public stable et exporte
  `./natal-chart`.
- `frontend/src/api/natal-chart/index.ts` porte l'implementation du domaine.

## Validation

Les tests `AdminPromptsPage`, `adminPromptsApi`, `natalChartApi`,
`NatalChartPage` et `natalInterpretation` passent apres deplacement, ce qui
prouve la preservation des imports publics observes.

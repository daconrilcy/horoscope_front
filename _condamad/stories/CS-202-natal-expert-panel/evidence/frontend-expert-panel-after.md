# CS-202 Frontend Expert Panel After

## UI implemented

- Nouveau composant:
  `frontend/src/features/natal-chart/NatalExpertPanel.tsx`.
- Styles dedies:
  `frontend/src/features/natal-chart/NatalExpertPanel.css`.
- Integration page:
  `frontend/src/pages/NatalChartPage.tsx` rend le panneau depuis
  `latestChart.data`.
- Types publics:
  `frontend/src/api/natal-chart/index.ts` etend `LatestNatalChart.result` avec
  les blocs publics CS-201.

## Blocs affiches

- `dignities.sect`: champs chart-level `chart_sect`,
  `sun_horizon_position`, `sun_above_horizon`, `calculation_basis` et
  `reference_system`.
- `dignities.planets[*].sect_condition`: groupes `Dans la secte`,
  `Hors secte`, `Neutre / variable / inconnu`.
- `advanced_conditions`: faits techniques `condition_code`,
  `condition_type`, `score_effect`, `axis_weights` et `evidence`.
- `dignities.planets`: scores essentiels, accidentels, totaux, axes et
  breakdowns disponibles.
- `planet_condition_profiles`: axes techniques, `ranking_score` et
  `condition_level`.
- `planet_condition_signals`: champs techniques; `prompt_hint` est type comme
  champ public mais n'est pas rendu.
- `dominant_planets`: top/chart ruler/most elevated, rangs, scores et facteurs.
- `interpretation_adapter`: signaux, themes actives, topics, axes et patterns
  factuels, sans prose narrative ni appel LLM.

## Etats couverts

- Loading.
- Error.
- Aucun chart charge.
- Ancien payload sans blocs experts.
- Blocs experts vides.
- Mode degrade sans heure fiable.

## Ownership and no-calculation proof

- Le panneau ne fait aucun fetch direct et recoit le chart via la page.
- Le grouping de secte utilise uniquement `is_in_sect`, `is_out_of_sect` et les
  codes du payload.
- Aucun backend, migration, seed ou projection JSON backend n'a ete modifie.
- Aucun style inline n'a ete ajoute dans les nouveaux fichiers.

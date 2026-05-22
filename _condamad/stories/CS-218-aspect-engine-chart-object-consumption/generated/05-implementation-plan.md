# Implementation Plan

## Initial Repository Findings

- `calculate_major_aspects` consomme deja `AspectBodyRuntimeData`; le coeur
  geometrique peut rester intact.
- `build_natal_result` consommait encore `positions_raw` et `points_raw` pour
  construire les corps d'aspects.
- `ChartObjectRuntimeData.capabilities.supports_aspects` existe depuis CS-217.
- `build_chart_object_runtime_data` est le owner canonique de construction des
  objets du theme.

## Proposed Changes

1. Ajouter `backend/app/domain/astrology/calculators/aspect_inputs.py` avec:
   - `AspectChartObjectSelector`;
   - `AspectBodyProjector`.
2. Construire `positions`, `points`, `houses` et `chart_objects` avant le calcul
   des aspects dans `build_natal_result`.
3. Calculer les aspects depuis `AspectBodyProjector(...).project_many(...)`.
4. Conserver le flag historique `include_points_in_aspects` en pilotant la
   capacite des points astraux dans le builder chart-object.
5. Garder les angles hors pool natal par defaut pour ne pas modifier les
   sorties existantes; le selector/projector restent capables d'inclure un
   angle dont la capacite est vraie.
6. Ajouter tests comportementaux et guards AST.

## Files to Delete

- Aucun.

## Risks and Controls

- Risque de changement public des aspects: controle par suite backend complete
  et tests golden existants.
- Risque de fausse migration: controle par spy sur `calculate_major_aspects`
  comparant participants et `chart_objects` aspectables.
- Risque de retour par collections historiques: guard AST et scans `RG-145`.

## Rollback Strategy

Revenir au flux `positions_raw`/`points_raw` dans `natal_calculation.py` et
supprimer `aspect_inputs.py`; les tests CS-218 echoueraient et signaleraient la
reintroduction de l'ancien flux.

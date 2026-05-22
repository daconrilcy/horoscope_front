# Implementation Plan

## Approach

1. Ajouter les payloads runtime dignity/dominance et validateurs de phase.
2. Declarer `supports_dignities` uniquement sur les corps ephemerides deja projetes.
3. Ajouter des modules purs `dignities/chart_object_inputs.py` et `dominance/chart_object_inputs.py`.
4. Adapter `build_natal_result` pour calculer, enrichir puis valider les phases dignity et dominance.
5. Renommer l'entree du moteur de dominance en `chart_object_positions` pour supprimer la consommation nominale `planet_positions`.
6. Ajouter tests unitaires, integration natal et guards d'architecture.

## No Legacy stance

Aucun shim, alias, fallback ou wrapper compat n'est introduit. Les calculateurs historiques restent owners des scores; les nouveaux modules ne font que selectionner, projeter et enrichir.

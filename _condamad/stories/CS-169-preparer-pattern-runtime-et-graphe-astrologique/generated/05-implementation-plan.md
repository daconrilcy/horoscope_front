# Implementation Plan

## Initial repository findings

- Les patterns astrologiques et graphes n'avaient pas de contrats runtime prêts pour de futures projections.
- Aucun endpoint public ni projection prediction ne devait être créé par cette story.

## Proposed changes

- Ajouter les contrats runtime de patterns.
- Ajouter les contrats de noeuds/arêtes de graphe astrologique.
- Exporter les types sans activer de calcul automatique.

## Files to modify

- `backend/app/domain/astrology/runtime/pattern_runtime_data.py`
- `backend/app/domain/astrology/runtime/astrological_graph_contracts.py`
- `backend/app/domain/astrology/runtime/__init__.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires des contrats de pattern, graph readiness et exports publics.

## Risk assessment

- Risque principal: exposition prématurée dans prediction ou API. Les tests et scans vérifient l'absence de projection.

## Rollback strategy

- Revenir les contrats runtime/graph et tests associés; aucune donnée persistée.

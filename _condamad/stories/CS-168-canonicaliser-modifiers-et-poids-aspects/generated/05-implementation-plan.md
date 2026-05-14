# Implementation Plan

## Initial repository findings

- Les modificateurs de force d'aspect n'avaient pas de taxonomie runtime explicite.
- Le champ générique `weight` devait être évité pour ne pas usurper les pondérations prediction.

## Proposed changes

- Ajouter une taxonomie de modificateurs et de poids interprétatif.
- Ajouter un évaluateur de force canonique avec raisons structurées.
- Brancher les modificateurs dans le builder runtime.

## Files to modify

- `backend/app/domain/astrology/runtime/aspect_modifiers.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/astrology/interpretation/aspect_strength_contracts.py`
- `backend/app/domain/astrology/interpretation/aspect_strength.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires des modificateurs, de la force canonique et des exports publics.

## Risk assessment

- Risque principal: ambiguïté avec les scores prediction. Les champs nomment explicitement `interpretive_weight` et l'ownership.

## Rollback strategy

- Revenir la taxonomie, l'évaluateur, le branchement runtime et les tests; aucun rollback DB.

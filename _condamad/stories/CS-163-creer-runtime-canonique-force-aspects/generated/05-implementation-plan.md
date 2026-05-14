# Implementation Plan

## Initial repository findings

- `AspectResult` exposait un modèle plat sans runtime canonique.
- La projection publique sérialisait uniquement les champs historiques.

## Proposed changes

- Ajouter des dataclasses runtime canoniques pour identité, participants, orbe, phase, interprétation et métadonnées.
- Construire automatiquement `AspectRuntimeData` depuis `AspectResult` sans élargir `model_dump()`.
- Réutiliser ce runtime dans la projection JSON enrichie.

## Files to modify

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires du builder runtime, des exports publics et de la projection JSON.

## Risk assessment

- Risque principal: élargissement involontaire des payloads internes. Couvert par l'exclusion `aspect_runtime` de `model_dump()`.

## Rollback strategy

- Revenir les fichiers runtime/builder/projection et les tests associés; aucune migration ni donnée persistée à restaurer.

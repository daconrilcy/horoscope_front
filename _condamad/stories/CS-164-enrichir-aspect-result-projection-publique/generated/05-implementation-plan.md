# Implementation Plan

## Initial repository findings

- La projection publique des aspects ne portait pas les informations canoniques calculées par le runtime.
- `AspectResult.model_dump()` risquait de diffuser les champs internes si le runtime était ajouté naïvement.

## Proposed changes

- Enrichir la sérialisation publique avec les champs runtime stables.
- Reconstruire le runtime à la volée pour les objets historiques dépourvus de `aspect_runtime`.
- Exclure explicitement `aspect_runtime` des dumps Pydantic.

## Files to modify

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_aspects_calculator.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests de projection JSON, de service chart et de non-exposition de `aspect_runtime` dans `model_dump()`.

## Risk assessment

- Risque principal: rupture de compatibilité payload. Le format historique reste présent et les nouveaux champs sont additifs.

## Rollback strategy

- Revenir les enrichissements de projection et les assertions associées; aucun rollback DB requis.

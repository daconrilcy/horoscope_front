# Implementation Plan

## Initial repository findings

- Les aspects dominants n'étaient pas représentés comme runtime structuré.
- Le calcul inter-cartes devait préserver les codes de corps pour continuer à utiliser les règles d'orbes.

## Proposed changes

- Ajouter le runtime et l'évaluateur de dominants.
- Ajouter un calcul interchart qui conserve `planet_a`/`planet_b` et ajoute `chart_a`/`chart_b`.
- Exposer les helpers de calcul via le package calculators.

## Files to modify

- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/calculators/__init__.py`

## Files to delete

- Aucun.

## Tests to add or update

- Tests unitaires des dominants et du calcul interchart avec règles d'orbes.

## Risk assessment

- Risque principal: préfixer les corps interchart et casser les règles d'orbe. Couvert par test de luminaire/lune.

## Rollback strategy

- Revenir les modules dominants, le helper interchart et leurs exports/tests; aucune migration.

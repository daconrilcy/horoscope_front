# Implementation Plan

## Current architecture finding

Les tests cibles existent sous `backend/app/tests/unit` et sont collectes depuis `backend/`. Les anciens chemins restent dans certaines stories comme commandes actives ou comme preuves historiques.

## Selected approach

- Corriger les commandes actives dans les deux stories prompt-generation ciblees.
- Corriger `RG-020` pour pointer vers le chemin collecte.
- Conserver les mentions interdites/historiques uniquement avec classification dans `validation-path-audit.md`.

## Files to modify

- `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md`
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md`
- `_condamad/stories/align-prompt-generation-story-validation-paths/generated/*`

## Tests to run

- Targeted corrected pytest paths.
- Backend topology guards.
- Story validation/lint.
- `ruff check .`.

## Deletion candidates

None. This story removes obsolete active references, not files.

## No Legacy stance

No compatibility path, duplicated test file, or alternate collection root is permitted.

## Rollback strategy

Revert only this story's markdown changes if validation shows a corrected path is not collectable.

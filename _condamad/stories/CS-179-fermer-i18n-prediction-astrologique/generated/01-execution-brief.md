# Execution Brief

## Story

- Key: `CS-179-fermer-i18n-prediction-astrologique`
- Objective: fermer les mappings FR actifs sous `backend/app/domain/prediction` pour les libelles astrologiques publics.
- Boundary: backend prediction only; no frontend, no API contract shape change, no new dependency.

## Execution Rules

- Preserve existing dirty files outside the story.
- Keep `domain/prediction` free of `app.services` imports.
- Resolve DB-backed labels outside prediction and inject a runtime label contract.
- Do not keep wrappers, aliases, local fallback FR mappings, or renamed equivalents for the removed labels.

## Done Conditions

- AC1-AC6 have code and validation evidence.
- `prediction-i18n-before.md` and `prediction-i18n-after.md` exist.
- Guard `RG-110` is executable through `app/tests/unit/test_astrology_localization_guardrails.py`.
- Story status can move to `ready-to-review` after implementation, then `done` only after review is clean.

## Halt Conditions

- Missing source story or guardrail registry.
- Need for a new dependency.
- Required labels cannot be routed through an existing canonical resolver or runtime contract.
- Required validation repeatedly fails with no scoped fix.

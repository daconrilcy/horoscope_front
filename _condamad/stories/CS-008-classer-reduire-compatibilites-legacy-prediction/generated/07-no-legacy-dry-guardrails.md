# No Legacy / DRY Guardrails

## Story-specific forbidden surfaces

- `app.prediction.schemas.TimeBlock`
- `PredictionPersistenceService.save(engine_output=...)`
- `app.prediction.llm_narrator`
- `LLMNarrator`
- Any compatibility wrapper, alias, re-export or fallback replacing the deleted surfaces.

## Canonical destinations

- V3 time blocks: `app.prediction.schemas.V3TimeBlock`.
- V2 runtime blocks: `app.prediction.block_generator.TimeBlock`.
- Persistence service input: `bundle=`.
- Public prediction categories: retained as `external-active` until product/API decision.
- Narration: `AIEngineAdapter.generate_horoscope_narration`.

## Required negative evidence

- `test_prediction_removed_legacy_compatibility_surfaces_stay_removed` fails if `schemas.TimeBlock` or `save(engine_output=...)` returns.
- `test_llm_narrator_deprecation_guard.py` fails if `LLMNarrator` or direct OpenAI runtime returns.
- `rg -n "EngineOutput|TimeBlock|engine_output=|\bcategories\b|LLMNarrator" app tests` hits must be classified.

## Exceptions

- `EngineOutput` remains classified `canonical-active` for existing V2 editorial/persistence code.
- `categories` remains classified `external-active` because frontend code consumes it.

## Reviewer questions

- Is `EngineOutput` classification acceptable as canonical-active until a dedicated V2 DTO migration?
- Does the new guard block the deleted compatibility keyword narrowly enough without blocking public projection `engine_output` context?
- Are public `categories` consumers sufficient external evidence to defer deletion?

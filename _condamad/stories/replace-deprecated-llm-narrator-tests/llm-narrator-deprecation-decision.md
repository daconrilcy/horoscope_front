# LLMNarrator Deprecation Decision

## Decision

- `LLMNarrator` is not a nominal test dependency for prediction narration.
- Prediction narration tests must target `AIEngineAdapter.generate_horoscope_narration`.
- The `app.prediction.llm_narrator` module may still host shared result DTOs until a separate DTO ownership story moves them.

## Scope

- Forbidden in backend tests: importing the `LLMNarrator` class, instantiating it, or patching its `narrate` method as nominal behavior.
- Allowed in this story: `NarratorResult`, `NarratorAdvice`, `llm_narrator_enabled`, and historical evidence artifacts.

## Expiry

- Class-level compatibility exceptions expire immediately for nominal tests.
- Any future exception must name a consumer, owner, expiry condition, and a targeted guard update before implementation.

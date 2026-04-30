# No Legacy / DRY Guardrails

## Canonical path

- Canonical owner: `AIEngineAdapter.generate_horoscope_narration`.
- Existing DTO reuse allowed: `NarratorResult` and `NarratorAdvice`.
- Legacy class under guard: `LLMNarrator`.

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior
- `from app.prediction.llm_narrator import LLMNarrator` in tests.
- `LLMNarrator()` in tests.
- `patch("app.prediction.llm_narrator.LLMNarrator.narrate")` as nominal prediction coverage.
- Global or broad `DeprecationWarning` ignores to silence this story.

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration
- Persisted decision for any remaining `LLMNarrator` compatibility test.
- Negative scan evidence for class imports/instantiations/patches.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
- Do remaining `llm_narrator` hits only refer to DTOs/config or explicitly classified artifacts?

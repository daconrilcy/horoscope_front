# Execution Brief — replace-deprecated-llm-narrator-tests

## Primary objective

Replace nominal `LLMNarrator` test coverage with canonical `AIEngineAdapter.generate_horoscope_narration` coverage, then prove prediction tests no longer emit unclassified `DeprecationWarning`.

## Boundaries

- Touch only prediction LLM narration tests and story evidence artifacts.
- Keep production behavior unchanged.
- Do not move `NarratorResult` / `NarratorAdvice` DTOs in this story.
- Do not delete `app.prediction.llm_narrator`; this story removes nominal test usage, not the module.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Reuse existing adapter and horoscope narration service test patterns.
- Add a deterministic guard for `LLMNarrator` class imports/instantiations/patches in tests.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md` and `llm-narrator-warnings-after.md` exist.
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` exists.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.

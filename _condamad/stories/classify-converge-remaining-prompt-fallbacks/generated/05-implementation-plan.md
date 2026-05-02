# Implementation Plan

## Current findings

- `PROMPT_FALLBACK_CONFIGS` initially contained 8 keys.
- `seed_29_prompts.py`, `seed_guidance_prompts.py` and `seed_66_20_taxonomy.py`
  already own canonical prompt/assembly paths for the migrated guidance/natal keys.
- `gateway.py` already rejects missing supported assemblies in production with
  `missing_assembly`.
- `test_natal` and `test_guidance` are synthetic test fixtures.

## Selected approach

1. Remove all non-fixture prompt entries from `PROMPT_FALLBACK_CONFIGS`.
2. Keep `PROMPT_RUNTIME_DATA` unchanged for model/schema/runtime metadata.
3. Add tests that:
   - keep the remaining fallback keys exact;
   - prove converged keys do not build fallback configs;
   - require the persistent audit to list every reviewed key.
4. Persist before/after classification in `fallback-classification.md`.
5. Run targeted tests, nearby runtime tests, scans, lint and regression.

## Files to modify

- `backend/app/domain/llm/prompting/catalog.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md`
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/generated/*.md`

## No Legacy stance

No compatibility wrapper, alias, repointed fallback prompt or second runtime
fallback registry is allowed. Removed keys must not produce
`UseCaseConfig` through `build_fallback_use_case_config`.

## Rollback strategy

Revert the catalog removal and related tests/evidence for this story only.
Do not touch pre-existing `backend/horoscope.db` changes.

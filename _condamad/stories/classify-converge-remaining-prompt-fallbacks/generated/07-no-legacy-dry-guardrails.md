# No Legacy / DRY Guardrails

## Canonical ownership

- Durable prompt instructions belong to governed DB prompts and assemblies.
- `PROMPT_FALLBACK_CONFIGS` may keep only synthetic test fixtures.
- Runtime metadata in `PROMPT_RUNTIME_DATA` may remain because it does not own prompt text.
- Missing assemblies in production must fail with `missing_assembly`.

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior
- Repointing a removed fallback prompt to another fallback prompt
- Any new `PROMPT_FALLBACK_CONFIGS` key outside `test_natal` and `test_guidance`
- `build_fallback_use_case_config` returning a config for:
  - `natal_long_free`
  - `natal_interpretation_short`
  - `guidance_daily`
  - `guidance_weekly`
  - `event_guidance`
  - `astrologer_selection_help`

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration
- Classification of every hit for the story-specific fallback scans.

## Allowed exceptions

| Key | Decision | Boundary |
|---|---|---|
| `test_natal` | fixture | synthetic orchestration/admin tests only |
| `test_guidance` | fixture | synthetic orchestration/compose tests only |

## Required evidence

- `fallback-classification.md` before/after inventory for all 8 reviewed keys.
- Exact allowlist test for remaining `PROMPT_FALLBACK_CONFIGS` keys.
- Builder guard proving removed keys return `None`.
- Production `missing_assembly` tests remain green.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?

# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/classify-converge-remaining-prompt-fallbacks/00-story.md`
- Initial `git status --short`: pre-existing `M backend/horoscope.db`; access warnings for pytest temp artifact directories.
- AGENTS.md considered: root `AGENTS.md` supplied in prompt and read from disk.
- Regression guardrails read: `_condamad/stories/regression-guardrails.md`; applicable RG-018, RG-019, RG-020, RG-021.
- Capsule generated: yes, via `condamad_prepare.py`.

## Search and inspection notes

- Inspected `catalog.py`, `gateway.py`, `canonical_use_case_registry.py`,
  `seed_29_prompts.py`, `seed_guidance_prompts.py`, `seed_66_20_taxonomy.py`
  and the required orchestration tests.
- Baseline fallback keys were:
  `natal_long_free`, `natal_interpretation_short`, `guidance_daily`,
  `guidance_weekly`, `event_guidance`, `astrologer_selection_help`,
  `test_natal`, `test_guidance`.
- Canonical prompt seeds exist for `natal_interpretation_short`,
  `guidance_daily`, `guidance_weekly` and `event_guidance`.

## Implementation notes

- Removed all non-fixture prompt entries from `PROMPT_FALLBACK_CONFIGS`.
- Kept runtime metadata in `PROMPT_RUNTIME_DATA`.
- Added audit coverage and builder guards.
- Added persistent classification audit with before/after inventory.

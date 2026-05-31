# CONDAMAD Implementation Review - CS-416

Verdict: CLEAN

## Scope

- Target story: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- Source brief: `_story_briefs/cs-416-contraindre-payload-llm-basic-par-reading-plan.md`
- Tracker row: verified path and source brief match CS-416.
- Review type: implementation, tests, evidence, guardrails and AC alignment.

## Review Iterations

- Iteration 1 verdict: CHANGES_REQUESTED.
- Iteration 2 verdict: CLEAN after code, tests and evidence corrections.

## Issues Fixed

- Full provider payload test failed because a historical profile test still assumed Basic exposed `interpretation_material`.
- Basic prompt style allowed 6 to 8 sections, while delivery and output contracts still capped Basic at 6.
- Basic payload tests imported a helper from another `test_*.py` module.
- Big Bang integration fixture could not build Basic after the reading-plan requirement.
- `basic-payload-after.json`, `validation.txt` and this review artifact needed refresh after fixes.

## Validation Results

- `ruff format` scoped: PASS.
- `ruff check .`: PASS.
- `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short`: PASS, 5 passed.
- `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`: PASS, 14 passed.
- `python -B -m pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short`: PASS, 7 passed.
- `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py -k "natal or basic" --tb=short`: PASS, 4 passed, 10 deselected.
- `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --long --tb=short`: PASS, 3 passed.
- `python -B -c "from app.main import app; assert app.title == 'horoscope-backend'"`: PASS.
- `condamad_validate.py <capsule> --final`: PASS.
- `condamad_story_validate.py <00-story.md>`: PASS.
- `condamad_story_lint.py --strict <00-story.md>`: PASS.
- `git diff --check` scoped paths: PASS.

## Guardrail Alignment

- `RG-149`, `RG-152`, `RG-154`, `RG-156`, `RG-164` and `RG-165`: covered by Basic payload tests, architecture guard and targeted scans.
- `RG-013` adjacency: fixed for the new Basic helper by moving the shared plan fixture to a non-executable helper module.
- Residual `rg` matches for raw natal carriers remain in non-Basic or non-prompt-visible runtime, schema and service owner surfaces.

## Final Finding Summary

No actionable implementation issue remains. The Basic provider payload is derived from `BasicNatalReadingPlan`, excludes forbidden prompt-visible carriers, aligns style/output section constraints to 8, and keeps Free/Premium material paths usable.

## Propagation

`no-propagation`: corrections are local to CS-416 implementation, tests and evidence.

## Residual Risk

Existing broad natal runtime files still contain `chart_json`, `natal_data`, `user_id` and coordinates outside the Basic prompt payload boundary. This remains classified as non-Basic or non-prompt-visible residual surface and is covered by tests/scans.

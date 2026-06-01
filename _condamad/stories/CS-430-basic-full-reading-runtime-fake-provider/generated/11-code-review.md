# CS-430 Implementation Review

Verdict: CLEAN

## Scope reviewed

- Story: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/00-story.md`
- Source brief: `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- Tracker row: `_condamad/stories/story-status.md`
- Guardrails: RG-150, RG-152, RG-155, RG-157, RG-164, RG-165, RG-166, RG-167, RG-168, RG-169
- Implementation files: Basic runtime, Basic material builder, slot/run persistence, run model, migration, and integration tests.

## Iteration 1 findings

1. Rejected idempotency keys were not terminal.
   A repeated call with the same `client_request_id` after rejection could reuse and mutate the rejected run.
   Fix: terminal rejected runs now return cached rejection evidence without provider reprocessing, public publication, or quota debit.
   Proof: `test_basic_runtime_rejected_idempotency_key_keeps_terminal_run`.

2. The legacy Basic wrapper passed `natal_result` positionally to a keyword-only builder.
   Fix: `interpretation_service.py` now calls `build_basic_natal_reading_plan_for_runtime(natal_result=...)`.
   Proof: lint and targeted Basic runtime tests pass with the corrected call site.

## Fresh review result

- Basic `generate_full` resolves to `theme_natal.reading.basic_full_reading.v1`.
- Prompt-visible payload construction uses `BasicNatalReadingPlan`.
- Valid fake output accepts and persists technical run metadata plus one public slot projection.
- Invalid fake modes reject before public projection and leave quota untouched.
- Accepted and rejected idempotency paths keep terminal state stable.
- Public payloads exclude raw provider response, parsed raw response, and provider mode.
- Free preview remains contractual and non-generative.
- Guardrail scans have only expected or allowed hits outside the CS-430 runtime.

No actionable implementation issue remains.

## Validation evidence

- `ruff check .`: PASS.
- `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py --tb=short`: PASS, 12 passed.
- `python -B -m pytest -q --long tests\integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short`: PASS, 20 passed.
- `python -B -m pytest -q --long tests\integration\test_theme_natal_reading_slots.py --tb=short`: PASS, 8 passed.
- `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py -k invalid_modes --tb=short`: PASS, 7 passed.
- Legacy branch scan: PASS_WITH_ALLOWED_HITS, existing service/test references only.
- Runtime symbol scan: PASS_WITH_EXPECTED_HITS, canonical owners and tests.
- Raw provider scan: PASS_WITH_ALLOWED_TECHNICAL_HITS, technical storage and negative assertions only.
- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Skipped validation

- `python -B -m pytest -q --tb=short` was not rerun because the prior implementation attempt timed out after 244s.
  The story-required targeted checks passed after this review/fix cycle.

## Closure

- Tracker row set to `done` with matching story path and source brief.
- Story header set to `done`.
- Propagation: no-propagation; findings were local implementation defects fully covered by CS-430 tests and evidence.

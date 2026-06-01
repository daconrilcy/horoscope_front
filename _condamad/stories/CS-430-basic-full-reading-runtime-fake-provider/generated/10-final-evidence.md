# Final Evidence — CS-430-basic-full-reading-runtime-fake-provider

## Story status

- Validation outcome: PASS
- Fresh implementation review: CLEAN
- Story key: CS-430-basic-full-reading-runtime-fake-provider
- Source story: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/00-story.md`
- Capsule path: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider`
- Status registry: `_condamad/stories/story-status.md` set to `done`

## Review/fix cycle

- Iteration 1 review found two actionable implementation issues.
- Finding 1: rejected idempotency keys could re-enter provider execution and mutate a terminal rejected run.
- Finding 2: `interpretation_service.py` called the shared Basic plan builder with a positional argument despite its keyword-only signature.
- Fix 1: `ThemeNatalBasicFullReadingRuntime` now returns the existing rejected run result without reprocessing the provider or debiting quota.
- Fix 2: the Basic legacy wrapper now calls `build_basic_natal_reading_plan_for_runtime` with `natal_result=`.
- Regression proof: `test_basic_runtime_rejected_idempotency_key_keeps_terminal_run` was added.
- Propagation: no-propagation; the corrections are local to CS-430 implementation behavior and evidence.

## AC validation

| AC range | Result | Evidence |
|---|---|---|
| AC1-AC6 | PASS | Runtime accepted-path test proves resolver contract, plan-backed payload, strict parse, run metadata, slot persistence, and no raw public fields. |
| AC7-AC13 | PASS | Parameterized fake-provider invalid-mode tests reject every invalid mode before public projection. |
| AC14-AC15 | PASS | Quota side effect asserts accepted slot exists before debit; accepted and rejected idempotency tests keep terminal state stable. |
| AC16-AC17 | PASS | AST guard and Free preview contractual test pass; scans captured. |
| AC18 | PASS | Evidence artifacts persisted under `evidence/`; generated review and final evidence updated. |

## Commands run

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `ruff format app\services\llm_generation\natal\theme_natal_basic_full_runtime.py app\services\llm_generation\natal\interpretation_service.py tests\integration\test_theme_natal_basic_full_reading_runtime.py` | `backend` | PASS | shell output |
| `ruff check app\services\llm_generation\natal\theme_natal_basic_full_runtime.py app\services\llm_generation\natal\interpretation_service.py tests\integration\test_theme_natal_basic_full_reading_runtime.py` | `backend` | PASS | shell output |
| `ruff check .` | `backend` | PASS | `evidence/validation.txt` |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py --tb=short` | `backend` | PASS, 12 passed | `evidence/runtime-after.txt` |
| `python -B -m pytest -q --long tests\integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short` | `backend` | PASS, 20 passed | `evidence/validation.txt` |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_reading_slots.py --tb=short` | `backend` | PASS, 8 passed | `evidence/persistence-after.txt` |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py -k invalid_modes --tb=short` | `backend` | PASS, 7 passed | `evidence/fake-provider-modes.txt` |
| `rg -n "natal_interpretation_short\|natal_long_free\|natal_interpretation" backend/app/services backend/tests/integration` | repo root | PASS_WITH_ALLOWED_HITS | `evidence/validation.txt` |
| `rg -n "basic_full_reading\|fake_provider\|ThemeNatalReadingSlot\|LlmGenerationRun\|free_preview" backend/app backend/tests` | repo root | PASS_WITH_EXPECTED_HITS | `evidence/validation.txt` |
| `rg -n "raw_provider_response\|provider_raw\|raw_response" backend/app/services backend/tests/integration` | repo root | PASS_WITH_ALLOWED_TECHNICAL_HITS | `evidence/validation.txt` |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-430-basic-full-reading-runtime-fake-provider\00-story.md` | repo root | PASS | `evidence/validation.txt` |
| `python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-430-basic-full-reading-runtime-fake-provider\00-story.md` | repo root | PASS | `evidence/validation.txt` |

## Commands skipped

- `python -B -m pytest -q --tb=short`: skipped after the prior implementation run timed out at 244s in this shell.
  The story-required targeted integration tests, persistence tests, lint, and guardrail scans passed after the fixes.
- Local app server start: not run because CS-430 changes a backend service/runtime path and no API/frontend server surface.

## Files changed by review/fix

- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/00-story.md`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/fake-provider-modes.txt`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-after.txt`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/validation.txt`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/generated/10-final-evidence.md`
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/generated/11-code-review.md`
- `_condamad/stories/story-status.md`

## Remaining risks

- Full default pytest was not rerun because the prior attempt timed out in the Codex shell.
  No story-required targeted validation remains failing or skipped.

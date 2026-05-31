# Final Evidence — CS-416-contraindre-payload-llm-basic-par-reading-plan

## Story status

- Validation outcome: passed
- Ready for review: yes
- Story key: CS-416-contraindre-payload-llm-basic-par-reading-plan
- Source story: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- Capsule path: `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan`
- Story registry target row verified against source brief: `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` was already modified before implementation.
- Capsule status: generated files repaired on canonical capsule; accidental duplicate `_condamad/stories/cs-416` created by helper was removed during this run.
- Existing `generated/11-code-review.md`: drafting-stage editorial review only; not used as final review evidence.
- Guardrails classified applicable: `RG-002`, `RG-022`, `RG-149`, `RG-152`, `RG-154`, `RG-156`, `RG-164`, `RG-165`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC14 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present; concrete validation recorded below. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Current file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Basic path requires `BasicNatalReadingPlan`. | Basic payload pytest. | PASS | |
| AC2 | Basic prompt payload sections and syntheses projected from plan sections. | Contract shape pytest. | PASS | |
| AC3 | Basic provider input contains `basic_natal_prompt_payload`. | Provider builder pytest. | PASS | |
| AC4 | No `NatalResult` or chart JSON builder in Basic provider owner. | AST guard pytest. | PASS | |
| AC5 | Prompt-visible Basic payload excludes PII. | Token pytest plus scan classification. | PASS | |
| AC6 | Sanitized `editorial_evidence` emitted. | Contract shape pytest. | PASS | |
| AC7 | Internal scores absent from Basic prompt payload. | Token pytest plus scan classification. | PASS | |
| AC8 | Word count, section count, `vous`, no firm prediction, no prescriptive advice emitted. | Style constraint pytest. | PASS | |
| AC9 | `chart_json` absent from Basic prompt payload. | Token pytest and architecture pytest. | PASS | |
| AC10 | Basic top-level provider assembly remains usable. | Provider builder pytest. | PASS | |
| AC11 | Premium assembly path remains usable. | Provider builder pytest. | PASS | |
| AC12 | Evidence artifacts persisted. | VC10 file check. | PASS | |
| AC13 | Internal source paths absent from Basic prompt payload. | Token pytest. | PASS | |
| AC14 | Raw evidence IDs absent from provider editorial evidence. | Editorial evidence pytest. | PASS | |

## Implementation summary

- Basic provider payload now requires `BasicNatalReadingPlan` and refuses Basic assembly without it.
- Basic `input_data` now exposes one prompt-visible block: `basic_natal_prompt_payload`.
- `basic_natal_prompt_payload` contains `sections`, `resolved_syntheses`, sanitized `editorial_evidence`, `limitations`, `disclaimers`, and `style_constraints`.
- Free/Premium provider payload paths keep the previous interpretation material, selected themes, facts and birth context structure.
- `THEME_ASTRAL_INPUT_SCHEMA` declares both the classic provider input shape and the Basic prompt payload variant.

## Files changed

- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-before.json`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/generated/10-final-evidence.md`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`.
- Updated provider builder tests for the new Basic shape and Premium no-regression.
- Updated architecture guard for Basic plan ownership and raw runtime exclusion.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | repo root | PASS | Canonical capsule repaired. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | repo root | PASS | Capsule structure valid. |
| `ruff format app/domain/llm/configuration/theme_astral_contracts.py app/domain/llm/runtime/theme_astral_provider_payload_builder.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py tests/architecture/test_llm_astrology_input_payload_boundaries.py` | `backend` | PASS | Scoped formatting complete. |
| `ruff check .` | `backend` | PASS | All checks passed. |
| `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short` | `backend` | PASS | 5 passed. |
| `python -B -m pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short` | `backend` | PASS | 7 passed. |
| `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py -k "natal or basic" --tb=short` | `backend` | PASS | 4 passed, 10 deselected. |
| `rg -n "chart_json\|natal_data\|email\|user_id\|place_id\|latitude\|longitude" app/domain/llm app/services/llm_generation/natal` | `backend` | PASS_WITH_LIMITATIONS | Existing non-Basic/non-prompt-visible matches remain; Basic prompt payload tests prove absence from `basic_natal_prompt_payload`. |
| `rg -n "ranking_score\|condition_axis\|score_profile\|weighted_score\|prompt_hint" app/domain/llm app/services/llm_generation/natal` | `backend` | PASS_WITH_LIMITATIONS | Existing validator denylist literal remains; Basic prompt payload tests prove absence. |
| `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt').exists()"` | `backend` | PASS | Evidence file exists. |
| `python -B -c "from app.main import app; assert app.title == 'horoscope-backend'"` | `backend` | PASS | App imports locally. |

## Commands skipped or blocked

- Full backend pytest suite not run; story validation plan only required focused payload, architecture and provider tests. Compensating evidence: Ruff full backend check plus targeted runtime and architecture tests.

## DRY / No Legacy evidence

- One Basic provider prompt serializer owns the new payload boundary: `_basic_natal_prompt_payload`.
- No fallback Basic payload is kept: missing `BasicNatalReadingPlan` raises `ValueError`.
- Raw `NatalResult`, `build_chart_json`, `chart_json`, `natal_data`, PII fields, scores, source paths and evidence IDs are absent from the Basic prompt payload tests.

## Diff review

- `git diff --stat` reviewed for touched backend/story surfaces.
- Unrelated dirty file preserved: `_condamad/run-state.json`.

## Final worktree status

- Expected story changes plus pre-existing `_condamad/run-state.json`.

## Remaining risks

- Existing broad natal runtime files still contain `chart_json`, `natal_data`, `user_id` and coordinates outside the Basic prompt payload boundary; this is documented as non-Basic/non-prompt-visible residual surface, not changed in this story.

## Suggested reviewer focus

- Verify that the Basic provider payload shape is acceptable with one `basic_natal_prompt_payload` block while Free/Premium continue using the previous provider input shape.

## Feedback loop routing

- `no-propagation`: no reusable process or skill correction beyond this story evidence.

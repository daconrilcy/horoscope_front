# Final Evidence — CS-430-basic-full-reading-runtime-fake-provider

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: CS-430-basic-full-reading-runtime-fake-provider
- Source story: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/00-story.md`
- Capsule path: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider`
- Status registry: `_condamad/stories/story-status.md` set to `ready-to-review`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `_condamad/run-state.json` dirty.
- Story/status alignment: CS-430 row path and brief source match the requested story and brief.
- Guardrails classified applicable: RG-150, RG-152, RG-155, RG-157, RG-164, RG-165, RG-166, RG-167, RG-168, RG-169.
- Pre-implementation `generated/11-code-review.md`: classified obsolete editorial review, not final implementation review evidence.

## Implementation summary

- Added `ThemeNatalBasicFullReadingRuntime` for Basic `generate_full` -> `theme_natal.reading.basic_full_reading.v1`.
- Added deterministic non-live fake provider modes: valid, invalid JSON, unknown field, empty source, invented fact, technical leak, mechanical phrase, short section.
- Added shared Basic runtime material builder so Basic payload construction reuses `BasicNatalReadingPlan` without copying plan assembly.
- Added explicit run metadata fields for generation contract key/hash/snapshot and provider mode, plus Alembic revision `20260601_0143`.
- Preserved public/technical separation: accepted public payload is on `ThemeNatalReadingSlot`; raw provider evidence stays on `LlmGenerationRun`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status set to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Repaired by capsule helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC18 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Repaired by capsule helper. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Repaired by capsule helper; executed targeted plan. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Repaired by capsule helper. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Current file. |

## Files changed

- Backend runtime: `backend/app/services/llm_generation/natal/basic_natal_runtime_material.py`, `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`.
- Persistence: `backend/app/infra/db/models/llm_generation_run.py`, `backend/migrations/versions/20260601_0143_add_theme_natal_run_contract_metadata.py`.
- Tests: `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`, `backend/tests/integration/test_theme_natal_reading_slots.py`.
- Evidence/capsule: `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/**`, `_condamad/stories/story-status.md`.

## Files deleted

- none.

## Tests added or updated

- Added `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`.
- Updated `backend/tests/integration/test_theme_natal_reading_slots.py` for the new run metadata columns and service signature.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Basic resolver path in `ThemeNatalBasicFullReadingRuntime.generate`. | Targeted runtime pytest PASS. | PASS | Contract key asserted. |
| AC2 | `BasicNatalReadingPlan` material builder + `build_basic_natal_prompt_payload`. | Targeted runtime pytest PASS. | PASS | Prompt sections asserted. |
| AC3 | Strict raw schema validation. | Targeted runtime pytest PASS. | PASS | Valid fake accepted. |
| AC4 | Run metadata columns and runtime persistence. | Runtime and slot schema pytest PASS. | PASS | Migration added. |
| AC5 | Accepted slot publication service. | Runtime pytest PASS. | PASS | Public slot asserted. |
| AC6 | Public projection excludes raw fields. | Runtime pytest + raw leak scan PASS_WITH_ALLOWED_HITS. | PASS | Raw stays technical. |
| AC7 | Invalid JSON fake mode. | Invalid-mode pytest PASS. | PASS | Rejected run. |
| AC8 | Unknown field fake mode. | Invalid-mode pytest PASS. | PASS | Extra forbidden. |
| AC9 | Empty source fake mode. | Invalid-mode pytest PASS. | PASS | Rejected before public. |
| AC10 | Invented fact fake mode. | Invalid-mode pytest PASS. | PASS | Source not in Basic plan. |
| AC11 | Technical leak fake mode. | Invalid-mode pytest PASS. | PASS | Leak token rejected. |
| AC12 | Mechanical phrase fake mode. | Invalid-mode pytest PASS. | PASS | Phrase rejected. |
| AC13 | Short section fake mode. | Invalid-mode pytest PASS. | PASS | Pydantic length rejected. |
| AC14 | Quota after acceptance. | Runtime pytest PASS. | PASS | Side effect sees accepted slot. |
| AC15 | Idempotence. | Runtime pytest PASS. | PASS | Same request keeps one run/slot. |
| AC16 | No old natal use-case calls. | AST guard pytest PASS; scan captured. | PASS | Existing legacy hits are outside new runtime. |
| AC17 | Contractual Free preview. | Runtime pytest PASS. | PASS | No `natal_long_free` call. |
| AC18 | Evidence artifacts persisted. | Capsule validation final gate. | PASS | Evidence files created. |

| AC range | Result | Evidence |
|---|---|---|
| AC1-AC6 | PASS | Runtime accepted-path test proves resolver contract, plan-backed payload, strict parse, run metadata, slot persistence, public no raw fields. |
| AC7-AC13 | PASS | Parameterized fake-provider invalid-mode tests reject every invalid mode before public projection. |
| AC14-AC15 | PASS | Quota side effect asserts accepted slot exists before debit; idempotence test proves one run/slot for same request. |
| AC16-AC17 | PASS | AST guard and Free preview contractual test pass; scans captured. |
| AC18 | PASS | Evidence artifacts persisted under `evidence/`; generated traceability and final evidence updated. |

## Commands run

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `ruff format <touched python files>` | `backend` | PASS | shell output |
| `ruff check .` | `backend` | PASS | `evidence/validation.txt` |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py --tb=short` | `backend` | PASS, 11 passed | `evidence/runtime-after.txt`, `evidence/validation.txt` |
| `python -B -m pytest -q --long tests\integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short` | `backend` | PASS, 19 passed | `evidence/validation.txt` |
| `python -B -m pytest -q --long tests\integration\test_theme_natal_reading_slots.py --tb=short` | `backend` | PASS, 8 passed | `evidence/persistence-after.txt`, `evidence/validation.txt` |
| `rg -n "natal_interpretation_short\|natal_long_free\|natal_interpretation" backend/app/services backend/tests/integration` | repo root | PASS_WITH_ALLOWED_HITS | `evidence/legacy-call-scan-after.txt` |
| `rg -n "basic_full_reading\|fake_provider\|ThemeNatalReadingSlot\|LlmGenerationRun\|free_preview" backend/app backend/tests` | repo root | PASS_WITH_EXPECTED_HITS | `evidence/runtime-symbol-scan-after.txt` |
| `rg -n "raw_provider_response\|provider_raw\|raw_response" backend/app/services backend/tests/integration` | repo root | PASS_WITH_ALLOWED_TECHNICAL_HITS | `evidence/public-raw-leak-scan-after.txt` |

## Commands skipped or blocked

- `python -B -m pytest -q --tb=short` timed out after 244s in the Codex shell. Compensating evidence: all capsule-required targeted integration tests, slot persistence tests, scans, and `ruff check .` passed.
- Local app server start was not run because this story is backend service/runtime only and no API/frontend surface was changed.

## DRY / No Legacy evidence

- The Basic plan assembly is centralized in `basic_natal_runtime_material.py` and reused by the old service wrapper and the new runtime.
- No live provider client or frontend code was added.
- No compatibility shim, fallback route, or legacy generation path was added.
- Rejected fake-provider output is stored only on technical runs and never published to public slots.

## Diff review

- `git diff --check -- <story paths>`: PASS, only CRLF warnings from Git.
- Unrelated pre-existing dirty file remains `_condamad/run-state.json`.

## Final worktree status

- Modified story/code/test/evidence files are expected for CS-430.
- Pre-existing dirty file still present: `_condamad/run-state.json`.

## Remaining risks

- Full default pytest did not finish inside the available shell timeout; review should focus on targeted runtime behavior and migration compatibility.

## Suggested reviewer focus

- Confirm the new `llm_generation_runs` metadata columns and migration are acceptable for CS-430's contract metadata requirement.

## Feedback loop routing

- no-propagation: no reusable process issue beyond the local full-suite timeout.

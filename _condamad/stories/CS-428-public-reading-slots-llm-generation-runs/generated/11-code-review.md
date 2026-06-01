# CS-428 Implementation Review

Verdict: CLEAN

## Scope

- Story: `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/00-story.md`
- Brief: `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- Tracker row: `CS-428`, matching path and source brief, status `done`.
- Reviewed implementation: backend slot/run models, service, migration, integration/unit tests and CONDAMAD evidence.
- Guardrails checked: `RG-011`, `RG-150`, `RG-152`, `RG-155`, `RG-157`, `RG-168`.

## Iterations

- Iteration 1 found one actionable implementation/proof issue:
  - AC7/AC8 required an explicit concurrency mechanism and proof, but the service only relied on sequential tests plus DB uniqueness.
- Fix applied:
  - Added application locks for slot claim and accepted publication.
  - Made accepted publication atomic with `UPDATE ... WHERE status != accepted`.
  - Added a concurrent app-lock serialization test.
- Iteration 2 fresh review found no remaining actionable implementation issue.

## AC Alignment

- AC1-AC4: PASS; slot/run tables, model exports, statuses and unique indexes are present and tested.
- AC5-AC6: PASS; rejected runs do not mutate accepted payloads and public lookup/list returns accepted slots only.
- AC7: PASS; app lock plus DB unique constraint/`IntegrityError` recovery prevent duplicate slot claims.
- AC8: PASS; accepted publication is atomic and quota debit remains gated by `accepted_now`.
- AC9-AC10: PASS; `slot_id + client_request_id` unique index and idempotent run lookup are tested.
- AC11: PASS; `chart_id` participates in model, indexes, service key and tests.
- AC12: PASS; `created_at` remains stable and `accepted_at` changes only on first acceptance.

## Validation

- `ruff format app\services\llm_generation\natal\theme_natal_reading_slots.py tests\integration\test_theme_natal_reading_slots.py`: PASS
- `ruff check app\services\llm_generation\natal\theme_natal_reading_slots.py tests\integration\test_theme_natal_reading_slots.py`: PASS
- `ruff check .`: PASS
- `python -B -m pytest -q --long tests/integration/test_theme_natal_reading_slots.py --tb=short`: PASS, 8 passed
- `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`: PASS, 5 passed
- `python -B -m pytest -q app/tests/unit/test_backend_db_test_harness.py --tb=short`: PASS, 4 passed
- `python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`: PASS, 8 passed
- `python -B -c "from app.main import app; print(len(app.routes))"`: PASS, 230 routes
- `git diff --check`: PASS, CRLF warnings only

## Scans

- `rg -n "ThemeNatalReadingSlot|LlmGenerationRun|accepted_at|source_generation_run_id" backend/app backend/tests`: expected hits
- `rg -n "client_request_id|idempot" backend/app backend/tests`: expected hits
- `rg -n "UserNatalInterpretationModel\.user_id == user_id,[\s\S]*UserNatalInterpretationModel\.level" backend/app/services/llm_generation/natal`: PASS, no matches
- `rg -n "_slot_lock_for_key|_publication_lock_for_slot|status != THEME_NATAL_SLOT_STATUS_ACCEPTED" backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`: PASS

## Closure

- Findings fixed: concurrency/validation proof gap.
- Findings rejected: none.
- Propagation: no-propagation; correction is local to CS-428 implementation/evidence.
- Residual risk: full backend pytest was not run; targeted story and guardrail validations passed.

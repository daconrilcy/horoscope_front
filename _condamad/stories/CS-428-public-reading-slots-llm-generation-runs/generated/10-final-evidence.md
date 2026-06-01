# Final Evidence — CS-428-public-reading-slots-llm-generation-runs

## Story status

- Validation outcome: PASS with scoped regression suite.
- Ready for review: yes.
- Story key: CS-428-public-reading-slots-llm-generation-runs.
- Source story: `00-story.md`.
- Capsule path: `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs`.
- Tracker row: `CS-428` set to `ready-to-review` on `2026-06-01`.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: `_condamad/run-state.json` was already modified.
- Story/status/brief alignment: PASS.
- Capsule preparation: missing generated files repaired with `condamad_prepare.py --repair-generated-only`; validation PASS.
- Existing `generated/11-code-review.md`: editorial pre-implementation review, classified obsolete for final implementation proof.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Capsule repaired by helper. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC12 traced. |
| `generated/04-target-files.md` | yes | yes | PASS | Story surface listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executed/skipped checks recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Guardrails classified. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final implementation evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Slot model + migration + service. | Integration slot suite + schema evidence. | PASS | Public slot state stored. |
| AC2 | Run model + migration + service. | Integration slot suite + schema evidence. | PASS | Technical attempt state stored. |
| AC3 | Partial unique slot indexes. | Schema test + Alembic proof. | PASS | Full product key includes nullable persona handling. |
| AC4 | Slot status constants + CheckConstraint. | Schema test + lint. | PASS | Approved lifecycle only. |
| AC5 | Rejected run writer avoids slot payload mutation. | Rejected-run and rejected-boundary tests. | PASS | Accepted payload unchanged. |
| AC6 | Public service filters accepted slots. | Accepted-only public lookup/list test. | PASS | Runs are not public source. |
| AC7 | Claim uses unique constraints and `IntegrityError` recovery. | Duplicate product slot claim test. | PASS | One slot per product key. |
| AC8 | Publication exposes `accepted_now` and quota gate. | Quota unit test + publication-once test. | PASS | Debit only on new acceptance. |
| AC9 | Run lookup by `slot_id + client_request_id`. | Same request id test. | PASS | Same logical state. |
| AC10 | Unique run index for client request id. | Same request id run count test. | PASS | No extra run. |
| AC11 | `chart_id` on key/model/indexes. | Chart identity test + targeted scan. | PASS | Distinct charts get distinct slots. |
| AC12 | Service writes `accepted_at` only on first acceptance. | Payload stability test. | PASS | `created_at` preserved. |

## Files changed

- Backend models: `backend/app/infra/db/models/__init__.py`, `backend/app/infra/db/models/theme_natal_reading_slot.py`, `backend/app/infra/db/models/llm_generation_run.py`.
- Backend service: `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`.
- Migration: `backend/migrations/versions/20260601_0142_create_theme_natal_reading_slots.py`.
- Tests: `backend/tests/integration/test_theme_natal_reading_slots.py`, `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
- Evidence/status: `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/**`, `_condamad/stories/story-status.md`.

## Files deleted

- `_condamad/stories/cs-428/` removed as an accidental parallel capsule from an ambiguous prepare attempt.

## Tests added or updated

- Added 7 integration tests for slot/run schema, product-key uniqueness, accepted-only lookup/list, rejected run isolation, `client_request_id` idempotence and one-time acceptance.
- Updated quota unit tests to assert slot publication debits quota only when `accepted_now=True`.

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `ruff format <changed python files>` | `backend` | PASS | Scoped formatting only. |
| `ruff check <changed python files>` | `backend` | PASS | Targeted lint clean. |
| `ruff check .` | `backend` | PASS | Backend lint clean. |
| `python -B -m pytest -q --long tests/integration -k "theme_natal and slot" --tb=short` | `backend` | PASS | 7 passed. |
| `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short` | `backend` | PASS | 5 passed. |
| `python -B -m pytest -q --long tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short` | `backend` | PASS | 8 passed. |
| `python -B -m pytest -q app/tests/unit/test_backend_db_test_harness.py tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_rejected_narrative_answer_boundary.py tests/architecture/test_narrative_natal_reading_public_boundary.py tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short` | `backend` | PASS | 42 guardrail tests passed. |
| Temp SQLite Alembic upgrade to `head` + schema inspection | `backend` | PASS | `evidence/schema-after.txt`. |
| `python -B -m alembic heads` | `backend` | PASS | `20260601_0142 (head)`. |
| `python -B -c "from app.main import app; ..."` | `backend` | PASS | App imports, 230 routes. |
| `git diff --check` | repo root | PASS | Whitespace clean; CRLF warnings only. |

## Commands skipped or blocked

- `python -B -m pytest -q --tb=short` full backend suite: not run; risk limited by targeted story tests, migration proof, rejected-boundary suite, and RG guardrail suites.
- Initial `pytest tests/integration -k "theme_natal and slot"` without `--long` was deselected by repository policy; rerun with `--long` passed.

## DRY / No Legacy evidence

- No compatibility shim, alias, fallback path, duplicate active public persistence, frontend cutover, provider change, prompt change, mass migration or legacy deletion was added.
- `UserNatalInterpretationModel` remains out-of-scope historical persistence.
- New public slot reads filter `status == "accepted"` and never infer public payload from `LlmGenerationRunModel`.
- Negative scans in `generated/06-validation-plan.md` passed.
- AST guard confirmed new/modified tests do not import `SessionLocal` or `engine` from `app.infra.db.session`.

## Diff review

- Scope reviewed with `git status --short`, `git diff --check`, targeted lint, tests and Alembic head check.
- `_condamad/run-state.json` remains a pre-existing unrelated dirty file.

## Final worktree status

```text
 M _condamad/run-state.json
 M _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/00-story.md
 M _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/11-code-review.md
 M _condamad/stories/story-status.md
 M backend/app/infra/db/models/__init__.py
 M backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/01-execution-brief.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/03-acceptance-traceability.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/04-target-files.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/05-implementation-plan.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/06-validation-plan.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/07-no-legacy-dry-guardrails.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/09-dev-log.md
?? _condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/10-final-evidence.md
?? backend/app/infra/db/models/llm_generation_run.py
?? backend/app/infra/db/models/theme_natal_reading_slot.py
?? backend/app/services/llm_generation/natal/theme_natal_reading_slots.py
?? backend/migrations/versions/20260601_0142_create_theme_natal_reading_slots.py
?? backend/tests/integration/test_theme_natal_reading_slots.py
```

## Remaining risks

- Full backend pytest was not run.
- New slot/run persistence is available behind service methods; public API cutover remains intentionally out of scope.

## Suggested reviewer focus

- Review transaction boundaries and the choice to keep `source_generation_run_id` as an integer pointer without circular FK.

## Feedback loop routing

- No reusable learning propagation required; encountered issues were local command usage and Windows SQLite cleanup handling, both recorded here.

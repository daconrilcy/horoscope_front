# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `remove-cross-test-module-imports`
- Source story: `_condamad/stories/remove-cross-test-module-imports/00-story.md`
- Capsule path: `_condamad/stories/remove-cross-test-module-imports`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Story source: `_condamad/stories/remove-cross-test-module-imports/00-story.md`
- Initial `git status --short`: `_condamad/stories/remove-cross-test-module-imports/` untracked; `_condamad/stories/replace-seed-validation-facade-test/` untracked; permission warnings under pytest artifact temp dirs.
- Pre-existing dirty files: `_condamad/stories/remove-cross-test-module-imports/` and `_condamad/stories/replace-seed-validation-facade-test/` were already untracked before code edits.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes
- Regression guardrails read: `_condamad/stories/regression-guardrails.md`

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable; status kept `ready-for-dev` because the story validator requires it. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC4 and all are PASS. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific No Legacy rules listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Replaced all 9 imports from executable test modules with imports from `billing_helpers.py`, `ops_alert_helpers.py`, `canonical_entitlement_alert_helpers.py`, and `regression/helpers.py`; persisted before/after scans. | Negative scan from `backend/` returned zero hit. | PASS | `cross-test-imports-before.md` had 9 hits; `cross-test-imports-after.md` has zero. |
| AC2 | Added non-executable helper owners and moved shared setup/builders out of `test_*.py` modules. | Helper inventory shows the new helper modules under `app/tests/integration`, `app/tests/unit`, and existing `app/tests/regression/helpers.py`. | PASS | No compatibility re-export from old test modules. |
| AC3 | Consumer tests keep their assertions and call the same setup through canonical helper owners. | Targeted billing, ops alert, engine regression/persistence, and entitlement alert handling tests all passed. Full `pytest -q` passed. | PASS | Initial full suite failure was only DB helper classification and was fixed. |
| AC4 | Added `app/tests/unit/test_backend_test_helper_imports.py` AST guard and registered `RG-013`. | `pytest -q app/tests/unit/test_backend_test_helper_imports.py` passed; full suite passed. | PASS | Guard fails on imports from `app.tests.*.test_` / `tests.*.test_`. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/remove-cross-test-module-imports/00-story.md` | modified | Mark implementation tasks complete while preserving validator-required status. | AC1-AC4 |
| `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-before.md` | added | Persist baseline 9-hit scan. | AC1 |
| `_condamad/stories/remove-cross-test-module-imports/cross-test-imports-after.md` | added | Persist zero-hit scan. | AC1 |
| `_condamad/stories/remove-cross-test-module-imports/generated/*.md` | added/modified | Capsule, traceability, plan, guardrails, final evidence. | AC1-AC4 |
| `_condamad/stories/regression-guardrails.md` | modified | Add durable invariant `RG-013` for no imports from executable test modules. | AC4 |
| `backend/app/tests/helpers/db_session.py` | unchanged dependency | Existing canonical DB helper reused by the new helper modules. | AC2, AC3 |
| `backend/app/tests/integration/billing_helpers.py` | added | Canonical owner for shared billing setup/access token helper. | AC1, AC2 |
| `backend/app/tests/integration/ops_alert_helpers.py` | added | Canonical owner for shared ops alert setup/builders. | AC1, AC2 |
| `backend/app/tests/unit/canonical_entitlement_alert_helpers.py` | added | Canonical owner for entitlement alert handling setup/builders. | AC1, AC2 |
| `backend/app/tests/unit/test_backend_test_helper_imports.py` | added | AST reintroduction guard for cross-test imports. | AC4 |
| Billing, ops alert, engine, and entitlement consumer tests | modified | Import and call helper owners directly. | AC1, AC3 |
| `backend/app/tests/regression/helpers.py` | modified | Owns shared `load_json` and `build_engine_input`. | AC1, AC2 |
| `backend/app/tests/unit/test_backend_db_test_harness.py` | modified | Classifies the new helper modules for allowed `create_all` usage while avoiding direct `SessionLocal`/`engine` imports. | AC3 |

## Files deleted

- None.

## Tests added or updated

- Added `backend/app/tests/unit/test_backend_test_helper_imports.py`.
- Updated consumer tests to use helper owners instead of executable test modules.
- Updated `backend/app/tests/unit/test_backend_db_test_harness.py` classification for the new helper files' `create_all` usage.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repo root | PASS | 0 | Initial and final dirty states captured; unrelated untracked `replace-seed-validation-facade-test/` left untouched. |
| `rg -n "from (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_|import (app\.tests\.(integration|unit|regression)|tests\.integration)\.test_" backend/app/tests backend/tests` | repo root | PASS | 0 | Baseline found 9 cross-test imports. |
| `ruff format .` | `backend/` | PASS | 0 | Reformatted changed Python files; rerun later reported 1241 unchanged. |
| `ruff check .` | `backend/` | FAIL | 1 | First run caught missing `date` import after moving builders. Fixed. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `pytest -q app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | PASS | 0 | 1 passed. |
| `pytest -q app/tests/unit/test_canonical_entitlement_alert_handling_service.py app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py` | `backend/` | PASS | 0 | 16 passed. |
| `pytest -q app/tests/integration/test_billing_api.py app/tests/integration/test_billing_api_61_65.py app/tests/integration/test_billing_api_61_66.py` | `backend/` | PASS | 0 | 15 passed. |
| `pytest -q app/tests/integration/test_engine_persistence_e2e.py app/tests/regression/test_engine_non_regression.py` | `backend/` | PASS | 0 | 40 passed. |
| `pytest -q app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_alert_batch_handle_api.py app/tests/integration/test_ops_alert_events_batch_retry_api.py app/tests/integration/test_ops_alert_events_list_api.py app/tests/integration/test_ops_alert_event_handle_api.py app/tests/integration/test_ops_alert_event_handling_history_api.py` | `backend/` | PASS | 0 | 84 passed. |
| `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py` | `backend/` | PASS | 1 | Zero hits; `rg` exit 1 means no matches. |
| `rg --files app/tests tests -g '*helpers*.py' -g conftest.py` | `backend/` | PASS | 0 | New helper modules are visible in non-test helper files. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-cross-test-module-imports\00-story.md` | `backend/` | PASS | 0 | Story validation passed after preserving `Status: ready-for-dev`. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-cross-test-module-imports\00-story.md` | `backend/` | PASS | 0 | Story lint passed after preserving `Status: ready-for-dev`. |
| `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | PASS | 0 | 3483 tests collected. |
| `pytest -q` | `backend/` | FAIL | 1 | First full run failed only on DB harness classification for the three new helper files. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | PASS | 0 | 5 passed after classifying new helpers. |
| `pytest -q` | `backend/` | PASS | 0 | 3471 passed, 12 skipped, 7 warnings in 558.61s. |
| `rg -n "billing_helpers.py\|ops_alert_helpers.py\|canonical_entitlement_alert_helpers.py" _condamad\stories\converge-db-test-fixtures\db-session-allowlist.md` | repo root | PASS | 1 | Zero hits; new helpers are not DB-session allowlist exceptions. |
| `rg -n "from app\.infra\.db\.session\|import app\.infra\.db\.session\|db_session_module\.SessionLocal\|SessionLocal" backend/app/tests/integration/billing_helpers.py backend/app/tests/integration/ops_alert_helpers.py backend/app/tests/unit/canonical_entitlement_alert_helpers.py` | repo root | PASS | 1 | Zero direct production session imports in new helpers. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | PASS | 0 | 5 passed after migrating new helpers to canonical DB helper. |
| `pytest -q app/tests/integration/test_billing_api.py app/tests/integration/test_billing_api_61_65.py app/tests/integration/test_billing_api_61_66.py` | `backend/` | PASS | 0 | 15 passed after canonical DB helper migration. |
| `pytest -q app/tests/unit/test_canonical_entitlement_alert_handling_service.py app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py` | `backend/` | PASS | 0 | 16 passed after canonical DB helper migration. |
| `pytest -q app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_alert_batch_handle_api.py app/tests/integration/test_ops_alert_events_batch_retry_api.py app/tests/integration/test_ops_alert_events_list_api.py app/tests/integration/test_ops_alert_event_handle_api.py app/tests/integration/test_ops_alert_event_handling_history_api.py` | `backend/` | PASS | 0 | 84 passed after canonical DB helper migration. |
| `pytest -q` | `backend/` | PASS | 0 | 3471 passed, 12 skipped, 7 warnings in 557.12s after risk correction. |
| `python -B -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | App imports locally; printed `horoscope-backend`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict issues; Git emitted CRLF normalization warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Diff summary reviewed. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | All planned checks were run. | None. | Not applicable. |

## DRY / No Legacy evidence

- No active import from `app.tests.integration.test_*`, `app.tests.unit.test_*`, `app.tests.regression.test_*`, or `tests.integration.test_*` remains under backend tests.
- No compatibility wrapper, alias, or re-export was added in the former owner tests.
- Shared helpers now have one owner per responsibility.
- `RG-013` records the durable no-cross-test-import invariant.
- Existing DB guard `RG-011` remains active; the new helper files use `app.tests.helpers.db_session` and are not DB-session allowlist exceptions.
- New helper files remain classified only for explicit `Base.metadata.create_all` schema reset behavior.

## Diff review

- `git diff --stat` reviewed: changed files are story-related test helpers, consumers, DB guard classification, guardrail registry, and story evidence.
- `git diff --check` passed with CRLF normalization warnings only.
- No production API/service/frontend files changed.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/tests/integration/test_billing_api.py
 M backend/app/tests/integration/test_billing_api_61_65.py
 M backend/app/tests/integration/test_billing_api_61_66.py
 M backend/app/tests/integration/test_engine_persistence_e2e.py
 M backend/app/tests/integration/test_ops_alert_batch_handle_api.py
 M backend/app/tests/integration/test_ops_alert_event_handle_api.py
 M backend/app/tests/integration/test_ops_alert_event_handling_history_api.py
 M backend/app/tests/integration/test_ops_alert_events_batch_retry_api.py
 M backend/app/tests/integration/test_ops_alert_events_list_api.py
 M backend/app/tests/integration/test_ops_review_queue_alerts_retry_api.py
 M backend/app/tests/regression/helpers.py
 M backend/app/tests/regression/test_engine_non_regression.py
 M backend/app/tests/unit/test_backend_db_test_harness.py
 M backend/app/tests/unit/test_canonical_entitlement_alert_handling_service.py
 M backend/app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py
?? _condamad/stories/remove-cross-test-module-imports/
?? _condamad/stories/replace-seed-validation-facade-test/
?? backend/app/tests/integration/billing_helpers.py
?? backend/app/tests/integration/ops_alert_helpers.py
?? backend/app/tests/unit/canonical_entitlement_alert_helpers.py
?? backend/app/tests/unit/test_backend_test_helper_imports.py
```

`git status --short` also emitted permission warnings for existing pytest artifact temp directories under `.codex-artifacts` and `artifacts`.

## Remaining risks

- None for the story scope. The full backend suite passes.

## Suggested reviewer focus

- Verify the four helper owners are the right long-term homes.
- Review `RG-013` and the AST guard for sufficient coverage of future cross-test imports.
- Review the `create_all` classification in `test_backend_db_test_harness.py`; no new DB-session allowlist exception remains.

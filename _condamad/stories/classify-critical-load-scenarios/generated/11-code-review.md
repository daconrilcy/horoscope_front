# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/classify-critical-load-scenarios/00-story.md`
- Status reviewed: `ready-for-review`
- Scope reviewed: `scripts/load-test-critical.ps1`, `backend/app/tests/unit/test_load_test_critical_script.py`, `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`, story evidence artifacts.

## Inputs reviewed

- Story capsule and generated evidence files.
- Shared guardrail registry `_condamad/stories/regression-guardrails.md`.
- Applicable invariant: `RG-015`, because a script/ops backend test was added.
- Git diff, untracked story artifacts, targeted tests, lint, scans, and PowerShell parser check.

## Diff summary

- `scripts/load-test-critical.ps1` now exposes a manifest with `smoke`, `llm`, `b2b`, `destructive-privacy`, and `stress-incidents` groups.
- Default `ScenarioGroups` are `smoke`, `llm`, and `b2b`; `privacy_delete_request` remains available only in `destructive-privacy`.
- `backend/app/tests/unit/test_load_test_critical_script.py` adds static guards for groups, default destructive exclusion, audited marker removal, and report generation.
- `ops-quality-test-ownership.md` registers the new script test for `RG-015`.
- Story baseline/after artifacts and CONDAMAD capsule files were persisted.

## Review layers

- Diff integrity: PASS. Changes are story-scoped; unrelated untracked story directories remain present but untouched.
- Acceptance audit: PASS for AC1-AC5.
- Validation audit: PASS with limitations. Required targeted validation passed; full `pytest -q` and live script execution were not rerun by the reviewer.
- DRY / No Legacy audit: PASS. Audited markers are absent and destructive privacy routing is explicitly guarded.
- Edge/security/data audit: PASS for the reviewed static scope. The destructive endpoint is no longer in the default group.
- Regression guardrail audit: PASS for `RG-015`; the new script test is registered.

## Findings

No actionable findings.

## Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | Manifest groups are declared in `scripts/load-test-critical.ps1`; targeted pytest verifies expected groups. |
| AC2 | PASS | Default groups exclude `destructive-privacy`; `privacy_delete_request` is only in the explicit destructive group. |
| AC3 | PASS | `rg -n "Story 66\\.35|Legacy critical scenarios" scripts/load-test-critical.ps1` returned zero hits. |
| AC4 | PASS | JSON write and Markdown report invocation remain present and are covered by the static test. |
| AC5 | PASS | Story validator and strict story lint passed. |

## Validation audit

Reviewer commands run:

| Command | Result |
|---|---|
| `pytest -q app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` from `backend` after `.\.venv\Scripts\Activate.ps1` | PASS, 7 tests passed |
| `ruff format --check app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` from `backend` after venv activation | PASS |
| `ruff check app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` from `backend` after venv activation | PASS |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\classify-critical-load-scenarios\00-story.md` after venv activation | PASS |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\classify-critical-load-scenarios\00-story.md` after venv activation | PASS |
| PowerShell parser check for `scripts/load-test-critical.ps1` | PASS |
| `git diff --check -- scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py _condamad/stories/classify-critical-load-scenarios` | PASS, line-ending warning only |
| Targeted forbidden marker and `privacy_delete_request` scans | PASS |

Skipped or not rerun:

- Full `pytest -q`: final evidence says it timed out after 304 seconds; reviewer did not rerun the full suite.
- Live execution of `scripts/load-test-critical.ps1`: not rerun because it requires a live backend and performs API/load actions.

## DRY / No Legacy audit

- No duplicate active scenario lists were introduced; the active execution path consumes the manifest.
- `Story 66.35` and `Legacy critical scenarios` are absent from the target script.
- `privacy_delete_request` appears only in the explicit destructive group and in the test assertions.
- No `legacy|compat|shim|fallback|deprecated|alias` hits were found in the changed script or new test.

## Commands run by reviewer

See validation audit. All Python commands were executed after activating `.\.venv\Scripts\Activate.ps1`.

## Residual risks

- Full backend regression is not proven locally by this review because the full suite was not rerun after the prior timeout.
- End-to-end runtime behavior of the load script is not proven without a live backend run.

## Verdict

`ACCEPTABLE_WITH_LIMITATIONS`

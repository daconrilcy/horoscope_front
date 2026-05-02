# Validation Plan

## Environment Assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend pytest commands run from `backend`.
- No new dependencies are allowed.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Scenario grouping guard | `pytest -q app/tests/unit/test_load_test_critical_script.py` | `backend` | yes | all tests pass |
| RG-015 ownership guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | ownership registry covers the new test |

## Unit Tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted unit tests | `pytest -q app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | all tests pass |

## Integration Tests

- Not applicable: this story changes script structure and static execution guards only; no backend API endpoint behavior changes.

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden marker scan | `rg -n "Story 66\\.35|Legacy critical scenarios" scripts/load-test-critical.ps1` | repo root | yes | no matches |
| Destructive scenario routing scan | `rg -n "privacy_delete_request" scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py` | repo root | yes | hits are limited to explicit destructive group and test guard |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy vocabulary scan | `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py` | repo root | yes | no active legacy/shim/fallback introduced |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format check | `ruff format --check app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | no formatting changes required |
| Ruff lint | `ruff check app/tests/unit/test_load_test_critical_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | no lint errors |

## Regression Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validator | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/classify-critical-load-scenarios/00-story.md` | repo root | yes | story validates |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/classify-critical-load-scenarios/00-story.md` | repo root | yes | story lint passes |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace errors or conflict markers |
| Worktree status | `git status --short` | repo root | yes | only expected dirty files plus pre-existing untracked story dirs |

## Commands That May Be Skipped Only With Justification

- Broad `pytest -q` may be skipped if targeted script/ownership tests and lint pass and the full suite is too expensive for this script-only change.

# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/` unless the command targets repository evidence files.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story guard catalogue | `pytest -q app/tests/unit/test_backend_story_guard_names.py` | `backend/` | yes | all tests pass |
| Migrated services guard lot | `pytest -q app/tests/unit/test_backend_services_llm_structure_guard.py app/tests/unit/test_backend_entitlement_structure_guard.py app/tests/unit/test_backend_services_structure_guard.py app/tests/unit/test_backend_story_guard_names.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story-number scan | `rg --files backend -g 'test_story_*.py'` | repo root | yes | no backend files appear |
| Story-number function scan | `rg -n "^\s*(async\s+)?def test_story_" backend -g 'test_*.py'` | repo root | yes | no backend test functions appear |
| Mapping evidence scan | `rg -n "test_story_|RG-" _condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md` | repo root | yes | mapping contains old story names and RG links as historical source rows |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy-heavy test terms | `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/tests backend/tests backend/app/domain -g 'test_*.py'` | repo root | yes | hits classified as guard terms, historical evidence, or out of scope |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Standard collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Full backend suite | `pytest -q` | `backend/` | yes | all tests pass |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| CONDAMAD capsule structure | `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/reclassify-story-regression-guards` | repo root | yes | validation passes |
| CONDAMAD final capsule | `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/reclassify-story-regression-guards --final` | repo root | yes | final validation passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files and target tests changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker errors |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

No required command is planned for skipping. If an environment limitation blocks a command, record the exact command, reason, risk, and compensating evidence in `10-final-evidence.md`.

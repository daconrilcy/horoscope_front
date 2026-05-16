# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| DB/model registry guard | `pytest -q app/tests/unit/test_db_model_registry_guard.py` | `backend/` | yes | all tests pass |
| Admin support integration | `pytest -q app/tests/integration/test_admin_support_api.py` | `backend/` | yes | all tests pass |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| New architecture guard | `pytest -q app/tests/unit/test_db_model_registry_guard.py` | `backend/` | yes | metadata, model files and exception register align |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Support route regression | `pytest -q app/tests/integration/test_admin_support_api.py` | `backend/` | yes | flagged content flow still works |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Destructive DB scan | `rg -n "drop_table\\(|DROP TABLE|_alembic_tmp_astrologer_profiles" app migrations ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra` | `backend/` | yes | only allowed story evidence hits for `_alembic_tmp_astrologer_profiles`; no destructive migration added |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Registry symbols scan | `rg -n "flagged_contents|FlaggedContentModel|llm_prompt_version_fallback_archives|SQLAlchemyJobStore|_alembic_tmp_astrologer_profiles|astrologer_prompt_profiles" app ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra -g "*.py" -g "*.md"` | `backend/` | yes | hits classified as model, consumer, scheduler, exception evidence or story evidence |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend/` | conditional | run if feasible; otherwise document limitation and targeted passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict marker errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped changes |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |

## Commands that may be skipped only with justification

- `pytest -q` may be skipped only if runtime is excessive after targeted checks pass; record risk.

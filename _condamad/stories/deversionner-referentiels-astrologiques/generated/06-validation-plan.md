# Validation Plan

## Environment assumptions

- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend package and tests run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Reference repository tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | repo root | yes | all pass |
| Migration/reference tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q` | repo root | yes | all pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Structural version scan | `rg -n "reference_version_id" backend/app/infra/db/models/reference.py backend/app/infra/db/models/prediction_reference.py backend/app/infra/db/repositories/reference_repository.py backend/app/infra/db/repositories/prediction_reference_repository.py backend/app/services/prediction/reference_seed_service.py` | repo root | yes | hits only on versioned/parametric tables or reference version root |
| Legacy terms scan | `rg -n "clone_version_data|reference_version_id.*PlanetModel|reference_version_id.*SignModel|reference_version_id.*HouseModel|reference_version_id.*AspectModel" backend/app backend/tests` | repo root | yes | no active structural-version hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | yes | no formatting errors |
| Lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |
| Regression suite | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | all pass or limitation documented |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-relevant files plus pre-existing dirty files |
| Worktree status | `git status --short` | repo root | yes | expected files only |

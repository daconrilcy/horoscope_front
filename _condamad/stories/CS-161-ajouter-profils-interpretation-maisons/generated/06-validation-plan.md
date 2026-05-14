# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for pytest/lint: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Model/schema tests | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py` | `backend` | yes | all tests pass |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Model contract | `pytest -q app/tests/unit/test_prediction_reference_repository.py` | `backend` | yes | model constraints pass |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Alembic schema | `pytest -q app/tests/integration/test_reference_data_migrations.py` | `backend` | yes | upgrade head contains expected table |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No astrology runtime consumption | `rg -n "house_interpretation_profiles|HouseInterpretationProfileModel" app/domain/astrology -g "*.py"` | `backend` | yes | zero hits |
| No generic characteristics return | `rg -n "AstroCharacteristicModel|astro_characteristics" app tests -g "*.py"` | `backend` | yes | only expected guard/historical hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff lint | `ruff check .` | `backend` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend` | conditional | pass or documented timeout limitation |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected files only plus pre-existing user file |

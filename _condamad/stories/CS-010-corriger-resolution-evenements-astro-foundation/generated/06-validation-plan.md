# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python checks: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Astro foundation unit tests | `pytest -q tests/unit/prediction/test_public_astro_foundation.py` | `backend` | yes | all tests pass |
| Public projection contract tests | `pytest -q app/tests/unit/test_public_projection.py` | `backend` | yes | all tests pass |
| API V4 integration regression | `pytest -q app/tests/integration/test_daily_prediction_api.py` | `backend` | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| RG-030 event source scan | `rg -n "aspect_exact_to_angle\|aspect_exact_to_luminary\|aspect_exact_to_personal\|detected_events" app/prediction` | `backend` | yes | hits show canonical event types and detected event resolution |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format touched files | `ruff format app/prediction/public_projection.py app/prediction/public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | `backend` | yes | files formatted |
| Lint touched files | `ruff check app/prediction/public_projection.py app/prediction/public_astro_daily_events.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py` | `backend` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend full regression | `pytest -q` | `backend` | conditional | all tests pass or unrelated pre-existing failures are documented |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace and conflict check | `git diff --check` | `backend` | yes | exit code 0 |
| Diff summary | `git diff --stat` | repository root | yes | only story-related owned changes plus pre-existing story registry changes |
| Final worktree status | `git status --short` | repository root | yes | expected files reported |

# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python validation: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Architecture guards | `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | all tests pass |
| Error contract tests | `pytest -q app/tests/unit/test_api_error_contracts.py` | `backend/` | yes | all tests pass |
| Error response integration tests | `pytest -q app/tests/integration/test_api_error_responses.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend startup/OpenAPI smoke | `python -c "from app.main import app; schema = app.openapi(); assert schema['paths']"` | `backend/` | yes | exits 0 |
| OpenAPI path snapshot | `python -c "from app.main import app; import json; print(json.dumps(sorted(app.openapi()['paths'].keys()), indent=2))"` | `backend/` | yes | emits path list |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| FastAPI-free schemas | `rg -n "from fastapi|import fastapi|APIRouter|JSONResponse|Depends|Request|Query|Body" app/api/v1/schemas` | `backend/` | yes | no active hits except classified false positives if any |
| Non-API layers do not import API schemas | `rg -n "from app\\.api\\.v1\\.schemas|import app\\.api\\.v1\\.schemas" app/services app/domain app/infra app/core` | `backend/` | yes | no active hits |
| Non-API layers do not import API dependencies/errors | `rg -n "from app\\.api\\.dependencies|from app\\.api\\.errors|import app\\.api" app/services app/domain app/infra app/core` | `backend/` | yes | no active hits |
| Legacy error surface scan | `rg -n "raise_http_error|legacy_detail|content\\[\"detail\"\\]" app/api app/tests` | `backend/` | yes | only classified historical/audit hits or none |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | exits 0 |
| Lint | `ruff check .` | `backend/` | yes | exits 0 |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend/` | conditional | all tests pass, or skipped with explicit environment/time risk |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | exits 0 |
| Final worktree | `git status --short` | repo root | yes | only expected changes |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.

# Validation Plan

## Environment assumptions

- Python commands run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| DB harness guard | `pytest -q app/tests/unit/test_backend_db_test_harness.py` | `backend/` | yes | all pass |
| App integration representative | `pytest -q app/tests/integration/test_reference_data_api.py` | `backend/` | yes | all pass |
| App unit representative | `pytest -q app/tests/unit/test_reference_data_service.py` | `backend/` | yes | all pass |
| SQLite alignment | `pytest -q tests/integration/test_backend_sqlite_alignment.py` | `backend/` | yes | all pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Direct import scan | `rg -n "from app\.infra\.db\.session import (SessionLocal|engine)" app/tests tests -g "*.py"` | `backend/` | yes | zero hits |
| Global redirection scan | `rg -n "db_session_module\.(SessionLocal|engine) =" app/tests/conftest.py` | `backend/` | yes | zero hits |
| Collection guard | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting failures |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend suite | `pytest -q` | `backend/` | yes | all pass |

## Rule for skipped commands

No planned command may be skipped without recording the exact reason, risk, and compensating evidence.

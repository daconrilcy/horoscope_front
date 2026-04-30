# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Backend commands run from `backend/` after `.\.venv\Scripts\Activate.ps1`.
- Python dependencies are managed by `backend/pyproject.toml`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Topology guard | `pytest -q app/tests/unit/test_backend_test_topology.py` | `backend/` | yes | all tests pass |
| RG-010 collection guard | `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | yes | all tests pass |

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend test inventory | `rg --files backend -g "test_*.py" -g "*_test.py" -g "!backend/.tmp-pytest/**"` | repo root | yes | only documented roots appear |
| Hidden app test roots | `rg --files backend/app -g "test_*.py" -g "*_test.py" -g "!backend/app/tests/**" -g "!backend/.tmp-pytest/**"` | repo root | yes | zero hits |
| No Legacy keyword classification | `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" _condamad/stories/guard-backend-pytest-test-roots backend/app/tests/unit/test_backend_test_topology.py backend/pyproject.toml` | repo root | yes | hits classified |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no unrelated formatting churn |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Standard pytest collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Backend suite | `pytest -q` | `backend/` | yes | all tests pass or unrelated flaky failure is classified with rerun evidence |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.

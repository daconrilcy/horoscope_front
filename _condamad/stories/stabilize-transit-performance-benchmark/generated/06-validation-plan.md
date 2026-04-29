# Validation Plan

## Environment Assumptions

- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.
- No dependency installation is expected.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |
| Standard targeted test | `pytest -q app/tests/unit/test_transit_performance.py` | `backend/` | yes | pass without env var |
| Strict opt-in benchmark | `$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py; Remove-Item Env:RUN_PERF_BENCHMARKS` | `backend/` | yes | pass with strict duration assertions active |
| No-op guard | `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend/` | yes | pass |
| Collect-only | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | pass |
| Budget scan | `rg -n "assert dur_.*< .*TARGET_BUDGET_MS" app/tests/unit/test_transit_performance.py` | `backend/` | yes | hits are only in the opt-in block |
| Budget constants | `rg -n "TARGET_BUDGET_MS = " app/prediction` | `backend/` | yes | transit remains `100.0`, activation remains `50.0` |
| Full regression | `pytest -q` | `backend/` | yes | pass, or classify unrelated failures |

## Skipped Command Rule

Any skipped command must be recorded with exact command, reason, risk, and compensating evidence.

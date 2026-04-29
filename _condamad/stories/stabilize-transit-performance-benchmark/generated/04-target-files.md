# Target Files

## Must Read

- `_condamad/stories/stabilize-transit-performance-benchmark/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md`
- `backend/app/tests/unit/test_transit_performance.py`
- `backend/app/prediction/transit_signal_builder.py`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/pyproject.toml`
- `AGENTS.md`

## Required Searches

- `rg -n "assert dur_.*< .*TARGET_BUDGET_MS|TARGET_BUDGET_MS = " backend\app\tests\unit\test_transit_performance.py backend\app\prediction`
- `rg -n "RUN_PERF_BENCHMARKS|perf_counter|TARGET_BUDGET_MS" backend\app\tests backend\tests`

## Likely Modified

- `backend/app/tests/unit/test_transit_performance.py`
- `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-before.md`
- `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-after.md`
- `_condamad/stories/stabilize-transit-performance-benchmark/generated/*.md`

## Forbidden Unless Story-Justified

- `backend/app/prediction/transit_signal_builder.py`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/pyproject.toml`
- `frontend/`
- `requirements.txt`

# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for backend checks: `backend/`.
- Dependencies are managed by `backend/pyproject.toml`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Anti cross-test import guard | `pytest -q app/tests/unit/test_backend_test_helper_imports.py` | `backend/` | yes | guard passes |
| Entitlement helper consumers | `pytest -q app/tests/unit/test_canonical_entitlement_alert_handling_service.py app/tests/unit/test_canonical_entitlement_alert_handling_service_events.py` | `backend/` | yes | tests pass |
| Billing consumers | `pytest -q app/tests/integration/test_billing_api.py app/tests/integration/test_billing_api_61_65.py app/tests/integration/test_billing_api_61_66.py` | `backend/` | yes | tests pass |
| Ops alert consumers | `pytest -q app/tests/integration/test_ops_review_queue_alerts_retry_api.py app/tests/integration/test_ops_alert_batch_handle_api.py app/tests/integration/test_ops_alert_events_batch_retry_api.py app/tests/integration/test_ops_alert_events_list_api.py app/tests/integration/test_ops_alert_event_handle_api.py app/tests/integration/test_ops_alert_event_handling_history_api.py` | `backend/` | yes | tests pass |
| Engine persistence consumer | `pytest -q app/tests/integration/test_engine_persistence_e2e.py app/tests/regression/test_engine_non_regression.py` | `backend/` | yes | tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Negative scan | `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py` | `backend/` | yes | zero hit |
| Helper owner inventory | `rg --files app/tests tests -g '*helpers*.py' -g conftest.py` | `backend/` | yes | extracted helpers visible in non-test modules |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no format errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Pytest collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Full backend tests | `pytest -q` | `backend/` | yes | tests pass or limitation documented |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no issues |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full `pytest -q` may be recorded as skipped only for an environmental/runtime limitation after targeted tests and collection pass.

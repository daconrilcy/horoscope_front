# Validation Plan

## Environment Assumptions

- Commands run on Windows PowerShell.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory is `backend`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ownership guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | guard passes |
| Concerned integration checks | `pytest -q app/tests/integration/test_pipeline_scripts.py app/tests/integration/test_secrets_scan_script.py app/tests/integration/test_security_verification_script.py` | `backend` | yes | tests pass |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Standard collection impact | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend` | yes | collection succeeds |
| RG-010 guards | `pytest -q app/tests/unit/test_backend_test_topology.py app/tests/unit/test_backend_pytest_collection.py` | `backend` | yes | guards pass |
| RG-014 guard | `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend` | yes | guard passes |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Inventory scan | `rg --files . -g "test_*.py" \| rg "(docs\|scripts\|ops\|secret\|security)"` | `backend` | yes | every hit has a registry row |
| Legacy scan | `rg -n "legacy\|compat\|shim\|fallback\|deprecated\|alias" backend _condamad/stories/classify-backend-ops-quality-tests -g "*.py" -g "*.md"` | repo root | yes | hits classified |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | no format drift after run |
| Lint | `ruff check .` | `backend` | yes | no lint errors |

## Regression Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression | `pytest -q` | `backend` | yes | full suite passes |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace/conflict issues |
| Final status | `git status --short` | repo root | yes | expected files only |

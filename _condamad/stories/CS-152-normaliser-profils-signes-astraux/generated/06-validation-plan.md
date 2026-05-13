# Validation Plan

## Environment Assumptions

- PowerShell on Windows.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend dependencies come from `backend/pyproject.toml`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Repository tests | `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q` | `backend` | yes | All tests pass. |
| Migration and seed tests | `pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q` | `backend` | yes | All tests pass. |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Sign rulership versioning removed | `rg -n "SignRulershipModel\\.reference_version_id|SignRulershipModel\\(reference_version_id" app tests` | `backend` | yes | No active runtime hit. |
| Old repository signature and tablename removed | `rg -n "get_sign_rulerships\\(reference_version_id\\)|__tablename__ = \"signs\"" app tests` | `backend` | yes | No active runtime hit. |
| Old rulership tablename removed | `rg -n "__tablename__ = \"sign_rulerships\"" app tests` | `backend` | yes | No active runtime hit. |
| Generic characteristics absent | `rg -n "AstroCharacteristicModel|astro_characteristics" app tests` | `backend` | yes | Only expected guard references, if any. |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | Exit 0. |
| Lint | `ruff check .` | `backend` | yes | Exit 0. |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff check | `git diff --check` | repo root | yes | No whitespace/conflict issues. |
| Scope check | `git diff --stat` | repo root | yes | Only story-related files changed. |

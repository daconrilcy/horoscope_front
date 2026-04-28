# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.
- No dependency change is expected.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| OpenAPI route presence | `python -B -c "from app.main import app; assert '/api/email/unsubscribe' in app.openapi()['paths']"` | `backend/` | yes | command exits 0 |
| Service ownership scan | `rg -n "email_unsubscribed=True\|update\\(UserModel\\)" app/services` | `backend/` | yes | hit in service layer only |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| API architecture guards | `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | all tests pass |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Public unsubscribe behavior | `pytest -q tests/integration/test_email_unsubscribe.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Exact SQL debt allowlist | `pytest -q app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist` | `backend/` | yes | test passes |
| Non-API layers do not import API | `pytest -q app/tests/unit/test_api_router_architecture.py::test_non_api_layers_do_not_import_api_package` | `backend/` | yes | test passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Route SQL/session negative scan | `rg -n "get_db_session\|Session\|UserModel\|sqlalchemy\|db\\." app/api/v1/routers/public/email.py` | `backend/` | yes | no hits |
| Public email allowlist removal | `rg -n "app/api/v1/routers/public/email.py" ..\_condamad\stories\harden-api-adapter-boundary-guards\router-sql-allowlist.md` | `backend/` | yes | no hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | command exits 0 |
| Lint | `ruff check .` | `backend/` | yes | command exits 0 |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend/` | yes | all tests pass or limitation documented |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | command exits 0 |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped only for environment/time failure after targeted tests and architecture guards pass.

# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python checks: `backend`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | yes | files formatted |
| Lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |
| Architecture guard | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app\tests\unit\test_api_router_architecture.py` | repo root | yes | all architecture tests pass |
| Extracted route behavior | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app\tests\integration\test_admin_content_api.py` | repo root | yes | admin content route tests pass |
| Full regression | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | suite passes or timeout is documented |
| SQL scan | `rg -n "from sqlalchemy|from app\.infra\.db\.models|from app\.infra\.db\.session|db\.(execute|commit|add|flush|refresh|query)" app\api\v1\routers app\api\dependencies` | `backend` | yes | hits match documented debt and allowlist |
| Generated client scan | `rg -n "operationId|openapi|generated client|client generated|api-client" ..\frontend ..\backend` | `backend` | yes | generated-client surfaces identified; no update required by empty OpenAPI diff |
| Legacy scan | `rg -n "legacy|compat|shim|fallback|deprecated|alias" app\api app\tests tests` | `backend` | yes | hits classified as pre-existing/out-of-scope or guard references |
| Diff check | `git diff --check` | repo root | yes | no whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected story changes only plus pre-existing dirty files |

## Skip handling

If the full regression command times out, record the timeout, risk, and compensating targeted checks in `10-final-evidence.md`.

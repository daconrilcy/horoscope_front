# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Python dependencies are managed by `backend/pyproject.toml`; no dependency change is allowed.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Architecture guards | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py` | repo root | yes | all tests pass |
| Transition guard | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/test_story_70_14_transition_guards.py` | repo root | yes | all tests pass |
| Admin LLM integration/OpenAPI | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_llm_config_api.py` | repo root | yes | all tests pass |
| Targeted combined suite | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py tests/unit/test_story_70_14_transition_guards.py app/tests/integration/test_admin_llm_config_api.py` | repo root | yes | all tests pass |

## Runtime contract checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runtime owner check | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -` with `app.routes` owner assertions | repo root | yes | four route keys owned by `app.api.v1.routers.admin.llm.observability` |
| Evidence files check | `.\.venv\Scripts\Activate.ps1; cd backend; python -B -` with `Path.exists()` assertions | repo root | yes | all persistent evidence files exist |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Removed handler scan | `rg -n '@router\.(get|post)\(\"/(call-logs|dashboard|replay|call-logs/purge)\"|def list_call_logs|def get_dashboard|def replay_request|def purge_logs|LlmCallLogListResponse|LlmDashboardResponse|ReplayPayload|purge_expired_logs|\breplay\b|_call_log_scope_filter|_legacy_removed_call_log_filter' backend\app\api\v1\routers\admin\llm\prompts.py` | repo root | yes | no hits |
| Observability SQL/import scan | `rg -n 'select\(|db\.query|Session|LlmCallLogModel|from app\.api\.v1\.routers\.admin\.llm\.prompts|sqlalchemy' backend\app\api\v1\routers\admin\llm\observability.py` | repo root | yes | no hits |
| Generated client scan | `rg -n 'operationId|openapi|generated client|client generated|api-client' frontend backend -S` | repo root | yes | no generated client found; hits are tests/OpenAPI references |

## Quality and regression

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | yes | formatting complete |
| Lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |
| Full regression | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | all tests pass |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict-marker errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-related tracked files changed |
| Worktree status | `git status --short` | repo root | yes | expected story changes listed |

# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/llm_observability/admin_observability.py`
- `backend/app/services/api_contracts/admin/llm/prompts.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/tests/unit/test_story_70_14_transition_guards.py`
- `backend/app/tests/integration/test_admin_llm_config_api.py`
- `_condamad/audits/api-adapter/2026-04-27-1906/*.md`

## Required searches

- `rg -n '@router\.(get|post)\(\"/(call-logs|dashboard|replay|call-logs/purge)\"|def list_call_logs|def get_dashboard|def replay_request|def purge_logs|LlmCallLogListResponse|LlmDashboardResponse|ReplayPayload|purge_expired_logs|\breplay\b|_call_log_scope_filter|_legacy_removed_call_log_filter' backend\app\api\v1\routers\admin\llm\prompts.py`
- `rg -n 'select\(|db\.query|Session|LlmCallLogModel|from app\.api\.v1\.routers\.admin\.llm\.prompts|sqlalchemy' backend\app\api\v1\routers\admin\llm\observability.py`
- `rg -n 'operationId|openapi|generated client|client generated|api-client' frontend backend -S`

## Modified files

- `backend/app/api/v1/routers/registry.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/tests/unit/test_story_70_14_transition_guards.py`
- `backend/app/tests/integration/test_admin_llm_config_api.py`
- `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`
- Story evidence files under `_condamad/stories/converge-admin-llm-observability-router/`

## Forbidden unless explicitly justified

- `backend/pyproject.toml`
- `backend/alembic/`
- `backend/app/infra/db/models/`
- `frontend/src/`

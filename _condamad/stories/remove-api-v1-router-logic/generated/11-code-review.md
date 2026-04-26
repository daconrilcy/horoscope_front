# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/remove-api-v1-router-logic/00-story.md`
- Capsule status reviewed: `ready-for-review`
- Worktree reviewed: implementation diff after remediation.

## Findings

- No blocking finding remains from the previous review pass.

## Resolved findings

### CR-1 High - HTTP/FastAPI response logic was moved into services

- Status: resolved
- Fix evidence:
  - `backend/app/api/v1/response_exports.py` now owns CSV `StreamingResponse` construction.
  - `backend/app/services/ops/admin_exports.py` now receives `request_id` and performs audit only.
  - `backend/app/services/llm_observability/admin_observability.py` no longer declares FastAPI `Request`/`Depends`; `backend/app/api/v1/routers/admin/llm/observability.py` owns route dependencies.
  - `backend/app/services/billing/public_billing.py` and `backend/app/services/ops/api_persona.py` now receive `request_id` instead of FastAPI `Request`.
  - `HTTPException` usages were removed from service modules touched by the migration and translated in route/API layers.

### CR-2 High - Architecture guard missed forbidden HTTP dependencies

- Status: resolved
- Fix evidence:
  - `backend/app/tests/unit/test_api_router_architecture.py` now checks all `backend/app/services/**` Python files and rejects imports from `fastapi` or `fastapi.*`, wildcard imports, and `APIRouter` definitions.

## Validation audit

Commands run after fixes:

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py` -> PASS, 40 passed.
- `rg -n "from fastapi|fastapi\.responses|JSONResponse|StreamingResponse|APIRouter|Depends\(" backend\app\services` -> no FastAPI hits; remaining broad `Request` strings are non-FastAPI domain/stdlib names only.
- `rg -n "app\.api\.v1\.router_logic|router_logic" backend\app backend\tests` -> no hits.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration/test_admin_llm_catalog.py app/tests/integration/test_b2b_usage_api.py app/tests/integration/test_ops_entitlement_mutation_audits_api.py app/tests/integration/test_llm_qa_router.py tests/unit/test_admin_manual_execute_response.py app/tests/unit/test_canonical_entitlement_alert_handling_service.py` -> PASS, 124 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_exports_api.py app/tests/integration/test_ops_persona_api.py app/tests/integration/test_billing_api.py app/tests/integration/test_daily_prediction_api.py app/tests/integration/test_admin_llm_canonical_consumption_api.py` -> PASS, 63 passed.
- `git diff --check` -> PASS, CRLF warnings only.

## Residual risks

- Full `pytest -q` was not rerun in this remediation pass.
- `backend/horoscope.db` remains modified in the worktree from the original dirty state and should not be committed with this story unless explicitly intended.

## Verdict

ACCEPTABLE_WITH_LIMITATIONS

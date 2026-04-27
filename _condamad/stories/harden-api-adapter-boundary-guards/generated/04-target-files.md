# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/00-audit-report.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/01-evidence-log.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/02-finding-register.md`
- `_condamad/audits/api-adapter/2026-04-27-1906/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/main.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/api/v1/routers/admin/content.py`
- `backend/app/api/v1/routers/admin/llm/prompts.py`
- `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`
- `backend/app/services/ops/admin_content.py`

## Required searches before editing

```powershell
rg -n "from sqlalchemy|from app\.infra\.db\.models|from app\.infra\.db\.session|db\.(execute|commit|add|flush|refresh|query)" backend\app\api\v1\routers backend\app\api\dependencies
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend\app\api backend\app\tests backend\tests
rg -n "operationId|openapi|generated client|client generated|api-client" frontend backend
```

## Modified files

- `backend/app/api/route_exceptions.py`
- `backend/app/main.py`
- `backend/app/api/v1/routers/admin/content.py`
- `backend/app/services/ops/admin_content.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `_condamad/stories/harden-api-adapter-boundary-guards/**`

## Forbidden or high-risk files

- `backend/pyproject.toml` - no dependency change allowed.
- `backend/alembic/**` - no migration expected.
- `frontend/**` - frontend is out of scope.
- `requirements.txt` - forbidden by repository instructions.

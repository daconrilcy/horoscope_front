# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `backend/app/main.py`
- `backend/app/api/errors/raising.py`
- `backend/app/api/errors/handlers.py`
- `backend/app/api/errors/__init__.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `backend/app/api/v1/schemas/routers/public/auth.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/reconciliation.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/entitlement_repair.py`
- `backend/app/api/v1/schemas/routers/ops/b2b/entitlements_audit.py`
- `backend/app/services/b2b/api_billing.py`
- `backend/app/services/consultation/precheck_service.py`
- `backend/app/services/llm_generation/admin_prompts.py`

## Required searches before editing

```powershell
rg -n "from fastapi|import fastapi|APIRouter|JSONResponse|Depends|Request|Query|Body" backend/app/api/v1/schemas
rg -n "from app\.api|import app\.api" backend/app/services backend/app/domain backend/app/infra backend/app/core
rg -n "raise_http_error|legacy_detail|content\[""detail""\]" backend/app backend/tests _condamad
rg -n "@router|^async def |^def " backend/app/api/v1/schemas
rg -n "include_router\(|from app\.api\.v1\.routers" backend/app/main.py backend/app/api/v1
```

## Likely modified files

- `backend/app/api/v1/schemas/routers/**/*.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/main.py`
- `backend/app/api/errors/raising.py`
- `backend/app/api/errors/handlers.py`
- `backend/app/api/errors/__init__.py`
- `backend/app/api/v1/routers/**/*.py` only for replacing legacy error helper imports/calls.
- `backend/app/services/**/*.py` only for replacing imports from `app.api`.
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md`

## Forbidden or high-risk files

- `frontend/**`: out of scope.
- `backend/pyproject.toml`: no dependency change expected.
- `backend/app/domain/astrology/**`: out of scope unless an import guard proves a direct API dependency.
- `backend/app/infra/db/**`: no DB behavior change expected.

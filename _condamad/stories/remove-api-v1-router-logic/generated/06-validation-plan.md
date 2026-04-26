# Validation Plan

## Environment assumptions

- Windows PowerShell.
- All Python commands run after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python validation: `backend/`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | yes | no formatting failure |
| Lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |
| Architecture guard | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_api_router_architecture.py` | repo root | yes | all tests pass |
| Targeted API/service tests | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q <story-targeted-tests>` | repo root | yes | all tests pass |
| Full backend suite | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | all tests pass |
| Filesystem absence | `cd backend; Test-Path app/api/v1/router_logic` | repo root | yes | `False` |
| Intermediate namespace absence | `cd backend; Test-Path app/api/v1/handlers` | repo root | yes | `False` |
| Removed namespace scan | `rg -n "app\.api\.v1\.handlers|api/v1/handlers|app\.api\.v1\.router_logic|router_logic" backend/app backend/tests backend/docs` | repo root | yes | no hits |
| Forbidden services scan | `cd backend; rg -n "services[\\/](router_logic|api_v1_router_logic)|app\.services\.(router_logic|api_v1_router_logic)" app tests` | repo root | yes | no hits |
| FastAPI leakage scan | `rg` scan for `from fastapi`, `fastapi.responses`, `JSONResponse`, `StreamingResponse`, `APIRouter`, and `Depends(` under `backend/app/services` | repo root | yes | no FastAPI hit in services |
| Local app import | `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; schema = app.openapi(); print(len(schema.get('paths', {})))"` | repo root | yes | OpenAPI builds |
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |

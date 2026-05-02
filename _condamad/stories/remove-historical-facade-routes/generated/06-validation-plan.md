# Validation Plan

## Environment assumptions

- Windows PowerShell.
- All Python commands run after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Historical audit validator evidence | `generated/10-final-evidence.md` | story capsule | yes | historical validation evidence remains recorded after one-off root validator removal |
| Router architecture guards | `pytest -q backend/app/tests/unit/test_api_router_architecture.py` | `backend/` after venv activation | yes | all tests pass |
| OpenAPI absence guard | `pytest -q backend/app/tests/integration/test_api_openapi_contract.py` | `backend/` after venv activation | yes | all tests pass |
| Chat canonical regression | `pytest -q backend/app/tests/integration/test_chat_api.py` | `backend/` after venv activation | yes | all tests pass |
| Admin export regression | `pytest -q backend/app/tests/integration/test_admin_exports_api.py` | `backend/` after venv activation | yes | all tests pass |
| Admin LLM config regression | `pytest -q backend/app/tests/integration/test_admin_llm_config_api.py` | `backend/` after venv activation | yes | all tests pass |
| Front routing guard | `npm run test -- --run src/tests/AdminPromptsRouting.test.tsx src/tests/AdminSettingsPage.test.tsx src/tests/adminPromptsApi.test.ts` | `frontend/` | yes | all tests pass |

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Removed backend route symbols | `rg -n "/v1/ai|ai_engine_router|app\.api\.v1\.routers\.public\.ai" frontend/src backend/app` | repo root | yes | no hits |
| Removed admin export compat field | `rg -n "use_case_compat" backend/app backend/tests frontend/src` | repo root | yes | no hits |
| Removed admin legacy states | `rg -n "legacy_maintenance|legacy_alias|legacy_registry_only" backend/app frontend/src` | repo root | yes | no hits |
| Removed frontend route | `rg -n "/admin/prompts/legacy" frontend/src` | repo root | yes | no hits |
| Repository route evidence | `rg -n "include_router|APIRouter" backend/app` | repo root | yes | classified in audit/final evidence |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Python format | `ruff format .` | `backend/` after venv activation | yes | no formatting errors |
| Python lint | `ruff check .` | `backend/` after venv activation | yes | no lint errors |
| Front lint/typecheck | `npm run lint` | `frontend/` | yes | no TypeScript errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression | `pytest -q` | `backend/` after venv activation | yes | all tests pass or documented limitation |
| Frontend regression | `npm run test -- --run` | `frontend/` | yes | all tests pass or documented limitation |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.

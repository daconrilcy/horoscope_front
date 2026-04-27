# Validation Plan

## Environment assumptions

- All Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`.
- Backend working directory for lint/tests: `backend`.

## Targeted checks

```bash
pytest -q app/tests/unit/test_api_error_contracts.py app/tests/unit/test_api_error_architecture.py app/tests/unit/test_api_router_architecture.py app/tests/integration/test_api_error_responses.py
```

## Architecture / negative scans

```bash
rg -n "from app\.api\.v1\.errors|app\.api\.v1\.errors" backend/app backend/tests
rg -n "def _error_response|def _create_error_response|api_error_response\(" backend/app/api/v1/routers backend/app/api/dependencies backend/app/services
rg -n "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services
Test-Path backend/app/api/v1/errors.py
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
pytest -q
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.

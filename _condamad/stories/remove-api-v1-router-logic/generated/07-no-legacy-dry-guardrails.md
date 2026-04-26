# No Legacy / DRY Guardrails

## Forbidden

- `backend/app/api/v1/router_logic`
- `backend/app/api/v1/handlers`
- `app.api.v1.router_logic`
- `app.api.v1.handlers`
- `backend/app/services/router_logic`
- `backend/app/services/api_v1_router_logic`
- Re-export, alias, compatibility loader, fallback, or `sys.modules` shim for the old package.

## Canonical Destinations

- Route declarations: `backend/app/api/v1/routers/**`.
- Pydantic contracts and HTTP error payloads: `backend/app/api/v1/schemas/**` and `backend/app/api/v1/errors.py`.
- Application logic formerly in `router_logic`: matching domain modules under `backend/app/services/**`.
- Cross-cutting core only when responsibility is genuinely platform-level.

## Required Evidence

- Filesystem absence of `backend/app/api/v1/router_logic`.
- Filesystem absence of `backend/app/api/v1/handlers`.
- `ModuleNotFoundError` for `app.api.v1.router_logic`.
- No backend app/test/doc references to `router_logic`, `api/v1/handlers` or `app.api.v1.handlers`.
- No service package named `router_logic` or `api_v1_router_logic`.
- Tests updated to patch the canonical service call site.
- No `fastapi` or `fastapi.*` imports under `backend/app/services/**`; HTTP response construction stays in route/API v1 modules.

## Classification

- `api/v1` may keep route registration, schemas, constants and API error helpers.
- Migrated service files may import API schemas only as the current DTO contract for these route use cases; they must not define routers, register routes, import FastAPI, or build FastAPI response objects.

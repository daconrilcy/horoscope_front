# No Legacy / DRY Guardrails

## Canonical owner

- HTTP adapter for admin LLM observability: `backend/app/api/v1/routers/admin/llm/observability.py`.
- Service/use-case owner: `backend/app/services/llm_observability/admin_observability.py`.
- Shared contracts: `backend/app/services/api_contracts/admin/llm/prompts.py`.

## Forbidden surfaces

- `@router.get("/call-logs")` in `prompts.py`.
- `@router.get("/dashboard")` in `prompts.py`.
- `@router.post("/replay")` in `prompts.py`.
- `@router.post("/call-logs/purge")` in `prompts.py`.
- Runtime owner for the four route keys different from `app.api.v1.routers.admin.llm.observability`.
- More or fewer than one `APIRoute` per expected method/path.
- Import from `app.api.v1.routers.admin.llm.prompts` inside `observability.py`.
- `select(`, `db.query`, `Session`, `LlmCallLogModel`, or `sqlalchemy` inside `observability.py`.

## Implemented guards

- `test_admin_llm_observability_routes_are_registered_once_from_canonical_router`.
- `test_admin_llm_prompts_does_not_redefine_observability_routes`.
- `test_admin_llm_observability_router_stays_service_delegating_adapter`.
- `test_admin_observability_router_exposes_only_observability_endpoints`.
- `test_admin_llm_observability_openapi_contract_exposes_all_routes`.

## Search classification

| Pattern | Result | Classification | Action | Status |
|---|---|---|---|---|
| Removed handler/decorator symbols in `prompts.py` | no hits | active legacy removed | none | PASS |
| SQL/import forbidden symbols in `observability.py` | no hits | active legacy absent | none | PASS |
| Generated client scan in `frontend backend` | hits only in backend OpenAPI tests | test guard expected hit | no client migration required | PASS |

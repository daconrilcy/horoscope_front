# Target Files

## Inspected

- `AGENTS.md`
- `backend/app/api/v1/router_logic/**`
- `backend/app/api/v1/routers/**`
- `backend/app/api/v1/errors.py`
- `backend/app/api/v1/constants.py`
- `backend/app/api/v1/schemas/**`
- `backend/app/services/**`
- `backend/app/core/**`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/integration/**`
- `backend/tests/integration/test_admin_llm_catalog.py`
- `backend/tests/unit/test_admin_manual_execute_response.py`
- `backend/docs/llm-db-cleanup-registry.json`
- `_condamad/stories/converge-api-v1-route-architecture/service-boundary-audit.md`

## Modified

- `backend/app/services/**` new domain modules added for migrated application logic.
- `backend/app/api/v1/router_logic/**` deleted.
- `backend/app/api/v1/routers/**` imports migrated to services.
- `backend/app/api/v1/schemas/routers/**` cleaned by Ruff after stale non-schema imports were removed.
- `backend/app/tests/**` and `backend/tests/**` monkeypatch/import paths migrated to services.
- `backend/app/tests/unit/test_api_router_architecture.py` guard inverted and extended.
- `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` updated for service module placement.
- `backend/docs/llm-db-cleanup-registry.json` allowlist paths migrated.
- `_condamad/stories/remove-api-v1-router-logic/**` evidence generated.

## Forbidden Unless New Story

- New dependencies.
- URL or route registration changes.
- `backend/app/api/v1/handlers`.
- `backend/app/services/router_logic`.
- `backend/app/services/api_v1_router_logic`.
- Compatibility aliases or re-export modules for `app.api.v1.router_logic`.

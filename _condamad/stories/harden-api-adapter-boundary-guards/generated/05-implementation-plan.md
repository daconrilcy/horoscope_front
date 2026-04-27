# Implementation Plan

## Current findings

- Runtime route exceptions were mounted in `main.py` without a reusable structured register.
- `test_api_router_architecture.py` had route ownership guards but no general SQL/session/model AST guard.
- `admin/content.py` already delegates some business helpers to `services.ops.admin_content`, making `PATCH /texts/{key}` a bounded extraction candidate.

## Selected approach

1. Add one exception register under `backend/app/api/route_exceptions.py`.
2. Make `main.py` call the canonical v1 registry and the exception register only.
3. Move the config-text update persistence flow to `services.ops.admin_content.update_config_text_value`.
4. Extend `test_api_router_architecture.py` with:
   - runtime exception-register tests;
   - main AST guard;
   - SQL debt allowlist parser and AST scanner;
   - extracted-flow guard.
5. Persist before/after route, SQL and OpenAPI evidence in the story folder.

## No Legacy stance

- No compatibility wrapper, alias or fallback was added.
- The route exception register is not a second API v1 registry; it only owns exact non-canonical runtime exceptions.
- Existing SQL debt remains allowlisted exactly and cannot grow silently.

## Rollback strategy

- Revert the new exception register and restore direct route includes only if the architecture guard is intentionally removed.
- Revert `update_config_text_value` extraction by moving the code back into the router only if AC5 is explicitly abandoned.

# Implementation Plan

## Initial repository findings

- `prompts.py` owned the four runtime observability routes before implementation.
- `observability.py` already declared the intended specialized router and delegated to `app.services.llm_observability.admin_observability`.
- `registry.py` did not register the observability router.
- Existing guards covered router architecture but not the runtime owner/cardinality invariant for these four routes.

## Changes made

- Register `admin_llm_observability_router` in `API_V1_ROUTER_REGISTRY`.
- Delete only the duplicated observability handlers and dead imports from `prompts.py`.
- Keep `observability.py` as the HTTP adapter and remove its direct `Session` annotation/import.
- Add AST/runtime architecture guards for owner, cardinality, forbidden decorators, and forbidden SQL/import symbols.
- Add OpenAPI integration coverage for the four observability paths.
- Persist route owner and OpenAPI before/after evidence plus removal audit.

## Rollback strategy

- Revert the registry registration, handler deletion, tests, and evidence files together.
- Do not restore compatibility wrappers; rollback would restore the previous exact implementation state only if this story is rejected.

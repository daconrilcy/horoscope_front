# Implementation Plan

## Initial Repository Findings

- `backend/app/api/v1/routers` mixed flat modules and partial domain packages.
- `admin/llm/*` existed but several files were wrappers around flat `admin_llm*` modules.
- `backend/app/main.py` still imported many routers from flat module paths.
- Tests patched or imported router internals through flat paths.
- Pydantic schemas are still widely declared inside routers; full extraction is larger than the safe namespace move completed here.

## Implemented Changes

- Move active router modules into domain packages: `admin`, `admin/llm`, `b2b`, `ops`, `public`, plus existing `internal/llm`.
- Replace `backend/app/api/v1/routers/__init__.py` re-exports with a package marker.
- Update backend imports/tests from flat module paths to canonical domain paths.
- Add architecture guards for domain classification, root package re-exports, and legacy flat import removal.
- Add a minimal OpenAPI contract test for representative preserved endpoints.

## Remaining Work

- Extract router-local `BaseModel` classes into domain schema modules.
- Move non-HTTP helper/business logic out of large routers into existing `services`, `infra`, or `domain` modules.
- Add a deeper route-thinness architecture guard after logic extraction.

## Rollback Strategy

- Revert the router file moves and import rewrites as one changeset if import or OpenAPI regressions appear.
- Keep the architecture tests as the reference for intended canonical paths.

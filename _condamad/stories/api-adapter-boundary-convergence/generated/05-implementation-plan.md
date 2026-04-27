# Implementation Plan

## Initial repository findings

- Capsule was incomplete; required generated files were created before implementation.
- `git status --short` initially showed only the untracked story capsule directory.
- `backend/app/api/v1/schemas` contains many FastAPI imports and `router = APIRouter(...)` assignments, but no route handlers.
- `backend/app/main.py` manually imports and includes API v1 routers.
- Non-API services import `app.api.dependencies`, `app.api.v1.constants`, and `app.api.v1.schemas`.
- `raise_http_error`, `legacy_detail`, and top-level `detail` compatibility are active in API error helpers and several routers.

## Proposed changes

- Add a canonical router registry and make `main.py` consume it.
- Add architecture guards before/with convergence for FastAPI-free schemas, non-API import boundaries, router registry, legacy errors, and non-v1 exceptions.
- Remove FastAPI-only imports and router objects from schema modules.
- Replace legacy error helper calls with `raise_api_error` and remove the compatibility field path if tests confirm no external blocker.
- Move/repoint shared constants/contracts only where required to eliminate non-API imports from `app.api`.
- Document classifications and OpenAPI evidence in `removal-audit.md`.

## Files to modify

- `backend/app/api/v1/routers/registry.py`
- `backend/app/main.py`
- `backend/app/api/v1/schemas/routers/**/*.py`
- `backend/app/api/errors/raising.py`
- `backend/app/api/errors/handlers.py`
- `backend/app/api/errors/__init__.py`
- Selected `backend/app/api/v1/routers/**/*.py` files that call `raise_http_error`.
- Selected `backend/app/services/**/*.py` files importing `app.api`.
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `_condamad/stories/api-adapter-boundary-convergence/removal-audit.md`

## Files to delete

- None planned initially. Delete only classified `dead` files if discovered.

## Tests to add or update

- Extend `backend/app/tests/unit/test_api_router_architecture.py`.
- Update `backend/app/tests/unit/test_api_error_contracts.py`.
- Run targeted integration error response tests if present.

## Risk assessment

- Moving all service-facing DTO imports may be broad; keep changes mechanical and owner-specific.
- Removing top-level `detail` may change external error payloads; classify before deleting.
- Router registry may accidentally omit routes; OpenAPI snapshot and architecture tests must catch this.
- `/api/email/unsubscribe` must remain unless explicitly approved for deletion.

## Rollback strategy

- Revert this story's changed files only; the generated capsule and audit identify the intended file set.
- If validation finds an unsafe external error payload dependency, keep the canonical implementation blocked and record `BLOCKED` rather than introducing a shim.

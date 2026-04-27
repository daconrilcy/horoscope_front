# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior
- `router = APIRouter(...)` under `backend/app/api/v1/schemas`
- `from fastapi` or `from fastapi.responses` under `backend/app/api/v1/schemas`
- `from app.api` or `import app.api` from `services`, `domain`, `infra`, or `core`
- `raise_http_error`
- `legacy_detail`
- `content["detail"]` in canonical API error handling
- API v1 router registration duplicated manually in `backend/app/main.py`
- Any FastAPI route outside `/v1` without an explicit `NON_V1_ROUTE_EXCEPTIONS` entry

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Story-specific canonical owners

- HTTP routers and dependencies: `backend/app/api/**`
- API v1 router inventory: `backend/app/api/v1/routers/registry.py`
- API error envelope: `backend/app/api/errors/contracts.py` and `backend/app/api/errors/handlers.py`
- Shared service contracts: nearest non-API owner under `backend/app/services`, `backend/app/domain`, or `backend/app/infra`
- Historical email unsubscribe route: keep `/api/email/unsubscribe` classified as `external-active` unless explicit user decision approves deletion.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?

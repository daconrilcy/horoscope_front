# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Story-specific forbidden symbols

- `backend/app/api/v1/routers/public/ai.py`
- `backend/app/api/v1/router_logic/public/ai.py`
- `backend/app/api/v1/schemas/ai.py`
- `app.api.v1.routers.public.ai`
- `ai_engine_router`
- `APIRouter(prefix="/v1/ai")`
- `/v1/ai`
- `/admin/prompts/legacy`
- `use_case_compat`
- `legacy_maintenance`
- `legacy_alias`
- `legacy_registry_only`

## Canonical owners

- Public chat LLM API: `/v1/chat/*`.
- Public guidance LLM API: `/v1/guidance/*`.
- Admin LLM catalog/release history: `/v1/admin/llm/*`.
- Admin export dimensions: `feature`, `subfeature`, `subscription_plan`, `taxonomy_scope`.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?

# No Legacy / DRY Guardrails

## Canonical responsibilities

- API v1 router registration: `backend/app/api/v1/routers/registry.py`.
- Exact runtime exceptions outside canonical v1 registry: `backend/app/api/route_exceptions.py`.
- Persistence orchestration: `backend/app/services/**` or `backend/app/infra/**`.
- HTTP request/response adaptation: `backend/app/api/**`.

## Forbidden for this story

- Direct `app.include_router(...)` of API v1 exception routers in `main.py`.
- Wildcard SQL allowlist rows.
- Missing reason or decision on SQL debt rows.
- New SQLAlchemy/model/session usage in routers or API dependencies outside exact allowlist.
- Reintroduction of admin LLM observability handlers in `prompts.py`.
- Compatibility wrappers, aliases, re-exports or fallback mounting.

## Required evidence

- `route-exception-register.md`
- `router-sql-allowlist.md`
- `router-sql-inventory-before.md`
- `router-sql-inventory-after.md`
- `openapi-before.json`
- `openapi-after.json`
- `openapi-contract-diff.md`
- `pytest -q app\tests\unit\test_api_router_architecture.py`

## Search classification

- SQL scan hits are expected existing debt and are now governed by `router-sql-allowlist.md`.
- Generic legacy/fallback hits are broad pre-existing test/domain terminology outside this story, except architecture-test guard strings.
- No new compatibility wrapper or fallback was added by this story.

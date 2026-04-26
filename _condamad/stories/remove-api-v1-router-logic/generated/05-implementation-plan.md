# Implementation Plan

## Findings

- `router_logic` contained 54 Python files consumed by routeurs API v1 and first-party tests.
- No external usage evidence was found.
- The previous intermediate `api/v1/handlers` destination was rejected because it still kept non-route logic under `api/v1`.
- Existing service domains cover the migrated responsibilities: `llm_generation`, `llm_observability`, `ops`, `b2b`, `billing`, `canonical_entitlement`, `user_profile`, `prediction`, `consultation`, `email`, `entitlement`, `chart`, `natal`, `auth`, `geocoding`, `privacy`, and `reference_data`.

## Approach

1. Move each former `router_logic` module to its domain service destination under `backend/app/services/**`.
2. Delete `backend/app/api/v1/router_logic/**` and ensure `backend/app/api/v1/handlers/**` does not exist.
3. Replace production imports and test monkeypatch strings from `app.api.v1.router_logic` / `app.api.v1.handlers` to `app.services.*`.
4. Keep API-specific schemas and `ErrorEnvelope` imports under `backend/app/api/v1/schemas/**` and `backend/app/api/v1/errors.py`.
5. Update architecture tests to assert directory absence, negative import, no backend references, and service module guardrails.
6. Update LLM DB cleanup allowlists that referenced old files.
7. Run format, lint, targeted tests, scans, full backend suite and OpenAPI import check.

## Rollback

Revert the import and file-placement patch as one change if route registration or API integration breaks. No DB migration or dependency change is involved.

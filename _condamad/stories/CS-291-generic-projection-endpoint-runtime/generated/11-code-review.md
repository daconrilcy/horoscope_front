# CS-291 Implementation Review

Date: 2026-05-25
Verdict: CLEAN

## Scope Reviewed

- Story: `_condamad/stories/CS-291-generic-projection-endpoint-runtime/00-story.md`
- Source brief: `_story_briefs/cs-291-implement-generic-projection-endpoint.md`
- Tracker row: `_condamad/stories/story-status.md`
- Runtime files: projection route, public schemas, endpoint service, router registry and projection tests.
- Guardrails: router root audit, SQL boundary allowlist, API error architecture, OpenAPI public/internal boundary.

## Review Cycle

- Iteration 1: found implementation and guardrail failures from full `pytest -q`.
- Fixes applied:
  - moved HTTP status mapping out of `ProjectionEndpointService` and into the API router;
  - updated stale builder and versioning guard tests to allow the new canonical generic endpoint;
  - isolated FastAPI dependency overrides in CS-291 API tests;
  - added `app.api.v1.routers.public.projections` to router root audit evidence;
  - documented the exact CS-291 DB dependency boundary rows in the SQL router allowlist.
- Iteration 2: fresh review found no actionable implementation issue.

## Alignment Result

- `POST /v1/astrology/projections` is registered in loaded routes and OpenAPI.
- `chart_id` and `birth_input` source selection remains service-owned and tested.
- Internal projection identifiers are denied by the service and absent from the CS-291 OpenAPI operation.
- Public builders remain the only dispatch targets: `structured_facts_v1`, `beginner_summary_v1`, `client_interpretation_projection_v1`.
- Entitlement plan source is resolved server-side; client-supplied plan fields are rejected.
- `persist=true` delegates to `ProjectionPersistenceService.persist_from_builder`.
- No frontend, B2B route, admin projection route, migration, provider or generated client was added by CS-291.

## Validation

- `ruff check .`: PASS.
- `pytest -q`: PASS, 3378 passed, 1 skipped, 1211 deselected.
- Targeted CS-291 and projection guard tests: PASS, 57 passed.
- API architecture guard subset: PASS, 3 passed.
- Runtime OpenAPI assertion for `/v1/astrology/projections`: PASS.
- Runtime route assertion for `/v1/astrology/projections`: PASS.
- Forbidden alternate route scan: PASS, no matches.
- Uvicorn startup check on `127.0.0.1:8012` and `/openapi.json`: PASS.
- `condamad_validate.py _condamad\stories\CS-291-generic-projection-endpoint-runtime`: PASS.
- `condamad_story_validate.py _condamad\stories\CS-291-generic-projection-endpoint-runtime\00-story.md`: PASS.
- `condamad_story_lint.py --strict _condamad\stories\CS-291-generic-projection-endpoint-runtime\00-story.md`: PASS.

## Propagation

- no-propagation: fixes are local to CS-291 implementation and its directly impacted guardrail evidence.

## Residual Risk

- No residual CS-291 implementation risk identified.

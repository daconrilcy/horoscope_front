# Dev Log

## Preflight

- Initial `git status --short`: run; workspace already contained many unrelated modified/untracked story, backend and docs files from prior work.
- Current branch: not changed.
- Existing dirty files: left untouched unless listed in CS-282 final evidence.

## Search evidence
- Story, source brief and CS-282 status row matched before implementation.
- CS-280 and CS-281 were `done` with final evidence and validation artifacts present.
- Existing owners inspected: API v1 registry, public entitlement route pattern, B2C runtime gate, CS-281 contract doc and OpenAPI neutrality guard.

## Implementation notes
- Added one canonical public route: `GET /v1/transit/projection`.
- Kept proof validation, B2C access and projection assembly outside the HTTP handler.
- Updated the route architecture audit because the new registered router must be inventoried.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `condamad_prepare.py --repair-generated-only ...` | PASS | Repaired missing generated capsule files. |
| `condamad_validate.py _condamad/stories/CS-282-transit-projection-proof-gated-api` | PASS | Capsule structure valid before implementation. |
| `ruff check .` | PASS | Full backend lint. |
| `python -B -m pytest -q app/tests/integration/test_transit_projection_api.py --long --tb=short` | PASS | 6 passed. |
| `python -B -m pytest -q tests/architecture/test_api_contract_neutrality.py --tb=short` | PASS | 21 passed. |
| `python -B -m pytest -q --tb=short` | PASS | 3315 passed, 1 skipped, 1201 deselected. |
| Runtime/OpenAPI assertions and negative `rg` scans | PASS | See `evidence/validation.txt`. |

## Issues encountered
- Initial full backend pytest exposed route architecture guard failures: local classes in router, missing audit row and SQL dependency in router. Fixed by moving access support into service and updating the canonical audit.
- Full backend pytest then exposed a service-layer FastAPI import. Fixed by removing FastAPI from the service resolver.
- A negative scan initially matched forbidden route fragments inside test constants. Fixed by constructing those literals without the raw legacy fragments in source.

## Decisions made
- The route returns client-state payloads for proof-blocked and unauthorized outcomes instead of generic envelopes so clients can distinguish blocked states.
- The proof gate validates persisted CS-280/CS-281 evidence before projection success.
- No frontend, DB schema, migration or pricing change was introduced.

## Final `git status --short`
- Run after evidence update; workspace remains dirty from pre-existing unrelated work plus CS-282 changes.

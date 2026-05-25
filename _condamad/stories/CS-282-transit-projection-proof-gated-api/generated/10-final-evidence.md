# Final Evidence — CS-282-transit-projection-proof-gated-api

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-282-transit-projection-proof-gated-api
- Source story: `_condamad/stories/CS-282-transit-projection-proof-gated-api/00-story.md`
- Capsule path: `_condamad/stories/CS-282-transit-projection-proof-gated-api`
- Story registry: CS-282 set to `done` with last update `2026-05-25`.

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Source brief: `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md`; read and not modified.
- Status row: path and source brief matched CS-282 before implementation.
- Pre-existing dirty files: many unrelated story/review/backend/doc files were already dirty; CS-282 work stayed scoped.
- Capsule: missing generated files repaired, then `condamad_validate.py` passed.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status set to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Capsule repaired before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC evidence updated. |
| `generated/04-target-files.md` | yes | yes | PASS | Present from capsule repair. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present from capsule repair. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present from capsule repair. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Single route in `public/transit_projection.py` and canonical registry. | Runtime route count assertion; integration test. | PASS |
| AC2 | OpenAPI exposes `/v1/transit/projection` and `transit_client_projection_v1`. | `openapi-after.json`; OpenAPI assertion; architecture tests. | PASS |
| AC3 | Proof gate validates dependency evidence before success. | Missing-proof integration test returns `409`/`proof_blocked`. | PASS |
| AC4 | Projection service returns only client content, facts, proof refs and hash. | Client-safe payload test; negative scans. | PASS |
| AC5 | Raw runtime/debug/fixed-star route fragments stay absent. | OpenAPI assertions and `rg` scans in `evidence/validation.txt`. | PASS |
| AC6 | B2C plan depth uses existing entitlement gate and cumulative plan sections. | Free/basic/premium integration test. | PASS |
| AC7 | Degraded, unavailable, unauthorized and proof-blocked states are explicit. | Degraded, unavailable, unauthorized and proof-blocked integration tests. | PASS |
| AC8 | CS-280 and CS-281 final/validation evidence required. | Dependency proof before/after and path assertions. | PASS |
| AC9 | Public exposure guards cover the canonical transit route and forbidden fragments. | `test_api_contract_neutrality.py` -> 21 passed. | PASS |
| AC10 | Required story artifacts persisted. | Evidence directory and capsule validation. | PASS |

## Files changed

- `backend/app/api/v1/routers/public/transit_projection.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/api_contracts/public/transit_projection.py`
- `backend/app/services/transit_projection/__init__.py`
- `backend/app/services/transit_projection/access_gate.py`
- `backend/app/services/transit_projection/client_projection.py`
- `backend/app/services/transit_projection/proof_gate.py`
- `backend/app/tests/integration/test_transit_projection_api.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`
- `_condamad/stories/CS-282-transit-projection-proof-gated-api/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added `backend/app/tests/integration/test_transit_projection_api.py`.
- Updated `backend/tests/architecture/test_api_contract_neutrality.py`.

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `ruff format <CS-282 python files>` | PASS | 8 files left unchanged on final run. |
| `ruff check .` | PASS | Full backend lint. |
| `python -B -m pytest -q app/tests/integration/test_transit_projection_api.py --long --tb=short` | PASS | 9 passed. |
| `python -B -m pytest -q tests/architecture/test_api_contract_neutrality.py --tb=short` | PASS | 21 passed. |
| `python -B -m pytest -q app/tests/unit/test_api_router_architecture.py::... --tb=short` | PASS | 4 passed. |
| `python -B -m pytest -q --tb=short` | PASS | 3315 passed, 1 skipped, 1204 deselected. |
| Runtime/OpenAPI Python assertions | PASS | Route count, OpenAPI exposure and raw runtime absence. |
| Negative `rg` scans | PASS | No forbidden raw runtime tokens in API/contracts; no forbidden public transit route fragments in app/tests. |

## Commands skipped or blocked

- Frontend validation skipped: story explicitly excludes frontend and no `frontend/**` file changed.

## DRY / No Legacy evidence

- One canonical public route: `/v1/transit/projection`.
- No legacy `/transit/raw`, `/transits/raw`, `/transit_chart_v1`, `/transit-debug` or `/fixed-stars/transits` route.
- B2C plan enforcement delegates to existing `resolve_b2c_access`.
- Proof validation and projection assembly live in services, not route-local dict/business logic.
- Unreadable proof evidence returns explicit `503`/`unavailable` instead of falling through to an unhandled server error.
- OpenAPI excludes `TransitChartRuntime`, `transit_chart_v1`, `execution_trace` and `debug_payload`.

## Diff review

- `git diff --stat -- <CS-282 paths>`: run; tracked diffs are scoped, while new CS-282 files are untracked until commit.
- `git diff --check -- <CS-282 paths>`: PASS with line-ending warnings only.

## Final worktree status

- Worktree remains dirty from pre-existing unrelated work plus CS-282 changes.
- No destructive git command, branch creation or commit was run.

## Remaining risks

- Runtime B2C access depends on the existing entitlement catalog containing `transit_client_projection`; tests mock the resolver to cover route behavior without changing entitlement data.

## Suggested reviewer focus

- Verify the selected public route name `/v1/transit/projection` and the entitlement feature code `transit_client_projection` match product/catalog naming expectations.

## Feedback loop

- no-propagation: fixes were local CS-282 implementation and architecture guard compliance; no reusable skill or global guardrail correction identified.

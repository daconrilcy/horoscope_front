# CS-282 Implementation Review: transit-projection-proof-gated-api

Verdict: CLEAN

## Review Scope

- Story reviewed: `_condamad/stories/CS-282-transit-projection-proof-gated-api/00-story.md`.
- Source brief: `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md`.
- Tracker row: `_condamad/stories/story-status.md`, source-matched CS-282 row.
- Implementation reviewed: public route, registry wiring, response contract, proof gate, B2C access gate, projection service, tests,
  OpenAPI guard and CS-282 evidence.

## Iterations

- Iteration 1: CHANGES_REQUESTED.
  - Finding: `transit_client_projection` was used by the runtime B2C gate but was absent from `FEATURE_SCOPE_REGISTRY` and from the
    canonical product entitlement seed, so real users could not receive the plan-scoped route behavior proven by mocked tests.
  - Fix: registered the feature as B2C, added seed feature/bindings for free, trial, basic and premium, extended the registry
    consistency validator and updated seed/API tests.
- Iteration 2: CHANGES_REQUESTED.
  - Finding: the proof gate accepted CS-280/CS-281 evidence files by path existence only, without checking PASS markers.
  - Fix: proof validation now rejects present-but-invalid dependency evidence and an integration test covers the invalid proof case.
- Iteration 3: CHANGES_REQUESTED.
  - Finding: the route contract listed `503`/`unavailable`, but no production path returned that client state when proof evidence was
    present but unreadable.
  - Fix: proof evidence read failures now raise a typed proof-gate unavailable error, the route returns `503` with `unavailable`, and
    the integration test covers this state.
- Iteration 4: CLEAN.

## Acceptance Criteria Review

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | `/v1/transit/projection` is registered once through `backend/app/api/v1/routers/registry.py`. |
| AC2 | PASS | OpenAPI exposes the controlled route and `transit_client_projection_v1`. |
| AC3 | PASS | Missing and invalid proof evidence produce blocked behavior before projection success. |
| AC4 | PASS | Response contract and integration tests expose only client-safe projection fields. |
| AC5 | PASS | OpenAPI assertions and architecture tests keep raw runtime/debug tokens absent. |
| AC6 | PASS | B2C plan depth is enforced and the runtime feature code is registered in the canonical B2C registry/seed. |
| AC7 | PASS | `available`, `degraded`, `unavailable`, `unauthorized` and `proof_blocked` states are modeled and tested. |
| AC8 | PASS | CS-280 and CS-281 proof files are required and checked for PASS evidence. |
| AC9 | PASS | `test_api_contract_neutrality.py` covers transit public exposure guards. |
| AC10 | PASS | CS-282 evidence and review artifacts are persisted. |

## Validation Evidence

- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .`
  - Result: PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q app/tests/integration/test_transit_projection_api.py --long --tb=short`
  - Result: PASS, 9 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q app/tests/unit/test_feature_registry_consistency_validator.py app/tests/unit/test_product_entitlements_models.py tests/architecture/test_api_contract_neutrality.py --tb=short`
  - Result: PASS, 36 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -m pytest -q --tb=short`
  - Result: PASS, 3315 passed, 1 skipped, 1204 deselected.
- Runtime/OpenAPI assertions:
  - route count for `/v1/transit/projection`: PASS.
  - `transit_client_projection_v1` present in `app.openapi()`: PASS.
  - `TransitChartRuntime` and `transit_chart_v1` absent from `app.openapi()`: PASS.
- CONDAMAD:
  - `condamad_validate.py ... --final`: PASS.
  - `condamad_story_validate.py .../00-story.md`: PASS.
  - `condamad_story_lint.py --strict .../00-story.md`: PASS.

## Propagation

No propagation required. The fixes were local to CS-282 implementation and existing entitlement guard coverage.

## Residual Risk

Aucun risque restant identifie.

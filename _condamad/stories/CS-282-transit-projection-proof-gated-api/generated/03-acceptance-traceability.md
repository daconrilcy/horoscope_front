# Acceptance Traceability — CS-282-transit-projection-proof-gated-api

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The public route is registered once. | `backend/app/api/v1/routers/public/transit_projection.py`; registry entry in `backend/app/api/v1/routers/registry.py`. | `test_transit_projection_route_registered_once_and_openapi_is_controlled`; runtime `app.routes` assertion in `evidence/validation.txt`. | PASS |
| AC2 | OpenAPI exposes the controlled route. | Response model `TransitProjectionResponse` and `/v1/transit/projection` route. | Architecture OpenAPI tests; `openapi-after.json`; `transit_client_projection_v1` OpenAPI assertion. | PASS |
| AC3 | Proof gate blocks missing evidence. | `TransitProjectionProofGate`; route returns `409`/`proof_blocked` before projection. | `test_transit_projection_blocks_missing_proof_gate`. | PASS |
| AC4 | The success payload is client-safe. | `TransitClientProjectionService` builds only client content, facts, public proof refs and hash. | `test_transit_projection_success_payload_is_client_safe`; negative OpenAPI/API scans. | PASS |
| AC5 | Raw runtime fields stay private. | No raw runtime schema in public contract; architecture guard allows only the controlled route. | OpenAPI assertions and negative `rg` scans in `evidence/validation.txt`. | PASS |
| AC6 | B2C plan depth is enforced. | `TransitProjectionAccessResolver` reuses `resolve_b2c_access`; projection sections are cumulative by plan. | `test_transit_projection_enforces_plan_depth`. | PASS |
| AC7 | Client degraded states are explicit. | Contract supports `degraded`, `unavailable`, `unauthorized`, `proof_blocked`; route maps blocked/denied states. | `test_transit_projection_returns_degraded_state`; `test_transit_projection_returns_unauthorized_state`; proof-blocked test. | PASS |
| AC8 | Dependency evidence is required. | Proof gate checks CS-280/CS-281 final and validation evidence plus CS-281 contract doc. | Dependency path assertions; `dependency-proof-before.md`; `dependency-proof-after.md`. | PASS |
| AC9 | Public exposure guard tests cover transits. | `backend/tests/architecture/test_api_contract_neutrality.py` updated for canonical route and forbidden transit fragments. | `python -B -m pytest -q tests/architecture/test_api_contract_neutrality.py --tb=short` -> 21 passed. | PASS |
| AC10 | Story evidence artifacts are persisted. | `evidence/openapi-before.json`, `routes-before.txt`, `dependency-proof-before.md`, `openapi-after.json`, `routes-after.txt`, `dependency-proof-after.md`, `validation.txt`, `source-checklist.md`. | Evidence existence created and capsule validated. | PASS |

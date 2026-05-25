# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `structured_facts_v1` has HTTP proof. | `backend/tests/api/test_projection_real_conditions.py::test_projection_endpoint_returns_public_shapes_for_supported_types` posts the public endpoint through `TestClient` and the `ProjectionEndpointService` using the real public builders. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC2 | `beginner_summary_v1` has HTTP proof. | Same parameterized HTTP test asserts the public response shape and payload projection id for `beginner_summary_v1`. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC3 | `client_interpretation_projection_v1` has HTTP proof. | Same parameterized HTTP test asserts the public response shape and payload projection id for `client_interpretation_projection_v1`; response sample persisted. | Targeted pytest PASS; full backend pytest PASS; `evidence/response-samples.json`. | PASS |
| AC4 | The B2C plan matrix is proven. | `test_projection_endpoint_accepts_supported_b2c_plans` covers `free`, `basic`, and `premium` via injected entitlement snapshots. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC5 | Entitlement refusal is stable. | `backend/tests/api/test_projection_authorization.py` keeps the 403 public envelope and now asserts `required_plan`. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC6 | Invalid payload errors are explicit. | `test_projection_endpoint_rejects_invalid_payload_shape` verifies the shared `invalid_request_payload` error envelope for forbidden input. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC7 | Missing chart data returns a public error. | `test_projection_endpoint_returns_public_error_for_missing_chart` verifies 404 `projection.chart_not_found`; error sample persisted. | Targeted pytest PASS; full backend pytest PASS; `evidence/response-samples.json`. | PASS |
| AC8 | Missing birth time is visible. | `test_projection_endpoint_exposes_degraded_birth_input_without_time` posts `birth_input` without `birth_time` and asserts degraded `no_time` payload. | Targeted pytest PASS; full backend pytest PASS; `evidence/response-samples.json`. | PASS |
| AC9 | Optional persistence is proven. | Existing `backend/tests/api/test_projection_persistence_endpoint.py` remains in the targeted validation set and proves `persist=true` 201 metadata. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC10 | OpenAPI exposes only the public endpoint. | Runtime route/OpenAPI command asserts canonical path present and forbidden paths absent; OpenAPI internal identifier scan passed. | `evidence/openapi-before.json`, `evidence/openapi-after.json`, `evidence/validation.txt`. | PASS |
| AC11 | Story evidence artifacts are persisted. | Evidence folder contains guardrails, OpenAPI snapshots, response samples, validation transcript, and frontend limits. | Capsule validation PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

# CS-291 Acceptance Traceability

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | The loaded app registers `POST /v1/astrology/projections`. | PASS | `backend/app/api/v1/routers/public/projections.py`, `backend/app/api/v1/routers/registry.py` | Runtime `app.routes` assertion PASS; `tests/api/test_projection_openapi.py` PASS |
| AC2 | OpenAPI exposes the public projection command. | PASS | `backend/app/services/api_contracts/public/projections.py` | Runtime `app.openapi()` assertion PASS; OpenAPI after snapshot persisted |
| AC3 | Existing chart requests use `chart_id`. | PASS | `ProjectionEndpointService._resolve_existing_chart`; route request schema | `tests/api/test_projection_endpoint.py` and `tests/unit/services/test_projection_endpoint_service.py` PASS |
| AC4 | New chart requests use `birth_input`. | PASS | `ProjectionEndpointService._calculate_chart`; `NatalCalculateRequest` reuse | `tests/api/test_projection_endpoint.py` PASS |
| AC5 | Public projection builders are dispatched. | PASS | `ProjectionEndpointService._build_projection` dispatches `StructuredFactsV1Builder`, `BeginnerSummaryV1Builder`, `ClientInterpretationProjectionV1Builder` | `tests/unit/services/test_projection_endpoint_service.py` PASS |
| AC6 | Internal projection identifiers are denied. | PASS | `SUPPORTED_PROJECTION_TYPES` allowlist and 403 `projection.unauthorized` | `tests/api/test_projection_authorization.py`; endpoint-source negative scan PASS |
| AC7 | Free/basic/premium plan access is enforced. | PASS | Plan read from `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot`; client plan field forbidden | `tests/unit/services/test_projection_endpoint_service.py` PASS |
| AC8 | Optional persistence reuses CS-264. | PASS | `ProjectionPersistenceService.persist_from_builder` reused for `persist=true` | `tests/api/test_projection_persistence_endpoint.py`; unit persistence assertion PASS |
| AC9 | OpenAPI hides forbidden internal surfaces. | PASS | Route response/request schemas reference public contracts only | `tests/api/test_projection_openapi.py`; route-local forbidden surface scan PASS |
| AC10 | Only the canonical projection route is authorized. | PASS | Only `POST /v1/astrology/projections` registered; no alternate route added | Runtime route assertion and forbidden route `rg` scan PASS |
| AC11 | Evidence artifacts are persisted. | PASS | Evidence files under `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/` | `openapi-before.json`, `openapi-after.json`, `validation.txt`, `source-checklist.md` persisted |

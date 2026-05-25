# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing transit ownership is reused. | `backend/app/domain/astrology/runtime/transit_chart_runtime.py` validates `transit_chart_v1` through `get_astrology_graph_family` and `AstrologyGraphFamilyOwner.TEMPORAL_RUNTIME`. | `python -B -m pytest -q tests/unit/domain/astrology/test_transit_chart_runtime.py tests/architecture/test_api_contract_neutrality.py --tb=short` PASS. | PASS |
| AC2 | The runtime returns structural transit objects. | `build_internal_transit_chart_runtime` builds `transiting_chart_objects` via `build_chart_object_runtime_data`, with no transit-specific chart object model. | Runtime unit tests PASS; `evidence/transit-runtime-after.json` persisted. | PASS |
| AC3 | Transit relationships are deterministic. | `_build_relationships` projects through `build_aspect_structural_runtime_data` and sorts by transit object, natal object, aspect code and orb. | `test_runtime_relationships_are_structural_and_deterministic` PASS. | PASS |
| AC4 | Astronomical proof references are emitted. | `_astronomical_proof_refs` references `CS253_GATE_MARKER`, `PRODUCTION_ASTRONOMY_MODE`, `PRODUCTION_TOLERANCE` and `SENSITIVE_GOLDEN_CASES`. | `test_runtime_emits_astronomical_proof_refs_and_doctrine_limits` PASS. | PASS |
| AC5 | Doctrine limits are documented. | `_doctrine_limits` reuses `get_astrology_doctrine_governance` for `aspect_rules` and `interpretation_rules`; governance surface updated for manifest/runtime. | `rg -n "fixed_star|fixed stars|fixed-stars" ...` reviewed; doctrine guard tests PASS. | PASS |
| AC6 | Internal trace keys stay bounded. | `TransitChartRuntimeTrace.keys` is exactly `TRANSIT_CHART_RUNTIME_TRACE_KEYS`; trace carries IDs/codes only. | `test_runtime_trace_keys_are_bounded_and_serializable` PASS. | PASS |
| AC7 | Public API surface remains neutral. | `test_transit_chart_runtime_is_not_public_api_contract` asserts no schemas, route paths or OpenAPI tokens. | `app.openapi()`, `app.routes`, `TestClient('/openapi.json')` checks PASS. | PASS |
| AC8 | Client surfaces remain closed. | No frontend/API/migration file added; runtime is under `backend/app/domain/astrology/runtime/`. | `rg` scans over `backend/app/api`, `frontend/src`, `backend/migrations` returned exit 1 = PASS no matches. | PASS |
| AC9 | Story evidence artifacts are persisted. | Evidence JSON/Markdown files created under `_condamad/stories/CS-280-internal-transit-runtime/evidence/`. | `condamad_validate.py` PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | A successful graph run produces ordered nodes. | `CalculationGraphRunner.run()` attaches `execution_trace`; `CalculationGraphNodeTrace.code` preserves runner order. | `test_successful_graph_run_produces_ordered_redacted_execution_trace`; targeted pytest PASS. | PASS |
| AC2 | The trace exposes stable graph identity fields. | `CalculationGraphExecutionTrace.version`, `graph_code`, `graph_version`, `run_id`; values built from `CalculationGraphDefinition`. | Unit test and `evidence/trace-after.json` assert version and graph identity. | PASS |
| AC3 | Node traces expose non-sensitive duration metrics. | `CalculationNodeResult.duration_ms`; trace copies only duration, status, keys and refs. | Unit test asserts `duration_ms is not None`; targeted pytest PASS. | PASS |
| AC4 | Failed node traces expose error kind. | `CalculationTraceErrorKind` and `_error_kind()` normalize runner errors. | `test_failed_node_trace_exposes_normalized_error_kind_without_cause_object`; targeted pytest PASS. | PASS |
| AC5 | Cache hits hide cached values. | `CalculationTraceCacheStatus.HIT`; trace stores output key only. | `test_cache_hit_trace_exposes_hit_state_without_cached_value`; targeted pytest PASS. | PASS |
| AC6 | Raw input payload values are redacted. | Trace model has `input_keys`, no raw input field. | Unit tests scan payload string for secret input absence; targeted runtime symbol scan PASS. | PASS |
| AC7 | Raw output payload values are redacted. | Trace model has `output_keys` and `provenance_ref`, no copied output values. | Unit tests cover success and cache secrets; targeted runtime symbol scan PASS. | PASS |
| AC8 | The terminology contract separates trace. | `execution_trace_to_dict()` includes `contract_note` separating `trace`, `provenance`, `replay_snapshot`; no replay field on trace. | `test_trace_contract_keeps_trace_provenance_and_replay_terms_distinct`; targeted pytest PASS. | PASS |
| AC9 | Public API runtime contract is unchanged. | No API/router/schema edits; architecture test added for CS-248 neutrality. | `test_calculation_graph_execution_trace_is_not_public_api_contract`; OpenAPI and route assertions PASS. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/trace-before.md`, `trace-after.json`, `openapi-routes.md`, `validation.md`; generated evidence updated. | Capsule validation PASS; evidence path checks implicit by file presence. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

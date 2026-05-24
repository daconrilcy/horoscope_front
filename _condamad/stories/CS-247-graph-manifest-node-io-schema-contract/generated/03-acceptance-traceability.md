# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `natal_chart_v1` exposes a validated manifest. | `build_natal_calculation_graph_manifest()` in `backend/app/domain/astrology/runtime/natal_calculation_graph.py`; `CalculationGraphManifest` in `calculation_graph_manifest.py`. | `python -B -m pytest -q tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py` via targeted combined run; `manifest-after.json`. | PASS |
| AC2 | Each node declares input schema descriptors. | `NodeIOSchema.input_schema` derived from `CalculationGraphDefinition.depends_on` and known graph descriptors. | `test_each_natal_node_declares_input_and_output_schema`; targeted combined pytest. | PASS |
| AC3 | Each node declares one output schema descriptor. | `NodeIOSchema.output_schema` generated from each node output key and node code. | `test_each_natal_node_declares_input_and_output_schema`; targeted combined pytest. | PASS |
| AC4 | Duplicate output keys are rejected. | `validate_graph_manifest()` duplicate output check. | `test_duplicate_output_key_is_rejected`; targeted combined pytest. | PASS |
| AC5 | Unknown required inputs are rejected. | `validate_graph_manifest()` rejects dependencies absent from global inputs and node outputs. | `test_unknown_required_input_is_rejected`; targeted combined pytest. | PASS |
| AC6 | Missing node schemas are rejected. | `validate_graph_manifest()` rejects empty input schema and incomplete output schema. | `test_missing_node_input_schema_is_rejected`, `test_missing_node_output_schema_is_rejected`; targeted combined pytest. | PASS |
| AC7 | Manifest comparison classifies breaking deltas. | `compare_graph_manifests()` and `GraphManifestDeltaKind` in `calculation_graph_manifest.py`. | `test_manifest_comparison_classifies_version_input_output_and_type_deltas`; `manifest-comparison.md`. | PASS |
| AC8 | Public API runtime contract is unchanged. | No API/router/frontend/migration code changed; architecture test extended for manifest schemas and routes. | `tests/architecture/test_api_contract_neutrality.py`; `python -B -c` OpenAPI/route checks; negative `rg` scan over `backend/app/api frontend`. | PASS |
| AC9 | Evidence artifacts are persisted. | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/*`. | Python path assertion for evidence files; files present: `validation.md`, `manifest-before.json`, `manifest-after.json`, `manifest-comparison.md`. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `transit_chart_v1` is the single selected family. | `backend/app/domain/astrology/runtime/temporal_technique_selection.py`; `temporal-selection-after.json`. | `test_temporal_technique_selection.py`; `test_temporal_family_single_path.py`. | PASS |
| AC2 | Rejected candidate reasons are explicit. | `TemporalCandidateDecision` entries for synastry, solar/lunar returns, progressions, composite, profections and forecasting. | Unit test `test_rejected_candidates_keep_explicit_non_selection_reasons`. | PASS |
| AC3 | Required inputs are declared. | `TemporalInputRequirement` entries in the selection contract and JSON snapshot. | Unit test `test_required_inputs_graph_contracts_and_relationships_are_declared`. | PASS |
| AC4 | Graph requirements are declared. | `required_graph_code=transit_chart_v1`; `required_graph_contracts` cite CS-246, CS-247, CS-248 and CS-250. | Unit test plus architecture guard proving no executable temporal graph yet. | PASS |
| AC5 | Chart object relationships are declared. | `TemporalChartObjectRequirement` and `TemporalRelationshipRequirement` entries. | Unit test `test_required_inputs_graph_contracts_and_relationships_are_declared`. | PASS |
| AC6 | Public projection stays blocked by CS-250 until closure. | Contract returns `selected-blocked-by-cs250` for pre-done status; local `CS-250` status is already `done`, so persisted snapshot is `selected-ready-after-cs250`. | `test_cs250_gate_keeps_selection_non_public_before_done`; `cs-250-gate.md`; no public surface tests. | PASS_WITH_LIMITATIONS |
| AC7 | No second temporal family is opened. | Rejected candidates all `closed`; no executable graph definition for `transit_chart_v1`. | `test_temporal_family_single_path.py`; targeted public-surface `rg` scan PASS no matches. | PASS |
| AC8 | Public API runtime contract is unchanged. | No API route, OpenAPI schema, frontend or migration change for temporal selection. | `test_api_contract_neutrality.py`; `app.routes`; `app.openapi()` checks; `api-neutrality.md`. | PASS |
| AC9 | Evidence artifacts are persisted. | `evidence/validation.md`, `temporal-selection-after.json`, `cs-250-gate.md`, `api-neutrality.md`. | Capsule validation PASS after evidence updates. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

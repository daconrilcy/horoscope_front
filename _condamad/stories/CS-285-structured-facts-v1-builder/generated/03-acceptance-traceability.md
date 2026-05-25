# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Existing projection owners are reused. | `StructuredFactsV1Builder` imports and delegates to `ChartInterpretationInputBuilder`; no API/frontend owner added. | `test_structured_facts_v1_builder_reuses_interpretation_owner`; `evidence/architecture-guard.txt`. | PASS |
| AC2 | `structured_facts_v1` is generated. | `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` emits `projection_id=structured_facts_v1`. | `pytest -q tests/unit/domain/astrology/test_structured_facts_v1_builder.py` PASS; sample JSON persisted. | PASS |
| AC3 | Payload output is stable. | Builder sorts positions, houses, aspects, signals, dominants and serializes `hash_input` with sorted keys. | `test_structured_facts_v1_output_is_stable_for_identical_runtime_input` PASS. | PASS |
| AC4 | Narrative fields are absent. | Payload contains factual sections only; excluded surfaces use non-textual category names without narrative/advice/provider field names. | Unit absence assertion PASS; targeted `rg` over builder and CS-285 test returned no matches. | PASS |
| AC5 | Missing runtime data stays deterministic. | `missing_data` records null chart id/sign balances and sorted empty collection names. | `test_structured_facts_v1_missing_runtime_data_is_deterministic` PASS. | PASS |
| AC6 | Internal primitives stay non-public. | No route, schema, migration, DB or frontend file changed. | `app.openapi()`, `app.routes`, and `TestClient('/health')` guards PASS; `evidence/public-surface-guard.txt`. | PASS |
| AC7 | Parallel pipeline drift is blocked. | One canonical `StructuredFactsV1Builder` owner under `interpretation`; AST guard checks owner reuse. | `test_structured_facts_v1_has_one_canonical_builder_owner` PASS; architecture guard PASS. | PASS |
| AC8 | Evidence artifacts are persisted. | `evidence/structured-facts-v1-sample.json`, `validation.txt`, `public-surface-guard.txt`, `architecture-guard.txt`, `broad-forbidden-scan.txt`. | Capsule validation PASS after generated evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

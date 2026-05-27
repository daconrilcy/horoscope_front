# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | `NatalExecutionInput` transports the rich contract. | `backend/app/domain/llm/runtime/contracts.py` adds typed `llm_astrology_input_v1`; service constructs it before adapter calls. | `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py::test_natal_execution_input_transports_rich_contract_to_gateway`; full backend pytest PASS. | PASS |
| AC2 | The adapter propagates the rich contract. | `backend/app/domain/llm/runtime/adapter.py` passes `natal_input.llm_astrology_input_v1` through `extra_context`. | Architecture guard `test_adapter_propagates_llm_astrology_input_through_extra_context`; targeted pytest PASS. | PASS |
| AC3 | `ExecutionContext` keeps fact ownership out. | `ExecutionContext` has no `llm_astrology_input_v1` model field; transport is `NatalExecutionInput` plus schema-owned runtime key. | `test_execution_context_does_not_own_llm_astrology_facts`; `test_natal_execution_input_is_the_typed_transport_owner`. | PASS |
| AC4 | The rendered prompt payload includes the rich contract. | `LLMGateway.build_user_payload` emits `llm_astrology_input_v1`; natal canonical schema and placeholders require the rich key. | `test_gateway_prefers_rich_input_over_chart_json_in_user_payload`; `_condamad/.../evidence/rendered-payload.json`. | PASS |
| AC5 | `chart_json` is not selected when rich input exists. | Gateway prefers rich input over `chart_json`; render vars remove `chart_json`/`natal_data` when rich key exists; natal registry demotes legacy carriers to optional. | Negative assertions in unit tests; transition scan evidence; `rg` no required natal `chart_json` in canonical registry. | PASS |
| AC6 | Remaining transition branches are bounded. | Existing `chart_json`, `natal_data`, and fallback paths remain classified as transition/governance surfaces; no new silent fallback introduced. | `_condamad/.../evidence/transition-scan.txt`; `git diff --check` PASS. | PASS |
| AC7 | Public API surface stays unchanged. | No API/router/schema files changed; OpenAPI check proves no public `llm_astrology_input_v1`. | `_condamad/.../evidence/public-surface-guard.txt`; architecture TestClient guard PASS. | PASS |
| AC8 | No real LLM call is required. | Tests use gateway/adapter doubles and direct gateway helpers only. | Targeted pytest PASS; full backend pytest PASS. | PASS |
| AC9 | Evidence artifacts are persisted. | Evidence files added under `_condamad/stories/CS-332-llm-astrology-input-v1-natal-runtime/evidence/`; generated traceability and final evidence updated. | Capsule validation PASS; evidence path checks represented by this file and `generated/10-final-evidence.md`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

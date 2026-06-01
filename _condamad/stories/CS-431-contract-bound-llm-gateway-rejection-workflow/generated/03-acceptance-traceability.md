# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Gateway accepts a resolved snapshot input. | `ResolvedGenerationContractSnapshot`; `LLMGateway.execute_resolved_snapshot`. | `test_contract_bound_llm_gateway.py` PASS. | PASS |
| AC2 | Raw natal use-case is not gateway contract source. | Snapshot method takes `snapshot`, `prompt_data`, ids; no request/use_case argument. | AST guard PASS in `ast-guard.txt`. | PASS |
| AC3 | Engine profile comes from snapshot. | `_call_contract_bound_provider` reads `snapshot.engine_profile`. | Gateway test asserts model, temperature, token budget. | PASS |
| AC4 | Prompt contract comes from snapshot. | `_build_contract_bound_messages` reads `snapshot.prompt_contract`. | Gateway test asserts prompt policy in provider message. | PASS |
| AC5 | Premium prompt excludes Basic payload. | `_prompt_visible_contract_data` allowlists `data_contract.prompt_visible`. | Premium carrier test + `prompt-carrier-scan.txt` PASS. | PASS |
| AC6 | Output schema comes from snapshot. | Provider `response_format` and validation use `snapshot.output_schema`. | Gateway/rejection tests PASS. | PASS |
| AC7 | Unknown JSON fields are rejected. | Strict schema validation returns `contract_form_rejected`. | `test_unknown_json_fields_are_rejected_when_repair_is_not_allowed` PASS. | PASS |
| AC8 | Data contract roles come from snapshot. | Carrier uses `snapshot.data_contract["prompt_visible"]`. | Gateway test asserts exact prompt-visible key set. | PASS |
| AC9 | Basic payload cannot enter Premium prompt. | Premium prompt data with `basic_natal_prompt_payload` is filtered out. | Premium carrier test + zero-hit carrier scan PASS. | PASS |
| AC10 | Provider output uses strict JSON parsing. | `validate_output` runs before schema and validators. | Invalid JSON repair test PASS. | PASS |
| AC11 | Invalid JSON gets one form repair. | Contract repair policy caps form repair at one attempt. | Invalid JSON test asserts two provider calls and `repair_attempts == 1`. | PASS |
| AC12 | Schema shape gets one repair. | Schema error follows the same single repair branch. | Unknown-field repair test PASS. | PASS |
| AC13 | Invented facts are rejected directly. | Injected validators return policy rejection without repair. | Parametrized policy rejection test PASS; integration invented fact stays audit-only. | PASS |
| AC14 | Astrological contradictions are rejected. | Natal runtime validator emits `astrological_contradiction`. | Policy rejection test + integration metadata test PASS. | PASS |
| AC15 | Technical leaks are rejected. | Natal runtime validator emits `technical_leak`. | Policy rejection test + integration run-only test PASS. | PASS |
| AC16 | Mechanical or empty text is rejected. | Injected validators reject mechanical/empty-text policy codes without content repair. | Parametrized policy rejection test PASS. | PASS |
| AC17 | Rejections persist only in runs. | `ThemeNatalReadingSlotService.record_rejected_run` remains run-only for payload. | `test_contract_bound_rejection_is_persisted_only_as_generation_run` PASS. | PASS |
| AC18 | Public readings stay accepted-only. | Public slot queries filter accepted slots. | `test_public_slot_listing_remains_accepted_only_after_rejected_attempt` PASS. | PASS |
| AC19 | Runs log contract versions. | `raw_provider_response["contract_metadata"]` stores all snapshot versions. | Integration metadata test PASS. | PASS |
| AC20 | Natal rules stay outside the gateway. | Validators are injected from natal runtime; gateway has no natal business tokens. | AST guard PASS. | PASS |
| AC21 | Story evidence artifacts are persisted. | Evidence files under `evidence/` and generated trace/final evidence updated. | Capsule validation PASS. | PASS |
| AC22 | Runs log contract hashes. | Run columns keep key/hash/snapshot; raw evidence keeps same contract metadata. | Integration metadata test PASS. | PASS |

Residual scan note: VC10 still reports pre-existing `AstroResponse_v3` and `fallback_default`
references in legacy/governance configuration and tests. This story did not delete those
surfaces; direct Premium carrier contamination and gateway ownership scans are covered and PASS.

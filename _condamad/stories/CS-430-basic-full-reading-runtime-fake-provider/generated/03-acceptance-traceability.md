# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic selects the target contract. | `ThemeNatalBasicFullReadingRuntime.generate` calls `resolve_theme_natal_reading_action` with Basic `generate_full` and resolves `theme_natal.reading.basic_full_reading.v1`. | `python -B -m pytest -q --long tests\integration\test_theme_natal_basic_full_reading_runtime.py --tb=short` PASS. | PASS |
| AC2 | Basic prompt payload is plan-backed. | `basic_natal_runtime_material.py` builds `BasicNatalReadingPlan`; runtime calls `build_basic_natal_prompt_payload`. | Runtime test asserts prompt sections; RG-164 covered by targeted pytest. | PASS |
| AC3 | Valid fake output is parsed strictly. | `ThemeNatalBasicRawProviderResponse.model_validate` validates fake output before projection. | Runtime accepted-path test PASS. | PASS |
| AC4 | Run metadata persists. | `LlmGenerationRunModel` adds `generation_contract_key/hash/snapshot_id` and `provider_mode`; runtime persists schema/hash/data metadata. | Runtime accepted-path test and slot schema test PASS. | PASS |
| AC5 | Accepted Basic reading persists. | Runtime publishes only through `ThemeNatalReadingSlotService.publish_accepted_payload`. | Runtime accepted-path test PASS. | PASS |
| AC6 | Public payload excludes raw provider data. | `_project_basic_public_payload` emits `ThemeNatalBasicPublicReading`; raw response remains on run only. | Runtime accepted-path test and `public-raw-leak-scan-after.txt` PASS with allowed technical/test hits. | PASS |
| AC7 | Invalid JSON mode is rejected. | `ThemeNatalFakeProviderMode.INVALID_JSON` returns invalid JSON and records rejected run. | Parameterized invalid-mode test PASS. | PASS |
| AC8 | Unknown field mode is rejected. | Strict Pydantic raw schema forbids `debug_trace`. | Parameterized invalid-mode test PASS. | PASS |
| AC9 | Empty source mode is rejected. | Raw evidence ref `source_id` min length and semantic validation reject it. | Parameterized invalid-mode test PASS. | PASS |
| AC10 | Invented fact mode is rejected. | `_semantic_validation_errors` rejects source IDs absent from Basic prompt-visible evidence. | Parameterized invalid-mode test PASS. | PASS |
| AC11 | Technical leak mode is rejected. | `_TECHNICAL_LEAK_TOKENS` reject technical strings before projection. | Parameterized invalid-mode test PASS. | PASS |
| AC12 | Mechanical phrase mode is rejected. | `_MECHANICAL_PHRASES` reject canned/mechanical provider wording. | Parameterized invalid-mode test PASS. | PASS |
| AC13 | Short section mode is rejected. | Raw section `narrative` min length rejects short text. | Parameterized invalid-mode test PASS. | PASS |
| AC14 | Quota waits for acceptance. | Runtime calls `consume_quota_after_publication` only after `publish_accepted_payload`; rejected path does not consume. | Accepted-path test asserts persisted accepted slot inside quota side effect; invalid-mode tests assert no quota call. | PASS |
| AC15 | Same request is idempotent. | Runtime returns accepted public slot before new provider attempt for an already accepted key. | Idempotence test PASS; run count increases once only. | PASS |
| AC16 | Old natal use cases are not called. | Runtime file does not call `generate_natal_interpretation`, `natal_interpretation_short`, or `natal_long_free`. | AST guard test PASS; `legacy-call-scan-after.txt` recorded expected legacy hits outside new runtime. | PASS |
| AC17 | Free preview traversal stays contractual. | `build_contractual_theme_natal_free_preview` validates fake Free raw/public schemas without legacy generator. | Free preview test PASS. | PASS |
| AC18 | Story evidence artifacts are persisted. | Evidence files under `evidence/` plus generated traceability/final evidence updated. | `condamad_validate.py ... --final` PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

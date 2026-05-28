# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The builder has one canonical owner. | `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`; legacy `theme_astral_llm_input_v1_builder.py` deleted. | `test_provider_payload_builder_has_one_canonical_owner`; legacy scan in `evidence/no-duplication-proof.txt`. | PASS |
| AC2 | Top-level payload keys are stable. | `_TOP_LEVEL_KEYS` and `_assert_payload_skeleton`. | `test_provider_payload_skeleton_is_stable_for_all_commercial_plans`. | PASS |
| AC3 | `input_data` keys are stable. | `_INPUT_DATA_KEYS` with birth context, facts, material, themes, limits. | `test_provider_payload_skeleton_is_stable_for_all_commercial_plans`. | PASS |
| AC4 | Commercial labels stay hidden. | Provider-visible payload receives `delivery_profile` values, not plan labels. | `test_commercial_labels_stay_out_of_provider_payload`; `evidence/plan-hiding-proof.txt`. | PASS |
| AC5 | `delivery_profile` is emitted. | `resolve_theme_astral_provider_delivery_profile` in configuration; builder emits `delivery_profile`. | `test_delivery_material_voice_and_output_contract_are_emitted`. | PASS |
| AC6 | `interpretation_material` is emitted. | Builder reuses `InterpretationMaterialBuilder` and injects material under `input_data`. | Builder, integration, and repository tests in `evidence/validation.txt`. | PASS |
| AC7 | Profile quantities vary. | Configuration maps internal plans to different material/fact/section budgets. | `test_profile_quantities_vary_without_skeleton_drift`. | PASS |
| AC8 | Voice changes style fields only. | `astrologer_voice` is a separate top-level style block. | `test_voice_changes_style_fields_only_and_truth_stays_engine_owned`. | PASS |
| AC9 | Truth data stays engine-owned. | `_astrological_facts` projects from `ChartInterpretationInputRuntimeData`; material comes from CS-365 builder. | `test_voice_changes_style_fields_only_and_truth_stays_engine_owned`; material integration tests. | PASS |
| AC10 | `output_contract` is versioned. | `_output_contract` references `THEME_ASTRAL_RESPONSE_CONTRACT_ID` and version `v1`. | `test_delivery_material_voice_and_output_contract_are_emitted`. | PASS |
| AC11 | Handoff uses the built payload. | `LLMGateway.build_user_payload` prefers `THEME_ASTRAL_INPUT_CONTRACT_ID` context payload. | `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`. | PASS |
| AC12 | Prompt data is not duplicated. | Handoff serializes one user payload block and no developer prompt block is built by the payload builder. | `test_prompt_data_is_carried_once_in_user_payload_block`; `evidence/no-duplication-proof.txt`. | PASS |
| AC13 | Protected surfaces stay unchanged. | No frontend, migration, DB model, or repository app code diff. | `git diff --quiet` protected-surface checks in `evidence/validation.txt`. | PASS |
| AC14 | Story evidence is persisted. | Evidence folder contains source availability, before/after snapshots, plan hiding, duplication, validation. | VC15 PASS; capsule validation PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.


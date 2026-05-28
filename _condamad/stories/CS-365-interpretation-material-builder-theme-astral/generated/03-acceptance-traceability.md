# CS-365 - Acceptance Traceability

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | The builder has one canonical owner. | PASS | `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`; AST guard in `test_interpretation_material_builder.py` proves a single `class InterpretationMaterialBuilder` owner. | Targeted pytest with `--long` PASS. |
| AC2 | Material keys are stable. | PASS | `InterpretationMaterialBlock.to_payload()` emits all `INTERPRETATION_MATERIAL_KEYS`. | Unit test `test_material_keys_are_stable_for_all_profiles` PASS. |
| AC3 | Planet-sign facts match sourced text. | PASS | Planet-sign selection matches object code plus zodiac sign. | Unit test `test_planet_sign_house_and_aspect_facts_match_sourced_text` PASS. |
| AC4 | Planet-house facts match sourced text. | PASS | Planet-house selection matches house position code plus house number. | Unit test `test_planet_sign_house_and_aspect_facts_match_sourced_text` PASS. |
| AC5 | Aspect facts match sourced text. | PASS | Aspect selection matches aspect code and preserves participant fact refs. | Unit test `test_planet_sign_house_and_aspect_facts_match_sourced_text` PASS. |
| AC6 | Items have `source_ref`. | PASS | `InterpretationMaterialItem.to_payload()` requires `source_ref`. | Unit test `test_items_always_keep_source_fact_and_text_or_hint` PASS. |
| AC7 | Items have `fact_ref`. | PASS | Each candidate is built with a calculated `fact_ref`. | Unit test `test_items_always_keep_source_fact_and_text_or_hint` PASS. |
| AC8 | Missing source text emits no item. | PASS | `_SourceIndex.find()` emits only exact source matches with text or writing hint; no fallback text is generated. | Unit test `test_missing_source_text_emits_no_material_item` PASS. |
| AC9 | Profiles limit quantities. | PASS | `_PROFILE_POLICIES` applies `free`, `basic`, `premium` thresholds and limits. | Unit test `test_material_keys_are_stable_for_all_profiles` PASS. |
| AC10 | LLM input gets material. | PASS | `ThemeAstralLLMInputV1Builder` writes `input_data.interpretation_material`. | Integration test PASS with `--long`. |
| AC11 | Protected surfaces stay unchanged. | PASS | No provider, output schema, frontend, migration, or SQL owner change. | `git diff --check` PASS; targeted SQL scan has no production match. |
| AC12 | Story evidence is persisted. | PASS | Capsule generated and evidence files updated. | `condamad_validate.py` PASS after final evidence repair. |
| AC13 | Items have `interpretive_text` or `writing_hint`. | PASS | `InterpretationMaterialItem.to_payload()` emits one source text field. | Unit test `test_items_always_keep_source_fact_and_text_or_hint` PASS. |

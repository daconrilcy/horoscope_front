# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The plan exposes Basic identity fields. | `BasicNatalReadingPlan.to_payload()` emits `level`, `locale`, `engine_version`. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC2 | The builder returns an inspectable plan. | `BasicNatalReadingPlanBuilder.build()` returns sections, public evidence, limits and style constraints. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC3 | Eligibility controls plan surfaces. | `_fact_allowed()` and `_forbidden_fact_families()` use `EligibilityContext`. | `test_date_only_plan_omits_houses_angles_mc_asc_and_house_rulers` | PASS |
| AC4 | Fact graph IDs feed required facts. | Sections use `NatalFactGraph.facts` and `required_fact_ids`. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC5 | Salience controls section priority. | `_ordered_allowed_fact_ids()` and `_select_sections()` use `NatalSalienceModel.score()`. | `test_salience_controls_section_priority_when_budget_is_tight` | PASS |
| AC6 | Theme codes populate sections. | `ThemeModel.theme_code` fills `theme_codes`. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC7 | Syntheses feed section intent. | `SynthesisResolver.resolve()` gates eligible theme sections and synthesis section. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC8 | Date-only omits house surfaces. | Date-only forbids angle, house and rulership families. | `test_date_only_plan_omits_houses_angles_mc_asc_and_house_rulers` | PASS |
| AC9 | Plan section count stays bounded. | `MAX_READING_PLAN_SECTIONS = 8`; builder cap enforced. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC10 | Full birth-time order is stable. | `_FULL_SECTION_ORDER`. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC11 | Date-only order is stable. | `_DATE_ONLY_SECTION_ORDER`. | `test_date_only_plan_omits_houses_angles_mc_asc_and_house_rulers` | PASS |
| AC12 | Each section names required facts. | `BasicNatalPlanSection.required_fact_ids`. | `test_plan_exposes_basic_identity_and_inspectable_sections` | PASS |
| AC13 | Each content section names evidence. | `supporting_evidence_ids` generated from required facts. | `test_public_evidence_is_user_readable_and_linked_to_sections` | PASS |
| AC14 | Forbidden facts stay out of sections. | `forbidden_fact_ids` distinct from required facts. | `test_forbidden_fact_ids_are_kept_out_of_required_facts` | PASS |
| AC15 | Public evidence is user-readable. | `BasicNatalPublicEvidence` label/explanation mapper. | `test_public_evidence_is_user_readable_and_linked_to_sections` | PASS |
| AC16 | Public limitations are emitted. | Builder combines eligibility limitations and Basic scope limit. | `test_limitations_and_disclaimers_are_emitted` | PASS |
| AC17 | Required disclaimers are emitted. | Builder emits non-predictive disclaimer. | `test_limitations_and_disclaimers_are_emitted` | PASS |
| AC18 | House 10 is not the sole model. | House routing keeps non-vocation sections. | `test_house_10_is_not_the_only_basic_narrative_model` | PASS |
| AC19 | House 4 archetype has coverage. | `_HOUSE_SECTION_OVERRIDES["house:4"] = "inner_life"`. | `test_house_4_archetype_routes_to_inner_life` | PASS |
| AC20 | House 7 archetype has coverage. | `_HOUSE_SECTION_OVERRIDES["house:7"] = "relationships"`. | `test_house_7_archetype_routes_to_relationships` | PASS |
| AC21 | House 12 archetype has coverage. | `_HOUSE_SECTION_OVERRIDES["house:12"] = "tensions"`. | `test_house_12_archetype_routes_to_tensions` | PASS |
| AC22 | Contradictions shape plan nuance. | Tension sections preserve required and forbidden fact IDs. | `test_contradictions_shape_plan_nuance_without_final_prose` | PASS |
| AC23 | Technical internals stay non-public. | Public evidence mapper omits scores, source paths and prompt hints. | `test_public_evidence_does_not_expose_internal_scoring_or_prompt_hints`; negative `rg` | PASS |


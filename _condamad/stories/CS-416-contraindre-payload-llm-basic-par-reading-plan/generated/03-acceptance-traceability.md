# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Basic payload selection is derived from `BasicNatalReadingPlan`. | `ThemeAstralProviderPayloadBuilder.build(..., basic_reading_plan=...)` requires the plan for `commercial_plan="basic"` and delegates to `_basic_natal_prompt_payload`. | `pytest ...test_basic_natal_prompt_payload_builder.py`: 5 passed. | PASS |
| AC2 | `BasicNatalPromptPayload` exposes expected narrative sections. | `basic_natal_prompt_payload.sections` and `resolved_syntheses` are projected from `reading_plan.sections`. | Payload contract tests and `basic-payload-after.json`. | PASS |
| AC3 | Provider handoff receives the Basic payload contract. | Basic `input_data` now contains only `basic_natal_prompt_payload`; schema declares this variant. | `pytest ...test_theme_astral_provider_payload_builder.py -k "natal or basic"`: 4 passed. | PASS |
| AC4 | Raw `NatalResult` cannot select new Basic prompt facts. | Builder imports `BasicNatalReadingPlan`, not `NatalResult`; Basic path refuses missing plan. | AST tests in `test_basic_natal_prompt_payload_builder.py` and `test_llm_astrology_input_payload_boundaries.py`: PASS. | PASS |
| AC5 | Prompt-visible Basic payload excludes personal data. | Basic prompt payload omits `birth_context`, coordinates, user identifiers and raw runtime carriers. | Privacy token tests on `basic_natal_prompt_payload`: PASS; VC8 scan has existing non-Basic/non-prompt-visible matches documented. | PASS |
| AC6 | Prompt-visible Basic payload includes `editorial_evidence`. | `_provider_editorial_evidence` emits label, explanation and section codes from public evidence. | Contract shape test: PASS. | PASS |
| AC7 | Prompt-visible Basic payload excludes internal scores. | Basic prompt payload serializer never emits scoring fields. | Token tests and VC9 scan classification: PASS. | PASS |
| AC8 | Basic style constraints are sent to prompt layer. | `_BASIC_STYLE_CONSTRAINTS` adds 900-1300 words, 6-8 sections, `vous`, no firm prediction, no prescriptive advice. | Style constraint test: PASS. | PASS |
| AC9 | `chart_json` stays absent from prompt-visible Basic natal payloads. | Basic `input_data` has no `chart_json` or `natal_data` carrier. | Token tests and architecture guard: PASS. | PASS |
| AC10 | Existing Basic assembly remains usable. | Basic builder still emits canonical top-level provider payload and output contract. | Provider builder targeted pytest: PASS. | PASS |
| AC11 | Existing Premium assembly remains usable. | Premium/free input data path remains unchanged. | Provider builder Premium assertions under targeted pytest: PASS. | PASS |
| AC12 | Story evidence artifacts are persisted. | `evidence/basic-payload-before.json`, `basic-payload-after.json`, `validation.txt`. | VC10 evidence file check: PASS. | PASS |
| AC13 | Prompt-visible Basic payload excludes internal source paths. | Serializer exposes public labels/explanations, not `source_paths` or fixture paths. | Token test excludes `runtime.fact`: PASS. | PASS |
| AC14 | Prompt-visible Basic payload excludes raw evidence IDs. | `editorial_evidence` omits `id`; section evidence labels replace IDs. | Test asserts no `id` in provider editorial evidence: PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.

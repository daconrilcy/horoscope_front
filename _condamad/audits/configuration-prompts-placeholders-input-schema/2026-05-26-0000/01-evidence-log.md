# Evidence Log - Configuration Prompts Placeholders Input Schema

| ID | Evidence type | Command / Source | Result | Path | Surface | Limitation |
|---|---|---|---|---|---|---|
| E-001 | source_inspection | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | PASS | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | Story contract | None. |
| E-002 | source_inspection | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | PASS | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | Brief questions | None. |
| E-003 | source_inspection | `_condamad/stories/regression-guardrails.md` | PASS | `_condamad/stories/regression-guardrails.md` | Guardrail registry | Exact `llm_astrology_input` guardrail absent. |
| E-004 | source_inspection | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | Prior LLM audit | Adjacent audit. |
| E-005 | source_inspection | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | Prior prompt pipeline audit | Adjacent audit. |
| E-006 | source_inspection | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | Prior readiness audit | Adjacent audit. |
| E-007 | source_inspection | `Get-Content backend/app/domain/llm/configuration/canonical_use_case_registry.py` | PASS | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:180-212` | Full/short natal contracts | Runtime DB not dumped. |
| E-008 | source_inspection | `Get-Content backend/app/domain/llm/configuration/canonical_use_case_registry.py` | PASS | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:271-390` | Thematic natal contracts | Later continuation inferred from same pattern. |
| E-009 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | PASS | `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py:64-73` | Active natal taxonomy | Bootstrap, not DB dump. |
| E-010 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_29_prompts.py` | PASS | `backend/app/ops/llm/bootstrap/seed_29_prompts.py:29-31,66-68,117-134` | Legacy natal prompt seeds | Bootstrap artifact. |
| E-011 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | PASS | `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py:44-49,175-186,402` | GPT-5 natal prompt seeds | Prompt copy read-only. |
| E-012 | source_inspection | `Get-Content backend/app/services/llm_generation/natal/interpretation_service.py` | PASS | `backend/app/services/llm_generation/natal/interpretation_service.py:579-653,935-947` | Natal runtime assembly | Adjacent service evidence. |
| E-013 | source_inspection | `Get-Content backend/app/domain/llm/runtime/contracts.py` | PASS | `backend/app/domain/llm/runtime/contracts.py:117-138` | Runtime input contracts | No target contract. |
| E-014 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1337-1368` | Gateway rendering path | Source inspection only. |
| E-015 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1479-1487` | `build_user_payload` trigger | Body traced by prior audit. |
| E-016 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1871-1905` | Validation payload builder | Only declared schema props. |
| E-017 | source_inspection | `Get-Content backend/app/domain/llm/prompting/prompt_renderer.py` | PASS | `backend/app/domain/llm/prompting/prompt_renderer.py` | `PromptRenderer` | No runtime execution. |
| E-018 | source_inspection | `Get-Content backend/app/domain/llm/runtime/input_validator.py` | PASS | `backend/app/domain/llm/runtime/input_validator.py` | Generic input validator | Generic JSON Schema only. |
| E-019 | targeted_scan | `rg -n "llm_astrology_input\|facts\|signals\|limits\|proofs" backend/app/domain/llm backend/app/ops/llm/bootstrap backend/tests/llm_orchestration` | PASS | `backend/app/domain/llm`, `backend/app/ops/llm/bootstrap`, `backend/tests/llm_orchestration` | Target injection terms | Scoped scan. |
| E-020 | targeted_scan | `rg -n "structured_facts_v1\|AINarrativeInput\|ChartInterpretationInput\|client_interpretation_projection_v1\|llm_astrology_input" backend/app/services/llm_generation/natal backend/app/domain/llm backend/tests/llm_orchestration` | PASS | `backend/app/services/llm_generation/natal`, `backend/app/domain/llm`, `backend/tests/llm_orchestration` | Modern projection injection | Scoped scan. |
| E-021 | source_inspection | `Get-Content backend/app/domain/llm/prompting/catalog.py` | PASS | `backend/app/domain/llm/prompting/catalog.py:98-145,196-208` | Runtime catalog and fallback configs | DB assembly path separate. |
| E-022 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1603-1642` | Legacy fallback behavior | Output fallback, not input fallback. |
| E-023 | source_inspection | `Get-Content backend/app/domain/llm/configuration/assembly_resolver.py` | PASS | `backend/app/domain/llm/configuration/assembly_resolver.py:117-150,221-260` | Assembly preview/resolution | Preview limitation. |
| E-024 | source_inspection | Mandatory entrypoint files | PASS | `backend/app/domain/llm/configuration/**`, `backend/app/domain/llm/runtime/input_validation.py` | Mandatory entrypoints | Some are facades. |
| E-025 | worktree_scan | `git status --short -- _condamad _story_briefs backend/app backend/tests` | PASS | repository root | Worktree scope before writes | Audit files added later. |

| ID | Result | Command or source | Path | Surface | Reproducible result | Limitation |
|---|---|---|---|---|---|---|
| E-001 | PASS | Source inspection | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | Story contract | Audit-only story requires files `00-audit.md` to `04-readiness.md`, no application changes, and classification values `compatible`, `partiel`, `bloquant`, `legacy fallback`. | None. |
| E-002 | PASS | Source inspection | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | Brief questions | Brief requires explicit audit of placeholders, input schemas, assemblies, `PromptRenderer`, `build_user_payload`, `chart_json`, `natal_data`, `astro_context`, and `llm_astrology_input`. | None. |
| E-003 | PASS | Source inspection | `_condamad/stories/regression-guardrails.md` | Guardrail registry | RG-018, RG-021 and RG-022 cover prompt fallback/config validation; no exact guardrail exists for `llm_astrology_input` readiness artifacts. | Registry is large; only LLM and story-declared relevant invariants were mapped. |
| E-004 | PASS | Source inspection | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | Prior LLM audit | Prior audit classifies current natal LLM input as centered on `chart_json`, `natal_data`, `evidence_catalog`, and `astro_context`. | Adjacent audit, not same domain. |
| E-005 | PASS | Source inspection | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | Prior prompt pipeline audit | Prior audit traces `NatalExecutionInput` through gateway context and `build_user_payload`, with `chart_json` as prompt-visible data. | Adjacent audit, not same domain. |
| E-006 | PASS | Source inspection | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | Prior readiness audit | Prior audit recommends `AINarrativeInputContract`; current LLM status is `available-not-injected`. | Adjacent audit, not same domain. |
| E-007 | PASS | Source inspection | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:180-212` | `natal_interpretation`, `natal_interpretation_short` | Both active natal contracts require `chart_json` in `input_schema`; placeholders are `chart_json` plus optional persona for full interpretation. | Source contract, not DB snapshot. |
| E-008 | PASS | Source inspection | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:271-390` | Thematic natal modules | Thematic natal contracts require `chart_json`, use `persona_name`, and fallback to `natal_interpretation_short`. | Later lines continue same pattern for `natal_evolution_path`. |
| E-009 | PASS | Source inspection | `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py:64-73` | Active natal assembly taxonomy | Active natal feature/subfeature/plan mappings include `natal_interpretation_short`, `natal_interpretation`, and seven thematic modules. | Bootstrap taxonomy, not runtime DB. |
| E-010 | PASS | Source inspection | `backend/app/ops/llm/bootstrap/seed_29_prompts.py:29-31,66-68,117-134` | Seeded legacy natal prompts | Seeded short/full natal prompts embed `{{chart_json}}`; seeded placeholders include `chart_json`, `locale`, `use_case`, and `persona_name`. | Historical bootstrap remains relevant through seed path only. |
| E-011 | PASS | Source inspection | `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py:44-49,175-186,402` | GPT-5 v3 natal prompts | Current v3 full and thematic prompt templates still declare `{{chart_json}}` as source unique/exclusive; lint placeholders include `chart_json`. | Prompt copy was read only. |
| E-012 | PASS | Source inspection | `backend/app/services/llm_generation/natal/interpretation_service.py:579-653,935-947` | `NatalExecutionInput` assembly | Runtime builds `chart_json_dict`, `evidence_catalog`, `astro_context`; passes `chart_json`, `natal_data`, `evidence_catalog`, `astro_context` to `NatalExecutionInput`. | Service is adjacent runtime source, not modified. |
| E-013 | PASS | Source inspection | `backend/app/domain/llm/runtime/contracts.py:117-138` | Runtime input contracts | `ExecutionContext` has `natal_data`, `chart_json`, `astro_context`; `NatalExecutionInput` requires `chart_json`, `natal_data`, `evidence_catalog`, `astro_context`. | Contract has no `llm_astrology_input` field. |
| E-014 | PASS | Source inspection | `backend/app/domain/llm/runtime/gateway.py:1337-1368` | Placeholder rendering path | Gateway builds render variables from user input plus context, then calls `PromptRenderer.render(... required_variables=config.required_prompt_placeholders ...)`. | Source inspection only. |
| E-015 | PASS | Source inspection | `backend/app/domain/llm/runtime/gateway.py:1479-1487` | `build_user_payload` trigger | Gateway calls `build_user_payload` and passes `chart_json_in_prompt` based on `{{chart_json}}` in rendered developer prompt. | `build_user_payload` body not fully quoted here; behavior is traced by adjacent audit E-005. |
| E-016 | PASS | Source inspection | `backend/app/domain/llm/runtime/gateway.py:1871-1905` | Input validation payload builder | If schema declares `chart_json`, gateway fills it from `context.natal_data`, raw dict `chart_json`, or parsed string `chart_json`. | Only validates declared schema properties. |
| E-017 | PASS | Source inspection | `backend/app/domain/llm/prompting/prompt_renderer.py` | `PromptRenderer` | Renderer supports flat `{{snake_case}}` placeholders and `context_quality` conditional blocks; required placeholders fail when unresolved or unauthorized. | No structured block API observed. |
| E-018 | PASS | Source inspection | `backend/app/domain/llm/runtime/input_validator.py` | `validate_input` | Validation delegates to JSON Schema Draft 7 and returns errors; no astrology-specific semantic validation exists here. | Generic validator can validate richer schema once declared. |
| E-019 | PASS | Command | `rg -n "llm_astrology_input\|facts\|signals\|limits\|proofs" backend/app/domain/llm backend/app/ops/llm/bootstrap backend/tests/llm_orchestration` | Target injection terms | No hit for `llm_astrology_input`; only unrelated `limits` hits in persona/context comments. | Search scoped to LLM domain, bootstrap and orchestration tests. |
| E-020 | PASS | Command | `rg -n "structured_facts_v1\|AINarrativeInput\|ChartInterpretationInput\|client_interpretation_projection_v1\|llm_astrology_input" backend/app/services/llm_generation/natal backend/app/domain/llm backend/tests/llm_orchestration` | Modern projection injection | Zero hits in scoped LLM runtime/service/orchestration paths. | Does not search astrology domain builders already covered by CS-326. |
| E-021 | PASS | Source inspection | `backend/app/domain/llm/prompting/catalog.py:98-145,196-208` | Runtime catalog and fallback configs | Catalog includes `natal_long_free`, `natal_interpretation`, `natal_interpretation_short`; fallback configs are limited to `test_natal` and `test_guidance`. | Catalog is one source among assembly DB/runtime. |
| E-022 | PASS | Source inspection | `backend/app/domain/llm/runtime/gateway.py:1603-1642` | Legacy fallback behavior | Supported feature output failures do not fall back to legacy use cases; non-supported paths may invoke configured fallback target. | Output fallback, not input-schema fallback. |
| E-023 | PASS | Source inspection | `backend/app/domain/llm/configuration/assembly_resolver.py:117-150,221-260` | Assembly preview and resolution | Assembly preview extracts placeholders and mocks `chart_json`/`natal_data` for `feature == "natal"`; resolution composes feature/subfeature templates and plan/persona blocks. | Preview mock does not prove runtime payload completeness. |
| E-024 | PASS | Source inspection | `backend/app/domain/llm/configuration/assemblies.py`, `assembly_registry.py`, `prompt_versions.py`, `prompt_version_lookup.py`, `input_validation.py` | Mandatory entrypoints | Entry points route to assembly registry/resolver, prompt version lookup, and input validation owners. | Some are facade entrypoints by design. |
| E-025 | PASS | Command | `git status --short -- _condamad _story_briefs backend/app backend/tests` | Worktree scope | Before writing audit files, only `_condamad/run-state.json` was untracked; no `backend/app` or `backend/tests` modifications were present. | Audit files are expected to appear after this evidence. |

## E-001 Story Contract

Result: PASS. Source inspection of `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` proves the audit-only output shape and no-application-change rule.

## E-002 Brief Questions

Result: PASS. Source inspection of `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` proves the mandatory questions and mandatory sources.

## E-003 Guardrail Registry

Result: PASS. Source inspection of `_condamad/stories/regression-guardrails.md` maps RG-018, RG-021 and RG-022; no exact guardrail exists for `llm_astrology_input` readiness.

## E-004 Prior Calculs Interpretations Audit

Result: PASS. Source inspection of `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` records current natal LLM input centered on `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`.

## E-005 Prior Pipeline Prompt Audit

Result: PASS. Source inspection of `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` traces `NatalExecutionInput`, gateway context and `build_user_payload`.

## E-006 Prior Projection Readiness Audit

Result: PASS. Source inspection of `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` records `AINarrativeInputContract` as candidate and current LLM status as available-not-injected.

## E-007 Canonical Full And Short Natal Contracts

Result: PASS. Source inspection of `backend/app/domain/llm/configuration/canonical_use_case_registry.py:180-212` proves `natal_interpretation` and `natal_interpretation_short` require `chart_json`.

## E-008 Canonical Thematic Natal Contracts

Result: PASS. Source inspection of `backend/app/domain/llm/configuration/canonical_use_case_registry.py:271-390` proves thematic natal contracts require `chart_json`, `persona_name` and fallback to `natal_interpretation_short`.

## E-009 Active Natal Taxonomy

Result: PASS. Source inspection of `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py:64-73` lists active natal feature/subfeature/plan mappings.

## E-010 Legacy Natal Prompt Seeds

Result: PASS. Source inspection of `backend/app/ops/llm/bootstrap/seed_29_prompts.py:29-31,66-68,117-134` proves seeded natal prompts use `{{chart_json}}`.

## E-011 GPT5 Natal Prompt Seeds

Result: PASS. Source inspection of `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py:44-49,175-186,402` proves v3 full and thematic prompts still use `{{chart_json}}`.

## E-012 Natal Runtime Assembly

Result: PASS. Source inspection of `backend/app/services/llm_generation/natal/interpretation_service.py:579-653,935-947` proves `chart_json`, `natal_data`, `evidence_catalog` and `astro_context` are assembled into `NatalExecutionInput`.

## E-013 Runtime Input Contracts

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/contracts.py:117-138` proves current input carriers and absence of `llm_astrology_input`.

## E-014 Gateway Placeholder Rendering Path

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/gateway.py:1337-1368` proves render variables and `required_prompt_placeholders` are passed to `PromptRenderer`.

## E-015 Build User Payload Trigger

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/gateway.py:1479-1487` proves `chart_json_in_prompt` controls `build_user_payload`.

## E-016 Validation Payload Builder

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/gateway.py:1871-1905` proves schema-declared `chart_json` can be filled from `natal_data`, dict `chart_json` or parsed string `chart_json`.

## E-017 PromptRenderer Constraints

Result: PASS. Source inspection of `backend/app/domain/llm/prompting/prompt_renderer.py` proves flat placeholder and `context_quality` block rendering behavior.

## E-018 Generic Input Validator

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/input_validator.py` proves JSON Schema Draft 7 validation without astrology-specific semantics.

## E-019 Target Injection Term Scan

Result: PASS. Command `rg -n "llm_astrology_input|facts|signals|limits|proofs" backend/app/domain/llm backend/app/ops/llm/bootstrap backend/tests/llm_orchestration` found no `llm_astrology_input` and only unrelated `limits` hits.

## E-020 Modern Projection Injection Scan

Result: PASS. Command `rg -n "structured_facts_v1|AINarrativeInput|ChartInterpretationInput|client_interpretation_projection_v1|llm_astrology_input" backend/app/services/llm_generation/natal backend/app/domain/llm backend/tests/llm_orchestration` returned zero hits.

## E-021 Runtime Catalog And Fallback Configs

Result: PASS. Source inspection of `backend/app/domain/llm/prompting/catalog.py:98-145,196-208` proves natal runtime catalog entries and fallback configs limited to tests.

## E-022 Legacy Fallback Behavior

Result: PASS. Source inspection of `backend/app/domain/llm/runtime/gateway.py:1603-1642` proves supported feature output fallback is blocked while non-supported fallback path remains.

## E-023 Assembly Preview And Resolution

Result: PASS. Source inspection of `backend/app/domain/llm/configuration/assembly_resolver.py:117-150,221-260` proves placeholder extraction and natal mock variables `chart_json`/`natal_data`.

## E-024 Mandatory Entrypoints

Result: PASS. Source inspection of `backend/app/domain/llm/configuration/assemblies.py`, `assembly_registry.py`, `prompt_versions.py`, `prompt_version_lookup.py`, and `input_validation.py` proves mandatory owners exist.

## E-025 Worktree Scope Before Writes

Result: PASS. Command `git status --short -- _condamad _story_briefs backend/app backend/tests` before audit writes showed only `_condamad/run-state.json` untracked and no backend app/test changes.

# Evidence Log - Configuration Prompts Placeholders Input Schema

| ID | Evidence type | Command / Source | Result | Path | Surface | Limitation |
|---|---|---|---|---|---|---|
| E-001 | source_inspection | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | PASS | `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | Story contract | None. |
| E-002 | source_inspection | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | PASS | `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | Brief questions | None. |
| E-003 | source_inspection | `_condamad/stories/regression-guardrails.md` | PASS | `_condamad/stories/regression-guardrails.md` | Guardrail registry | Exact `llm_astrology_input` guardrail absent. |
| E-004 | source_inspection | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | Prior LLM audit | Adjacent audit. |
| E-005 | source_inspection | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | Prior prompt pipeline audit | Adjacent audit. |
| E-006 | source_inspection | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | PASS | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | Prior readiness audit | Adjacent audit. |
| E-007 | source_inspection | `Get-Content backend/app/domain/llm/configuration/canonical_use_case_registry.py` | PASS | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:180-212` | `natal_interpretation`, `natal_interpretation_short` | Source contract, not DB snapshot. |
| E-008 | source_inspection | `Get-Content backend/app/domain/llm/configuration/canonical_use_case_registry.py` | PASS | `backend/app/domain/llm/configuration/canonical_use_case_registry.py:271-390` | Thematic natal modules | Later lines continue same pattern for `natal_evolution_path`. |
| E-009 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | PASS | `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py:64-73` | Active natal assembly taxonomy | Bootstrap taxonomy, not runtime DB. |
| E-010 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_29_prompts.py` | PASS | `backend/app/ops/llm/bootstrap/seed_29_prompts.py:29-31,66-68,117-134` | Seeded legacy natal prompts | Historical bootstrap remains relevant through seed path only. |
| E-011 | source_inspection | `Get-Content backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | PASS | `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py:44-49,175-186,402` | GPT-5 v3 natal prompts | Prompt copy was read only. |
| E-012 | source_inspection | `Get-Content backend/app/services/llm_generation/natal/interpretation_service.py` | PASS | `backend/app/services/llm_generation/natal/interpretation_service.py:579-653,935-947` | `NatalExecutionInput` assembly | Service is adjacent runtime source, not modified. |
| E-013 | source_inspection | `Get-Content backend/app/domain/llm/runtime/contracts.py` | PASS | `backend/app/domain/llm/runtime/contracts.py:117-138` | Runtime input contracts | Contract has no `llm_astrology_input` field. |
| E-014 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1337-1368` | Placeholder rendering path | Source inspection only. |
| E-015 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1479-1487` | `build_user_payload` trigger | Body traced by adjacent audit E-005. |
| E-016 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1871-1905` | Input validation payload builder | Only validates declared schema properties. |
| E-017 | source_inspection | `Get-Content backend/app/domain/llm/prompting/prompt_renderer.py` | PASS | `backend/app/domain/llm/prompting/prompt_renderer.py` | `PromptRenderer` | No structured block API observed. |
| E-018 | source_inspection | `Get-Content backend/app/domain/llm/runtime/input_validator.py` | PASS | `backend/app/domain/llm/runtime/input_validator.py` | `validate_input` | Generic validator can validate richer schema once declared. |
| E-019 | targeted_scan | `rg -n "llm_astrology_input\|facts\|signals\|limits\|proofs" backend/app/domain/llm backend/app/ops/llm/bootstrap backend/tests/llm_orchestration` | PASS | `backend/app/domain/llm`, `backend/app/ops/llm/bootstrap`, `backend/tests/llm_orchestration` | Target injection terms | Search scoped to LLM domain, bootstrap and orchestration tests. |
| E-020 | targeted_scan | `rg -n "structured_facts_v1\|AINarrativeInput\|ChartInterpretationInput\|client_interpretation_projection_v1\|llm_astrology_input" backend/app/services/llm_generation/natal backend/app/domain/llm backend/tests/llm_orchestration` | PASS | `backend/app/services/llm_generation/natal`, `backend/app/domain/llm`, `backend/tests/llm_orchestration` | Modern projection injection | Does not search astrology domain builders already covered by CS-326. |
| E-021 | source_inspection | `Get-Content backend/app/domain/llm/prompting/catalog.py` | PASS | `backend/app/domain/llm/prompting/catalog.py:98-145,196-208` | Runtime catalog and fallback configs | Catalog is one source among assembly DB/runtime. |
| E-022 | source_inspection | `Get-Content backend/app/domain/llm/runtime/gateway.py` | PASS | `backend/app/domain/llm/runtime/gateway.py:1603-1642` | Legacy fallback behavior | Output fallback, not input-schema fallback. |
| E-023 | source_inspection | `Get-Content backend/app/domain/llm/configuration/assembly_resolver.py` | PASS | `backend/app/domain/llm/configuration/assembly_resolver.py:117-150,221-260` | Assembly preview and resolution | Preview mock does not prove runtime payload completeness. |
| E-024 | source_inspection | `Get-Content` mandatory entrypoint files | PASS | `backend/app/domain/llm/configuration/assemblies.py`, `assembly_registry.py`, `prompt_versions.py`, `prompt_version_lookup.py`, `input_validation.py` | Mandatory entrypoints | Some are facade entrypoints by design. |
| E-025 | worktree_scan | `git status --short -- _condamad _story_briefs backend/app backend/tests` | PASS | repository root | Worktree scope | Audit files are expected to appear after this evidence. |

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

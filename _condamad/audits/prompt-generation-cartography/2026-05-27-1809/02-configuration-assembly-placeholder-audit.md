# CS-344 - Configuration Assembly Placeholder Audit

This is the story-specific report. The full CONDAMAD companion report is in `00-audit-report.md` in the same folder.

## Executive Summary

The nominal configuration path is explicit: canonical use-case contract, assembly registry, assembly resolver, prompt renderer, placeholder governance, execution profile registry and runtime gateway. The main gap is output schema ownership split across canonical contracts, assembly IDs, fallback catalog entries, bootstrap schemas and tests. Seeds are provisioning inputs, not runtime truth. Bounded fallbacks are present and separated from nominal runtime.

## Text Diagram Of Configuration Resolution

```text
use_case contract
  -> canonical_use_case_registry.py
  -> required_prompt_placeholders + input_schema + output_schema_name
  -> use_cases_seed.py provisions DB rows

request feature/subfeature/plan/locale
  -> gateway._resolve_plan
  -> AssemblyRegistry.get_active_config_sync
  -> resolve_assembly
  -> assemble_developer_prompt
  -> gateway render_vars
  -> PromptRenderer.render
  -> gateway._resolve_schema
```

## Registry Matrix

| owner | source de donnees | sortie | garde | test |
|---|---|---|---|---|
| `canonical_use_case_registry.py` | `CANONICAL_USE_CASE_CONTRACTS` | use cases, placeholders, schemas | Pydantic contracts | E-005, E-008 |
| `assembly_registry.py` | active snapshot or DB assemblies | selected assembly | taxonomy and published status | E-006, E-009 |
| `assembly_resolver.py` | assembly ORM relationships | resolved prompt blocks | plan rules, policy, budget | E-006 |
| `prompt_governance_registry.json` | JSON registry | placeholder families | Pydantic load validation | E-007 |
| `prompt_renderer.py` | prompt template + render vars | rendered developer prompt | allowlist and required checks | E-007, E-014 |
| `execution_profile_registry.py` | snapshot or DB profile | model/tokens/timeout | published status and cache | E-006 |
| `catalog.py` | fallback catalog | bounded fallback schemas/prompts | non-nominal fallback only | E-010 |
| `gateway.py` | request/context/config | resolved execution plan | mandatory assembly and fallback governance | E-011 |
| `backend/app/ops/llm/bootstrap/**` | seed data | provisioning rows | idempotent seed logic | E-013 |

## Developer Prompt Block Matrix

| Block | Owner | Source data | Output | Guard | Test |
|---|---|---|---|---|---|
| feature | `assembly_resolver.resolve_assembly` | `config.feature_template.developer_prompt` | first developer prompt block | `config.is_feature_template_enabled()` | E-006, E-014 |
| subfeature | `assembly_resolver.resolve_assembly` | `config.subfeature_template.developer_prompt` | optional second prompt block | `config.is_subfeature_template_enabled()` | E-006 |
| persona | `resolve_assembly` / gateway | `config.persona`, `compose_persona_block` | `persona_block`, not appended by `assemble_developer_prompt` | `config.is_persona_enabled()` | E-006, E-016 |
| plan rules | `PLAN_RULES_REGISTRY` | `plan_rules_ref` | subscription or daily narration instruction block | `validate_plan_rules_content` warning | E-006, E-016 |
| hard policy | `get_hard_policy("astrology")` | runtime hard-policy registry | policy layer in preview/resolved assembly | hard policy kept separate from prompt block in preview | E-006 |
| length budget | `LengthBudgetInjector` | `config.length_budget` | `[CONSIGNE DE LONGUEUR]` and token source | `LengthBudget` model and gateway token source | E-006, E-014 |
| context quality | `ContextQualityInjector` / `PromptRenderer` | `qualified_ctx.context_quality`, `{{#context_quality:*}}` blocks | degraded-context instructions or selected conditional block | conditional block regex and injector handled flag | E-007, E-014 |

## Placeholder Families

| Family | Declared owner | Allowed variables | Validation or replacement path | Runtime consumer |
|---|---|---|---|---|
| `natal` | `prompt_governance_registry.json` | `locale`, `use_case`, `llm_astrology_input_v1`, `birth_date`, `birth_time`, `birth_timezone`; universal `persona_name` | `PromptRenderer.render` checks required values and `PLACEHOLDER_POLICY` blocks unresolved required natal placeholders | `LLMGateway._resolve_plan` and renderer |
| `guidance` | `prompt_governance_registry.json` | `locale`, `use_case`, `situation`, `objective`, `time_horizon`, `natal_chart_summary`, `context_lines`, `current_datetime`, `chart_json`, `event_description`, `last_user_msg` | required `situation`, optional fields, and `locale` fallback `fr-FR` | guidance gateway path |
| `chat` | `prompt_governance_registry.json` | `locale`, `use_case`, `last_user_msg`, `persona_name`, `natal_chart_summary` | required `last_user_msg`; persona is optional | chat gateway path |
| `horoscope_daily` | `prompt_governance_registry.json` | `locale`, `use_case`, `question`, `last_user_msg` | optional/fallback placeholder classification | daily narration gateway path |
| universal | `prompt_governance_registry.json` | `locale`, `use_case`, `persona_name`, `last_user_msg` | treated as optional empty when absent unless required by the family-specific list | all renderer families |

## Output Schema Owner Matrix

| Surface | Role | Source data | Runtime status | Evidence |
|---|---|---|---|---|
| `canonical_use_case_registry.py` | canonical contract declaration | `output_schema_name`, `CanonicalOutputSchemaDefinition` | source contract owner, not the final runtime resolver | E-005 |
| `assembly_registry.py` / assembly rows | nominal runtime selector | active snapshot or published DB `output_schema_id` | nominal when assembly schema is present | E-006, E-011 |
| `gateway.py` / `_resolve_schema` | runtime schema resolution | snapshot bundle, DB schema ID, fallback catalog | final runtime decision point; records F-002 split ownership risk | E-011 |
| `catalog.py` / `get_output_schema` | bounded fallback | `PROMPT_RUNTIME_DATA` output schemas | fallback only when no schema is resolved and use case is not paid | E-010, E-011 |
| `backend/app/ops/llm/bootstrap/**` | provisioning input | seed schema constants and canonical contracts | provisioning only, not loaded runtime truth | E-013 |
| `test_output_contract.py` | test guard | runtime schema fixtures and bootstrap schema import | proves fixture/schema validation but exposes F-002 split ownership | E-014, E-017 |

## `llm_astrology_input_v1` Trace

`canonical_use_case_registry.py` declares `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` and modern natal use cases require `llm_astrology_input_v1`. `prompt_governance_registry.json` also marks `llm_astrology_input_v1` required for the `natal` family. `gateway.py` overlays context into render variables, removes legacy `chart_json` and `natal_data` for natal paths, then calls `PromptRenderer.render` with configured required placeholders.

## Nominal Runtime Versus Bounded Fallback

Nominal: `AssemblyRegistry.get_active_config_sync` -> `resolve_assembly` -> `assemble_developer_prompt` -> `PromptRenderer.render` -> `_resolve_schema` from snapshot or DB schema ID.

Bounded fallback: `_resolve_fallback_use_case_config`, `catalog.build_fallback_use_case_config`, `catalog.get_output_schema`, and bootstrap no-assembly fallback in non-production blank assembly state.

Seeds/bootstrap: `use_cases_seed.py`, `seed_66_20_taxonomy.py`, `seed_29_prompts.py`, `seed_30_8_v3_prompts.py`, `seed_guidance_prompts.py`, `seed_horoscope_narrator_assembly.py`. These are provisioning inputs, not loaded runtime truth.

## Tests And Gaps

| Test | Proves | Gap |
|---|---|---|
| `test_prompt_resolution.py` | placeholders, context quality, length budget, paid schema path | writes `evaluation_report.md`, so skipped for no-delta audit validation |
| `test_differentiation.py` | plan and persona differentiation | does not prove schema ownership convergence |
| `test_output_contract.py` | fixture/schema validation | imports bootstrap schema for natal premium |
| `test_config_coherence_validator.py` | coherence validator exists | not run in this audit |

## Findings

- F-002: output schema ownership remains split and needs a bounded convergence story.
- F-003: prompt-resolution evaluation should have a non-mutating guard mode.

## Review Alignment Note

This story-specific report intentionally mirrors the required CS-344 contract shape:
diagram, registry matrix, prompt block matrix, placeholder family matrix,
output schema owner matrix, nominal-versus-fallback separation, seed/bootstrap
classification, test map and coverage gaps. The companion files in the same
folder carry the CONDAMAD evidence log, finding register, story candidates, risk
matrix and executive summary.

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

| Block | Owner | Classification |
|---|---|---|
| feature | `assembly_resolver.resolve_assembly` | feature block from feature template |
| subfeature | `assembly_resolver.resolve_assembly` | optional subfeature block |
| persona | `resolve_assembly` / gateway | persona block, not appended by `assemble_developer_prompt` |
| plan rules | `PLAN_RULES_REGISTRY` | subscription or daily narration instruction block |
| hard policy | `get_hard_policy("astrology")` | policy layer, visible in preview/resolved assembly |
| length budget | `LengthBudgetInjector` | injected length constraint and token source |
| context quality | `ContextQualityInjector` / `PromptRenderer` | degraded-context or conditional block handling |

## Placeholder Families

| Family | Declared owner | Runtime consumer |
|---|---|---|
| `natal` | `prompt_governance_registry.json`; required `llm_astrology_input_v1` | `PromptRenderer.render` via gateway |
| `guidance` | `prompt_governance_registry.json`; `situation`, `objective`, `natal_chart_summary` | guidance gateway path |
| `chat` | `prompt_governance_registry.json`; required `last_user_msg` | chat gateway path |
| `horoscope_daily` | `prompt_governance_registry.json`; `question` optional | daily narration gateway path |
| universal | `locale`, `use_case`, `persona_name`, `last_user_msg` | all families |

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


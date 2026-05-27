# Configuration Assembly Placeholder Audit - CS-344

## Domain Closure Status

Status: `open`.

The audited domain is backend LLM configuration assembly and placeholder resolution. The audit is read-only and covers use-case contracts, assembly resolution, prompt rendering, placeholder governance, execution profile resolution, output schema resolution, bounded fallbacks, bootstrap provisioning, and existing evaluation tests.

## Prior Audit And Story History Consulted

| Source | Classification | Current disposition | Evidence |
|---|---|---|---|
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | prior same-domain audit | still-active for CS-344 subset | E-002 |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/02-finding-register.md` F-002 | prior finding | still-active, narrowed to configuration/schema/fallback owners | E-002 |
| `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` | prior story | consulted, no code implementation to close CS-344 | E-003 |
| `_condamad/stories/regression-guardrails.md` RG-002/RG-022 | guardrails | applicable as boundary and prompt-validation-path guards | E-004 |

## Scope

In scope: `backend/app/domain/llm/configuration/**`, `backend/app/domain/llm/prompting/prompt_renderer.py`, `backend/app/domain/llm/prompting/placeholder_policy.py`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/domain/llm/governance/prompt_governance_registry.py`, `backend/app/domain/llm/governance/data/prompt_governance_registry.json`, selected `backend/app/domain/llm/runtime/gateway.py` schema/render paths, `backend/app/ops/llm/bootstrap/**`, and `backend/tests/evaluation/**`.

Out of scope: provider handoff internals, frontend, API behavior, migrations, runtime refactor, prompt text rewrite, seed execution, and guardrail registry enrichment.

## Closure Analysis

Active findings after this audit:

- F-002 remains open because output schema ownership is split across canonical contracts, assembly UUIDs, fallback catalog schemas, and test/seed schema imports.
- F-003 remains open because one evaluation test proves prompt resolution but writes `backend/tests/evaluation/evaluation_report.md`, making it unsuitable as a no-delta validation guard for read-only audits.

Closed or bounded findings:

- CS-343 F-002 is closed for the CS-344 classification slice covering seed/bootstrap versus runtime ownership. Seeds are classified as provisioning inputs and not runtime source of truth in this audit. Remaining provider handoff context is deferred to CS-345.

Deferred non-domain context:

- Provider fallback execution, provider response repair, and final handoff are CS-345.
- `llm_astrology_input_v1` source completeness beyond configuration tracing is CS-346.
- Persistence/audit hash/output observability details are CS-347.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` / `CANONICAL_USE_CASE_CONTRACTS` | used | E-005, E-008 | Canonical owner for use-case contract, required placeholders, input schema, and output schema name declarations. | Runtime DB rows not queried. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` / `list_modern_natal_use_case_contracts` | used | E-005, E-008 | Differentiates modern natal contracts requiring `llm_astrology_input_v1`. | Source inspection only. |
| `backend/app/domain/llm/configuration/assembly_registry.py` / `AssemblyRegistry.get_active_config_sync` | used | E-006, E-009 | Nominal runtime owner for active assembly resolution by feature/subfeature/plan/locale. | Runtime DB not executed. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` / `resolve_assembly` | used | E-006, E-009 | Resolves feature, subfeature, persona, plan rules, hard policy, length budget and context quality metadata. | Prompt text not copied. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` / `assemble_developer_prompt` | used | E-006, E-009 | Concatenates feature, subfeature and plan rules, then injects length budget and context quality. | Source path only. |
| `backend/app/domain/llm/configuration/assemblies.py` | intentional-public-export | E-006 | Public entrypoint re-exporting assembly admin, registry and resolver APIs. | No external package consumer was scanned. |
| `backend/app/domain/llm/configuration/active_release.py` / `get_active_release_id` | used | E-006 | Separates active release lookup to avoid circular imports. | Not directly exercised by targeted tests. |
| `backend/app/domain/llm/configuration/execution_profile_registry.py` | used | E-006, E-009 | Runtime owner for profile waterfall, snapshot bundle profile resolution, and profile cache. | Runtime DB not executed. |
| `backend/app/domain/llm/configuration/execution_profiles.py` | intentional-public-export | E-006 | Canonical package entrypoint for `ExecutionProfileRegistry`. | No external package consumer was scanned. |
| `backend/app/domain/llm/configuration/config_coherence_validator.py` | used | E-012 | Coherence owner for execution profile, output contract, placeholders, persona, plan rules and length budget validation. | Validator code was scanned, not run directly. |
| `backend/app/domain/llm/governance/prompt_governance_registry.py` | used | E-007, E-009 | Runtime facade loading placeholder families, aliases, universal placeholders and governed exceptions from JSON. | No JSON mutation performed. |
| `backend/app/domain/llm/governance/data/prompt_governance_registry.json` | used | E-007 | Source data for placeholder families and aliases: chat, guidance, natal and horoscope_daily. | Registry schema load tested indirectly only. |
| `backend/app/domain/llm/prompting/placeholder_policy.py` | used | E-007 | Defines blocking placeholder policy for natal and guidance_contextual families. | Policy is small and source-only. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer.render` | used | E-007, E-009 | Runtime placeholder renderer and context-quality conditional block resolver. | No live rendering command run. |
| `backend/app/domain/llm/prompting/catalog.py` / `PROMPT_RUNTIME_DATA` | used | E-010 | Bounded fallback owner for runtime metadata and output schema fallback outside nominal assembly. | This is a fallback owner, not nominal source of truth. |
| `backend/app/domain/llm/prompting/catalog.py` / `PROMPT_FALLBACK_CONFIGS` | used | E-010 | Test-only/bounded fallback prompt configs exist only for `test_natal` and `test_guidance`. | Provider handoff fallback audit deferred to CS-345. |
| `backend/app/domain/llm/runtime/gateway.py` / `_resolve_plan` | used | E-009, E-011 | Runtime consumer of assembly registry, resolver, profile, schema, context and renderer. | Only selected paths inspected. |
| `backend/app/domain/llm/runtime/gateway.py` / `_resolve_schema` | used | E-011 | Runtime schema resolution from snapshot bundle, DB schema ID, and bounded catalog fallback. | Live DB path not executed. |
| `backend/app/ops/llm/bootstrap/use_cases_seed.py` | used | E-013 | Provisioning input that seeds persisted use-case contracts from canonical registry. | Not runtime source of truth. |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | used | E-013 | Provisioning input for assemblies, schemas and profiles from canonical contracts. | Seed not executed. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | needs-user-decision | E-013 | Historical/bootstrap prompt carrier still contains natal prompt text and required placeholders. Decide retain, migrate, or delete after config convergence. | Deletion cannot be proven from static scan alone. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | used | E-013 | Provisioning input for V3 natal prompt material and lint placeholders. | Seed not executed. |
| `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` | used | E-013 | Provisioning input for guidance use-case prompts and placeholders. | Seed not executed. |
| `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` | used | E-013 | Provisioning input for horoscope_daily assemblies, plan rules and narrator schema. | Seed not executed. |
| `backend/tests/evaluation/test_prompt_resolution.py` | test-only | E-014 | Evaluation test proving placeholder removal, context quality, length budget and schema path, but it writes a report file. | Not run to preserve backend/tests no-delta. |
| `backend/tests/evaluation/test_differentiation.py` | test-only | E-014, E-016 | Evaluation test proving plan and persona differentiation through assembly path. | Full suite not run. |
| `backend/tests/evaluation/test_output_contract.py` | test-only | E-014, E-017 | Evaluation test proving fixture responses against runtime output schemas. | Full suite not run. |
| `backend/tests/evaluation/evaluation_matrix.yaml` | test-only | E-014 | Matrix input for prompt resolution evaluation cases. | Not parsed independently. |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/**` | test-only | E-002 | Prior audit evidence for closure ledger. | Historical audit only. |

## Text Diagram

```text
canonical_use_case_registry.py
  -> declares use_case key, input_schema, output_schema_name,
     persona_strategy, fallback_target_key, required_prompt_placeholders
  -> use_cases_seed.py provisions persisted use-case rows

runtime request: feature/subfeature/plan/locale/use_case
  -> LLMGateway._resolve_plan
  -> AssemblyRegistry.get_active_config_sync
     -> active release snapshot manifest when present
     -> otherwise published PromptAssemblyConfigModel waterfall
  -> assembly_resolver.resolve_assembly
     -> feature template + optional subfeature template
     -> optional persona block
     -> plan rules from PLAN_RULES_REGISTRY
     -> hard policy via get_hard_policy("astrology")
     -> length_budget and context_quality metadata
  -> assembly_resolver.assemble_developer_prompt
     -> feature + subfeature + plan_rules
     -> LengthBudgetInjector
     -> ContextQualityInjector
  -> LLMGateway render_vars
     -> context_dict overlays user input
     -> natal paths remove chart_json/natal_data
     -> persona_name defaulted when needed
     -> context_quality injected as render variable
  -> PromptRenderer.render
     -> context_quality conditional blocks
     -> placeholder family from prompt_governance_registry.json
     -> PLACEHOLDER_ALLOWLIST + universal placeholders
     -> required placeholders fail under blocking families
  -> LLMGateway._resolve_schema
     -> snapshot schema bundle
     -> DB output_schema_id
     -> bounded catalog fallback for non-paid use cases
```

## Registry Matrix

| owner | source de donnees | sortie | garde | test |
|---|---|---|---|---|
| `canonical_use_case_registry.py` | `CANONICAL_USE_CASE_CONTRACTS` | use-case keys, required placeholders, `llm_astrology_input_v1` input schema, output schema names | Pydantic models, `list_modern_natal_use_case_contracts` | E-005, E-008 |
| `assembly_registry.py` | active release snapshot or published DB assemblies | selected `PromptAssemblyConfigModel` | feature taxonomy normalization, cache keyed by snapshot | E-006, E-009 |
| `assembly_resolver.py` | assembly ORM relationships and config fields | `ResolvedAssembly`, developer prompt blocks | plan rule validation, hard policy, length budget model | E-006, E-009 |
| `prompt_governance_registry.py` | `prompt_governance_registry.json` | placeholder family defs, aliases, universal placeholders | Pydantic registry schema and exception scope validation | E-007 |
| `placeholder_policy.py` | `PlaceholderPolicy.blocking_features` | runtime blocking families | `PromptRenderer.render` raises on required unresolved placeholders | E-007 |
| `prompt_renderer.py` | developer prompt + render vars | rendered developer prompt | strict placeholder regex, allowlist, required/optional/fallback handling | E-007, E-014 |
| `execution_profile_registry.py` | active snapshot bundle or published DB profile | model, tokens, timeout, reasoning/verbosity profile | feature taxonomy normalization and published status filter | E-006, E-009 |
| `catalog.py` | `PROMPT_RUNTIME_DATA`, `PROMPT_FALLBACK_CONFIGS` | bounded fallback metadata and schemas | only catalog lookup; not nominal assembly owner | E-010 |
| `gateway.py` | request, context, assembly, profile, schema | resolved execution plan and rendered prompt | supported-family mandatory assembly guard, fallback governance, schema guard | E-009, E-011 |
| `backend/app/ops/llm/bootstrap/**` | seed constants and canonical contracts | persisted prompts, use cases, personas, schemas, assemblies, profiles | idempotent seed logic and startup-local auto-heal | E-013 |

## Developer Prompt Block Matrix

| Block | Owner | Source data | Output | Guard | Test |
|---|---|---|---|---|---|
| feature | `assembly_resolver.resolve_assembly` | `config.feature_template.developer_prompt` | first developer prompt block | `config.is_feature_template_enabled()` | E-006, E-014 |
| subfeature | `assembly_resolver.resolve_assembly` | `config.subfeature_template.developer_prompt` | optional second block | `config.is_subfeature_template_enabled()` | E-006 |
| persona | `assembly_resolver.resolve_assembly` and gateway context | `config.persona`, `compose_persona_block` | `persona_block`, not appended by `assemble_developer_prompt` | `config.is_persona_enabled()` | E-006, E-016 |
| plan rules | `PLAN_RULES_REGISTRY` | `plan_rules_ref` | subscription/daily plan instructions | `validate_plan_rules_content` warning | E-006, E-016 |
| hard policy | `get_hard_policy("astrology")` | runtime policy registry | policy layer in preview/resolved assembly | hard policy kept separate from prompt block in preview | E-006 |
| length budget | `LengthBudgetInjector` via `assemble_developer_prompt` | `config.length_budget` | `[CONSIGNE DE LONGUEUR]` and token source | `LengthBudget` model, gateway token source | E-006, E-014 |
| context quality | `ContextQualityInjector` and `PromptRenderer` | `qualified_ctx.context_quality`, `{{#context_quality:*}}` blocks | degraded-context instructions or selected template block | conditional block regex and injector handled flag | E-007, E-014 |

## Placeholder Families And Allowed Variables

| Family | Declared owner | Allowed variables | Validation or replacement path | Runtime consumer |
|---|---|---|---|---|
| `natal` | `prompt_governance_registry.json` | `locale`, `use_case`, `llm_astrology_input_v1`, `birth_date`, `birth_time`, `birth_timezone`; universal `persona_name` | `PromptRenderer.render` checks required values and `PLACEHOLDER_POLICY` blocks natal unresolved required placeholders | `LLMGateway._resolve_plan` and renderer |
| `guidance` | `prompt_governance_registry.json` | `locale`, `use_case`, `situation`, `objective`, `time_horizon`, `natal_chart_summary`, `context_lines`, `current_datetime`, `chart_json`, `event_description`, `last_user_msg` | required `situation`, optional fields, `locale` fallback `fr-FR` | `GuidanceService` through gateway configuration |
| `chat` | `prompt_governance_registry.json` | `locale`, `use_case`, `last_user_msg`, `persona_name`, `natal_chart_summary` | required `last_user_msg`; persona optional | chat gateway path |
| `horoscope_daily` | `prompt_governance_registry.json` | `locale`, `use_case`, `question`, `last_user_msg` | optional/fallback classification | daily narration gateway path |
| universal | `prompt_governance_registry.json` | `locale`, `use_case`, `persona_name`, `last_user_msg` | treated as optional empty when absent unless required by legacy list | all renderer families |

## `llm_astrology_input_v1` Trace

| Step | Owner | Evidence |
|---|---|---|
| Contract declaration | `canonical_use_case_registry.py` declares `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` and modern natal required placeholders. | E-005, E-008 |
| Runtime request payload | `gateway.py` imports `LLMAstrologyInputV1` and uses `LLM_ASTROLOGY_INPUT_V1_KEY`. | E-011 |
| Assembly prompt resolution | `assembly_resolver.py` builds developer prompt, gateway derives `required_prompt_placeholders` from rendered assembly placeholders. | E-006, E-011 |
| Placeholder validation | `prompt_governance_registry.json` declares `llm_astrology_input_v1` required for `natal`; renderer enforces family policy. | E-007 |
| Render variables | `gateway.py` overlays context into `render_vars`, removes `chart_json` and `natal_data` for natal paths, and calls `PromptRenderer.render`. | E-011 |

## Bounded Fallback Paths

Nominal runtime:

- `AssemblyRegistry.get_active_config_sync` resolves active assembly by feature/subfeature/plan/locale.
- `resolve_assembly` and `assemble_developer_prompt` produce the developer prompt.
- `_resolve_schema` uses snapshot bundle schema or DB `output_schema_id`.

Bounded fallback paths:

- `_allows_nominal_bootstrap_fallback` only allows no-assembly fallback for non-production blank assembly tables.
- `_resolve_fallback_use_case_config` uses DB prompt or `build_fallback_use_case_config` outside nominal assembly flow.
- `_resolve_schema` falls back to `catalog.get_output_schema` only when no schema is resolved and the use case is not paid.
- `PROMPT_FALLBACK_CONFIGS` contains only synthetic `test_natal` and `test_guidance` prompt configs.

Seeds/bootstrap:

- `use_cases_seed.py`, `seed_66_20_taxonomy.py`, `seed_29_prompts.py`, `seed_30_8_v3_prompts.py`, `seed_guidance_prompts.py`, and `seed_horoscope_narrator_assembly.py` are provisioning inputs.
- They must not be used as proof of current loaded runtime state without DB/source-trace evidence.

## Existing Tests And Coverage Gaps

| Test surface | Proves | Does not prove | Evidence |
|---|---|---|---|
| `backend/tests/evaluation/test_prompt_resolution.py` | Placeholder absence, context quality handling, length budget propagation, paid natal schema path. | Non-mutating validation: it writes `evaluation_report.md`. | E-014 |
| `backend/tests/evaluation/test_differentiation.py` | Plan rules and persona differentiation through assembly path. | Full prompt registry coherence or output schema convergence. | E-014, E-016 |
| `backend/tests/evaluation/test_output_contract.py` | Fixture responses validate against runtime schema choices. | Runtime assembly schema ID convergence; it imports bootstrap schema for natal premium. | E-014, E-017 |
| `backend/tests/llm_orchestration/test_config_coherence_validator.py` | Coherence validator exists for config contracts. | Not run in this audit. | E-012 |

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: schema ownership is not fully DRY. `CanonicalOutputSchemaDefinition`, `catalog.py` fallback schemas, bootstrap schemas, DB `output_schema_id`, and tests all carry schema knowledge. F-002 tracks this.
- No Legacy: bounded fallbacks are present and classified separately from nominal runtime. No code change or new fallback was introduced.
- Mono-domain: configuration assembly ownership remains under `backend/app/domain/llm/configuration` and rendering under `backend/app/domain/llm/prompting`.
- Dependency direction: the audited domain imports infra DB models for runtime resolution, but no API dependency was introduced by this audit. No code files changed.

## Exhaustive Active Finding Surfaces

F-002 implementation surfaces:

- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/config_coherence_validator.py`
- `backend/app/ops/llm/bootstrap/use_cases_seed.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`
- `backend/tests/evaluation/test_output_contract.py`
- `backend/tests/llm_orchestration/test_config_coherence_validator.py`

F-003 implementation/test surfaces:

- `backend/tests/evaluation/test_prompt_resolution.py`
- `backend/tests/evaluation/report_generator.py`
- `backend/tests/evaluation/evaluation_report.md`

Application files changed by this audit: none.

Governance/test files changed by this audit: none.


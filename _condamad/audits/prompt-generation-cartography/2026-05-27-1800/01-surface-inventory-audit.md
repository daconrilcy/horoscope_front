# Surface Inventory Audit - CS-343 Prompt Generation Cartography

## Executive Summary

This audit inventories backend LLM prompt-generation surfaces without changing runtime behavior. The active modern natal path is now centered on `llm_astrology_input_v1`, with prompt-visible blocks separated from validation-only, audit-only and runtime-only carriers. Configuration, bootstrap, router, persistence, test and CONDAMAD archival surfaces remain classified instead of being merged into prompt material.

## Inspected Surface Table

| file path | owner | symbol or function | role | status | boundary | producer | consumer | evidence | gap or dependency marker |
|---|---|---|---|---|---|---|---|---|---|
| `backend/app/domain/llm/runtime/gateway.py` | LLM runtime gateway | `LLMGateway._resolve_plan`, `_build_messages`, `_call_provider`, `execute_request` | plan resolution, message composition, provider handoff | active runtime | prompt-visible | assembly/config/user input | provider runtime manager | E-005, E-006, E-007 | CS-345 provider handoff audit |
| `backend/app/domain/llm/runtime/gateway.py` | LLM runtime gateway | `build_user_payload` | user payload composition | active runtime | prompt-visible | request context | provider user message | E-005, E-007 | CS-345 payload handoff audit |
| `backend/app/domain/llm/runtime/gateway.py` | LLM runtime gateway | `_prompt_visible_llm_astrology_input` | prompt block filtering | active runtime | prompt-visible | `llm_astrology_input_v1` | rendered payload | E-005, E-007 | CS-345/CS-346 boundary proof |
| `backend/app/domain/llm/runtime/gateway.py` | LLM runtime gateway | `_without_prompt_excluded_keys` | audit key redaction before handoff | active runtime | audit-only | rich input | provider payload | E-005, E-007 | CS-345 audit-only proof |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | LLM configuration | `CanonicalUseCaseContract`, `list_canonical_use_case_contracts`, `list_modern_natal_use_case_contracts` | use-case selection and placeholder contract | active configuration | runtime-only | source registry | seeds/gateway/admin | E-005, E-006, E-012 | CS-344 configuration audit |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | LLM configuration | `resolve_assembly`, `assemble_developer_prompt`, `build_assembly_preview` | assembly resolution and developer prompt assembly | active configuration | prompt-visible | DB assembly/prompt/persona | gateway/admin preview | E-005, E-006 | CS-344 assembly audit |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | LLM prompting | `PromptRenderer.render`, `extract_placeholders` | placeholder rendering | active runtime | prompt-visible | developer prompt and variables | gateway/admin preview | E-005, E-006, E-007 | CS-344 placeholder audit |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Astrology interpretation | `LLMAstrologyInputV1Builder.build` | rich natal LLM input assembly | active runtime | prompt-visible | facts/signals/limits/shaping | natal service/gateway | E-005, E-006, E-007 | CS-346 input source audit |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Astrology interpretation | `_evidence_block`, `_provenance_block`, `build_llm_input_hash_material` | evidence and hash material separation | active runtime | validation-only | evidence refs/projection hash | audit/persistence | E-005, E-006, E-007 | CS-347 validation persistence audit |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | Natal generation service | `_build_llm_astrology_input_v1`, `interpret`, `_generate_free_short` | natal generation orchestration | active runtime | runtime-only | chart result and interpretation builders | AIEngineAdapter/gateway | E-005, E-006, E-007 | CS-346 source completeness audit |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | Natal generation service | `_apply_narrative_answer_audit`, `_llm_input_hash_for_audit`, `_evidence_refs_for_audit` | audit persistence enrichment | observability/audit | audit-only | gateway result and rich input | persistence model | E-005, E-010 | CS-347 audit persistence audit |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | Guidance generation service | `GuidanceService.generate_*`, adapter calls | guidance prompt orchestration | active runtime | prompt-visible | prompt context and user request | AIEngineAdapter/gateway | E-004, E-005 | CS-345 non-natal runtime comparison |
| `backend/app/services/llm_generation/chat/public_chat.py` | Chat generation service | public chat helpers | chat trigger and quota orchestration | active runtime | runtime-only | chat request | chat guidance service | E-004, E-011 | CS-345 chat handoff if needed |
| `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | Daily narration service | `generate_horoscope_narration_via_gateway` | daily narration gateway path | active runtime | prompt-visible | prediction prompt context | LLMGateway | E-004, E-005 | CS-345 daily handoff audit |
| `backend/app/services/llm_generation/shared/natal_context.py` | Shared prompt context | `build_natal_chart_summary`, `build_chat_natal_hint` | textual prompt context for guidance/chat | active runtime | prompt-visible | natal profile/chart summaries | guidance/chat services | E-004, E-005 | CS-346 non-rich input comparison |
| `backend/app/ops/llm/bootstrap/use_cases_seed.py` | LLM bootstrap | `seed_use_cases`, `validate_use_case_seed_contracts` | persisted use-case config seed | bootstrap/seed | runtime-only | canonical registry | database seed | E-012 | CS-344 config seed parity |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | LLM bootstrap | prompt seed constants and `seed_prompts` | historical prompt seed carrier | debt | prompt-visible | static prompt constants | database seed | E-010, E-012 | CS-344 decide retained bootstrap role |
| `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` | LLM bootstrap | `seed_guidance_prompts` | guidance prompt seed carrier | bootstrap/seed | prompt-visible | static prompt constants | database seed | E-010, E-012 | CS-344 config prompt audit |
| `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` | LLM bootstrap | `seed_horoscope_narrator_assembly` | daily narration assembly seed and legacy cleanup | bootstrap/seed | prompt-visible | assembly prompt constants | database seed | E-010, E-012 | CS-344/CS-345 daily prompt audit |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | LLM bootstrap | `seed_66_20_taxonomy` | assembly/profile taxonomy seed | bootstrap/seed | runtime-only | canonical contracts | database seed | E-012 | CS-344 profile/assembly audit |
| `backend/app/infra/db/models/llm/**` | LLM persistence models | prompt, use-case, assembly, persona, observability models | storage contract carriers | active configuration | runtime-only | migrations/runtime services | DB/session | E-012 | CS-347 persistence audit |
| `backend/migrations/versions/*llm*` | Alembic history | prompt/persona/assembly/provider/audit migrations | schema history | historical | audit-only | migration files | database history | E-012 | CS-347 historical schema context |
| `backend/app/api/v1/routers/admin/llm/**` | Admin API routers | prompt, assembly, release, sample payload, observability endpoints | admin exposure and manual execution | active runtime | runtime-only | HTTP requests | services/domain owners | E-011 | CS-344/CS-347 API exposure context |
| `backend/app/api/v1/routers/internal/llm/qa.py` | Internal QA router | QA seed and LLM QA endpoints | internal execution trigger | active runtime | runtime-only | HTTP QA request | services | E-011 | CS-347 QA audit context |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | Public API router | natal interpretation endpoints | public natal generation trigger | active runtime | runtime-only | HTTP request | natal service | E-011 | CS-346/CS-347 public trigger context |
| `backend/app/api/v1/routers/public/guidance.py` | Public API router | guidance endpoints | public guidance trigger | active runtime | runtime-only | HTTP request | guidance service | E-011 | CS-345 non-natal context |
| `backend/app/api/v1/routers/public/chat.py` | Public API router | chat endpoints | public chat trigger | active runtime | runtime-only | HTTP request | chat services | E-011 | CS-345 chat context |
| `backend/app/api/v1/routers/public/consultations.py` | Public API router | consultation generation endpoint | public consultation trigger | active runtime | runtime-only | HTTP request | consultation generation service | E-011 | CS-345 guidance-contextual context |
| `backend/app/api/v1/routers/public/predictions.py` | Public API router | daily prediction LLM narrative trigger | active runtime | runtime-only | HTTP request | daily prediction/narration path | E-011 | CS-345 daily context |
| `backend/tests/architecture/test_llm_astrology_input_*.py` | Backend tests | architecture tests | prompt/audit/runtime boundary guards | test guard | validation-only | source tree | pytest | E-004, E-007 | keep in CS-344 to CS-347 validation |
| `backend/tests/llm_orchestration/**` | Backend tests | gateway, renderer, assembly and prompt tests | orchestration guards | test guard | validation-only | source tree | pytest | E-004, E-007 | keep in CS-344 to CS-347 validation |
| `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py` | Backend tests | natal rich input tests | legacy carrier extinction guard | test guard | validation-only | source tree | pytest | E-004, E-007 | keep in CS-346 validation |
| `_condamad/**`, `_story_briefs/**` prompt/evidence hits | CONDAMAD artifacts | audit/story text | historical context and evidence archive | historical | audit-only | prior audits/stories | auditors/story writers | E-003, E-010 | do not classify text hits as runtime influence |

## Surface Status Summary

| status | surfaces |
|---|---|
| active runtime | gateway, natal/guidance/chat/daily services, public/internal routers |
| active configuration | canonical registry, assembly resolver, DB model contracts |
| test guard | architecture, LLM orchestration and unit guards |
| bootstrap/seed | use-case, prompt, guidance, daily narration and taxonomy seed files |
| observability/audit | natal answer audit helpers and LLM observability/persistence carriers |
| historical | Alembic migrations and CONDAMAD/story archives |
| debt | retained prompt seed/history carriers and legacy text occurrences requiring bounded follow-up |

## Boundary Summary

| boundary | Included surfaces | Excluded from prompt material |
|---|---|---|
| prompt-visible | rendered developer prompts, filtered `llm_astrology_input_v1` blocks, selected context summaries | audit-only provenance, provider response, persisted answer |
| validation-only | evidence refs validation, test guards, output validation paths | final prompt text and provider messages |
| audit-only | hashes, grounding status, prompt refs, persistence audit fields, CONDAMAD archives | provider prompt payload |
| runtime-only | route triggers, use-case selection, profile/provider metadata, DB model carriers | user-visible prompt text unless passed into renderer/payload |

## Gaps And Dependencies For CS-344 To CS-350

| Follow-up | Question or dependency |
|---|---|
| CS-344 | Which persisted assemblies/prompts and bootstrap seeds are canonical, retained only for bootstrap, or debt? |
| CS-345 | Which gateway provider fallback branches remain nominal, non-nominal tolerated behavior, or debt requiring removal? |
| CS-346 | Does every natal prompt-visible block in `llm_astrology_input_v1` have complete source ownership and tests? |
| CS-347 | Are output validation, persistence hashes, prompt refs and provider fields complete without reintroducing prompt-visible evidence? |
| CS-348 | Which owner diagram should become the architecture source of truth after CS-344 to CS-347 close their details? |
| CS-349 | Which classified debts are accepted risks, resolved findings or follow-up stories in the final report? |
| CS-350 | Which surfaces and dependencies must be rendered in Mermaid without showing archival text hits as active flows? |

## Runtime Delta Check

`git status --short -- backend/app backend/tests backend/migrations frontend/src` returned no entries after evidence collection. This audit did not modify application, test, migration or frontend source files.

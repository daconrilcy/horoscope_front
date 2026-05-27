# Audit Report - prompt-generation-cartography - 2026-05-27-1800

## Domain Closure Status

Status: closed for CS-343 inventory delivery.

No application implementation story remains inside the CS-343 audited domain. Residual implementation questions are deferred non-domain context for CS-344 to CS-350 and must use this inventory as baseline.

## Prior Audit And Story History Consulted

| Source | Classification | Evidence | Current status |
|---|---|---|---|
| `_condamad/audits/prompt-generation/2026-05-02-1452` | same-domain history | E-003 | Prior fallback findings remain context; CS-343 only maps surfaces. |
| `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | adjacent LLM input context | E-003 | Still relevant for `chart_json` and modern input ownership. |
| `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000` | adjacent prompt pipeline context | E-003 | Superseded by current runtime after CS-330 to CS-342 for `llm_astrology_input_v1` presence. |
| `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000` | adjacent configuration context | E-003 | Follow-up details belong to CS-344. |
| `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000` | adjacent input readiness context | E-003 | Modern input source selection remains relevant for CS-346. |
| `_condamad/stories/regression-guardrails.md` | guardrail registry | E-002 | RG-002 and RG-022 apply; RG-016 to RG-022 remain related prompt-generation context. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/runtime/gateway.py` / `LLMGateway` | used | E-005, E-006, E-007 | Runtime owner for rendered prompt, user payload, messages, provider handoff and validation. | Live provider execution not run. |
| `backend/app/domain/llm/runtime/gateway.py` / `_prompt_visible_llm_astrology_input` | used | E-005, E-007 | Filters prompt-visible blocks for `llm_astrology_input_v1`. | Source/test evidence only. |
| `backend/app/domain/llm/runtime/gateway.py` / `_without_prompt_excluded_keys` | used | E-005, E-007 | Removes audit/provenance keys before provider handoff. | Source/test evidence only. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | used | E-005, E-006, E-012 | Canonical owner for use-case contracts and required prompt placeholders. | Configuration persistence details deferred to CS-344. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | used | E-005, E-006 | Resolves assemblies and builds developer prompts from prompt/persona/config surfaces. | Runtime DB row coverage deferred to CS-344. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer` | used | E-005, E-006, E-007 | Renders placeholders into developer prompt and extracts placeholder names. | Exact prompt text not copied into audit. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | used | E-005, E-006, E-007 | Owner for facts, signals, limits, shaping, evidence and provenance boundaries. | Source/test evidence only. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `_build_llm_astrology_input_v1` | used | E-005, E-006, E-007 | Produces modern natal LLM input before calling gateway through adapter. | Detailed field completeness deferred to CS-346. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / audit helpers | used | E-005, E-010 | Persists prompt version, provider, hashes, grounding status and evidence refs outside prompt material. | Persistence table semantics deferred to CS-347. |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | used | E-004, E-005 | Active generation service for guidance use cases using prompt context and adapter calls. | Not deeply audited beyond inventory. |
| `backend/app/services/llm_generation/chat/public_chat.py` and `chat_guidance_service.py` | used | E-004, E-011 | Public chat generation/exposure surfaces. | Chat internals deferred to follow-up if needed. |
| `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | used | E-004, E-005 | Daily horoscope narration uses gateway and assembly-owned prompt governance. | Daily prompt details deferred to CS-344/CS-345. |
| `backend/app/services/llm_generation/shared/natal_context.py` | used | E-004, E-005 | Builds text prompt context for non-natal-modern guidance/chat surfaces. | Does not prove prompt visibility for every caller. |
| `backend/app/ops/llm/bootstrap/use_cases_seed.py` | used | E-012 | Bootstrap owner for persisted use-case contract rows. | Seed execution not run. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | debt | E-010, E-012 | Historical/bootstrap prompt carrier; contains prompt text and canonical keys but is not the modern runtime owner. | Deletion not proposed by CS-343. |
| `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` | bootstrap/seed | E-010, E-012 | Guidance prompt seed carrier for persisted prompt versions. | Seed execution not run. |
| `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` | bootstrap/seed | E-010, E-012 | Canonical daily narration assembly seed and legacy cleanup carrier. | Seed execution not run. |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | bootstrap/seed | E-012 | Assembly/profile seed carrier for feature taxonomy. | Seed execution not run. |
| `backend/app/infra/db/models/llm/**` | used | E-012 | Persistence models for prompt, use-case, assembly, persona, sample payload and observability surfaces. | Model-by-model schema audit deferred to CS-347. |
| `backend/migrations/versions/*llm*`, prompt/persona/provider related migrations | historical | E-012 | Historical schema carriers for prompt registry, assembly, persona, provider and audit fields. | No migration was modified or executed. |
| `backend/app/api/v1/routers/admin/llm/**` | used | E-011 | Admin exposure for prompt, assembly, release, sample payload and observability operations. | API behavior not audited beyond route ownership. |
| `backend/app/api/v1/routers/internal/llm/qa.py` | used | E-011 | Internal QA trigger/exposure surface for LLM generation paths. | QA route behavior not executed. |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | used | E-011 | Public natal generation trigger that delegates to service. | Public API contract not changed. |
| `backend/app/api/v1/routers/public/guidance.py`, `chat.py`, `consultations.py`, `predictions.py` | used | E-011 | Public trigger/exposure surfaces for LLM generation or narration. | Per-route behavior deferred outside CS-343. |
| `backend/tests/architecture/test_llm_astrology_input_*.py` | test-only | E-004, E-007 | Guards prompt/audit/runtime boundaries for modern natal input. | Only selected architecture tests were run. |
| `backend/tests/llm_orchestration/**` prompt and gateway tests | test-only | E-004, E-007 | Guards prompt renderer, gateway, assembly and LLM orchestration behavior. | Only scoped tests were run. |
| `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py` | test-only | E-004, E-007 | Guards modern input preference over legacy carriers. | None. |
| `_condamad/**` and `_story_briefs/**` prompt/evidence occurrences | out-of-domain | E-010 | Audit/story archives explain history and must not be treated as runtime influence. | Broad scans intentionally include archival text. |

## Findings Summary

| Finding | Summary | Closure |
|---|---|---|
| F-001 | Inventory baseline is produced. | Closed for CS-343. |
| F-002 | Debt and archival carriers remain classified for bounded follow-ups. | Deferred to CS-344 to CS-350. |
| F-003 | Dependency direction remains guarded. | Closed for CS-343. |

## Deferred Non-Domain Context

- CS-344: configuration, assemblies, placeholders, prompt registry and prompt rendering details.
- CS-345: gateway, provider handoff, provider fallback and final message composition.
- CS-346: natal astrology input source completeness and mapper ownership.
- CS-347: output validation, persistence, observability and audit fields.
- CS-348 to CS-350: architecture synthesis, delivery report and Mermaid documentation.

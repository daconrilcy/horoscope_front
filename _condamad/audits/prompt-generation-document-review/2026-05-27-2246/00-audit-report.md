<!-- Commentaire global: rapport compagnon CONDAMAD pour l'audit CS-353 des processus paralleles de generation de prompts LLM. -->

# CS-353 Domain Audit Report

## Domain Closure Status

Status: `open`.

Reason: the runtime implementation was not changed, and the audit found active provider-capable prompt processes outside the modern natal `llm_astrology_input_v1` flow that need documentation and guardrail follow-up. No backend, frontend, test, migration or CS-350 source-document edit is in scope for this story.

## Audited Domain

- Domain key: `prompt-generation-document-review`
- Domain type: `condamad-audit-documentation`
- Audit archetype: custom parallel legacy prompt-generation audit, with `legacy-surface-audit`, `contract-shape-audit`, `test-guard-coverage-audit`, DRY and No Legacy dimensions.
- Explicit story deliverable: `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`
- Primary reviewed artifact: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- Runtime source surface: guidance, public chat, daily horoscope narration, fallback catalog, gateway recovery, repair prompter, admin sample/manual execution, bootstrap seeds, carrier fields and tests.
- Read-only implementation mode: yes for `backend/app/**`, `backend/tests/**`, `frontend/src/**`, migrations and `_condamad/docs/**`.

## Prior Audit And Story History Consulted

| Source | Path | Classification | Current status | Evidence |
|---|---|---|---|---|
| CS-351 adversarial document review | `_condamad/audits/prompt-generation-document-review/2026-05-27-2305/00-audit-report.md` | prior same-domain audit | still-active; document accepted with corrections, but not a parallel-process inventory | E-004 |
| CS-352 code-document concordance | `_condamad/audits/prompt-generation-document-review/2026-05-27-2240/00-audit-report.md` | prior same-domain audit | still-active; F-001/F-002 documentation-only findings remain adjacent | E-004 |
| CS-343 surface inventory | `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | source inventory | still-active; already classifies guidance, chat, horoscope, seeds and QA surfaces | E-005 |
| CS-344 configuration audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | configuration audit | still-active; seed/fallback/non-nominal separation applies | E-006 |
| CS-345 gateway handoff audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | runtime handoff audit | still-active; provider handoff and recovery classification apply | E-007 |
| CS-346 natal input audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | natal input audit | still-active for modern natal boundary and legacy carrier exclusion | E-008 |
| CS-347 output validation audit | `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | validation/persistence audit | still-active for repair, validation and audit persistence | E-009 |
| Guardrails registry | `_condamad/stories/regression-guardrails.md` | governance | RG-017 to RG-022 apply; exact parallel-process audit guardrail remains absent | E-003 |

## Closure Analysis

- Prior same-domain findings consulted: CS-351 F-001/F-002 and CS-352 F-001/F-002 remain documentation wording corrections, not active implementation findings for CS-353.
- Closed findings by current evidence: none; this audit is read-only.
- Active CS-353 findings after current evidence: F-001, F-002 and F-003.
- Complete in-domain implementation surface for active findings: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`, `_condamad/stories/regression-guardrails.md` if a future story accepts a new invariant, and focused backend guard tests only if a future story chooses executable protection.
- Application files to modify for active findings: none in this audit story.
- Governance/test files to modify for active findings: none in this audit story.
- Deferred non-domain context: product decision on `event_guidance`, admin manual execution policy, real external provider validation, and final CS-350 document amendment.

## Mandatory Audit Dimensions

| Dimension | Verdict | Evidence | Notes |
|---|---|---|---|
| DRY | PASS with documentation finding | E-001, E-002, E-004, E-018 | This audit creates one bounded report; however CS-350 does not yet contain a single explicit parallel-process matrix. |
| No Legacy | FAIL for documentation completeness, PASS for runtime non-modification | E-006, E-007, E-008, E-011, E-012 | Legacy carriers and fallback paths are classified in code/tests, but future readers can miss `event_guidance`, admin sample payloads and non-natal provider-capable flows without this report. |
| Mono-domain ownership | PASS | E-001, E-002, E-019 | All writes are audit/evidence artifacts under `_condamad/**`; runtime code remains read-only. |
| Dependency direction | PASS | E-010, E-011, E-012, E-013 | Provider-capable paths use `AIEngineAdapter` or `LLMGateway`; no new dependency edge was introduced. |
| Contract shape | PASS | E-017, E-018 | The explicit CS-353 report contains the required sections and process fields. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/00-story.md` | used | E-001 | Defines CS-353 scope, acceptance criteria and explicit deliverable path. | none |
| `_story_briefs/cs-353-audit-process-paralleles-legacy-generation-prompt-llm.md` | used | E-002 | Source brief for process families, statuses and required report shape. | none |
| `_condamad/stories/regression-guardrails.md` / RG-017 to RG-022 | used | E-003 | Existing prompt-generation guardrails consulted before findings and candidates. | no exact CS-353 parallel-process guardrail exists |
| `_condamad/audits/prompt-generation-document-review/2026-05-27-2305/00-audit-report.md` | used | E-004 | Prior same-domain adversarial audit consulted for closure ledger. | none |
| `_condamad/audits/prompt-generation-document-review/2026-05-27-2240/00-audit-report.md` | used | E-004 | Prior same-domain code-document audit consulted for closure ledger. | none |
| `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` | used | E-010 | Source document under review for omissions around parallel paths. | current workspace state only |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800/01-surface-inventory-audit.md` | used | E-005 | Source inventory for candidate prompt surfaces. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1809/02-configuration-assembly-placeholder-audit.md` | used | E-006 | Prior seed/fallback/configuration classification. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` | used | E-007 | Prior gateway provider handoff and recovery classification. | no real provider call |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md` | used | E-008 | Modern natal boundary and carrier classification. | none |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1847/05-output-validation-persistence-audit.md` | used | E-009 | Repair/validation/audit persistence classification. | none |
| `backend/app/api/v1/routers/public/guidance.py` / `/v1/guidance`, `/v1/guidance/contextual` | used | E-011 | Public authenticated trigger for guidance and contextual guidance. | no runtime HTTP request executed |
| `backend/app/services/llm_generation/guidance/guidance_service.py` / `GuidanceService.request_guidance_async`, `request_contextual_guidance_async` | used | E-011 | Guidance service owner builds prompt context and calls adapter. | source inspection only |
| `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py` / `seed_guidance_prompts` | used | E-014 | Bootstrap seed owner for guidance prompts, including legacy `chart_json` event guidance seed. | no DB seed executed |
| `backend/app/api/v1/routers/public/chat.py` / `/v1/chat` | used | E-012 | Public authenticated chat trigger. | no runtime HTTP request executed |
| `backend/app/services/llm_generation/chat/chat_guidance_service.py` / `ChatGuidanceService.send_message_async` | used | E-012 | Chat service owner builds context and calls adapter. | source inspection only |
| `backend/app/services/llm_generation/chat/public_chat.py` | used | E-012 | Public chat helper surface for quota response shape. | no independent provider handoff in this file |
| `backend/app/services/llm_generation/shared/natal_context.py` / `build_natal_chart_summary`, `build_chat_natal_hint` | used | E-012 | Shared textual natal summary carrier for guidance/chat prompt context. | source inspection only |
| `backend/app/services/llm_generation/horoscope_daily/narration_service.py` / `generate_horoscope_narration_via_gateway` | used | E-013 | Daily horoscope narration owner calls `LLMGateway.execute_request`. | source inspection only |
| `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` / `seed_horoscope_narrator_assembly` | used | E-014 | Bootstrap seed owner for daily horoscope assembly and legacy cleanup. | no DB seed executed |
| `backend/app/domain/llm/prompting/catalog.py` / `PROMPT_FALLBACK_CONFIGS`, `build_fallback_use_case_config` | used | E-015 | Bounded fallback catalog owner; current fallback keys are synthetic test entries. | fallback use may depend on DB/flags not executed here |
| `backend/app/domain/llm/runtime/gateway.py` / `LLMGateway` | used | E-015, E-016 | Canonical provider handoff, fallback and repair owner. | no real provider call |
| `backend/app/domain/llm/runtime/repair.py` / `build_repair_prompt` re-export | intentional-public-export | E-016 | Canonical runtime repair entrypoint exported through `__all__` and imported by gateway. | source-backed internal public export only |
| `backend/app/domain/llm/runtime/repair_prompter.py` / `build_repair_prompt` | used | E-016 | Builds recovery-only repair prompt after invalid provider output. | invoked conditionally after validation failure |
| `backend/app/domain/llm/configuration/catalog.py` | out-of-domain | E-015 | Story candidate path is absent; actual owner is `backend/app/domain/llm/prompting/catalog.py`. | absence only, not a deletion candidate |
| `backend/app/api/v1/routers/admin/llm/prompts.py` / `execute_admin_catalog_sample_payload` | used | E-017 | Admin manual execution route can call gateway with sample payload context. | admin policy decision not audited in depth |
| `backend/app/services/llm_generation/admin_sample_payloads.py` / `_validate_payload_json` | used | E-017 | Admin sample payload owner requires `chart_json` for natal sample payloads. | admin samples are not nominal public flow |
| `backend/tests/**` prompt-generation guards | test-only | E-018 | Tests guard carrier exclusion, fallback classification, provider locking and direct provider calls. | full suite not run in this audit |
| `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md` | used | E-019 | Explicit CS-353 deliverable. | created by this audit |
| `_condamad/stories/CS-353-audit-process-paralleles-generation-prompt-llm/evidence/*.txt` | test-only | E-019 | Persistent evidence artifacts for audit story handoff. | generated after source inspection |

## Findings Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 1 |
| Info | 1 |

## Active Implementation Findings

No application implementation finding remains for this audit story. Active findings are documentation, governance or decision findings:

- F-001: CS-350 lacks a single matrix of active non-natal provider-capable prompt processes.
- F-002: `event_guidance` remains a legacy/debt guidance seed/contract using `chart_json`, with no public trigger found in the audited route set.
- F-003: admin manual execution can send admin sample payload context to the gateway, while natal sample payload policy still requires `chart_json`; this needs explicit documentation/policy classification.
- F-004: exact guardrail coverage for parallel legacy prompt processes is absent.
- F-005: modern natal legacy carrier guards remain active and should be cited by future documentation work.

## Deferred Non-Domain Concerns

- Product ownership of `event_guidance` and whether it should be migrated, deleted or explicitly retained as debt.
- Admin manual execution authorization/product policy beyond provider capability classification.
- Real external provider behavior, because this audit uses source and test evidence only.
- Final amendment to `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`.

## Final Decision

Decision: `parallel processes confirmed; documentation correction required`.

Guidance, contextual guidance, public chat and daily horoscope narration are provider-capable runtime processes that reuse `AIEngineAdapter` or `LLMGateway`, but they are not the modern natal `llm_astrology_input_v1` flow. Repair and fallback paths are non-nominal/recovery, bootstrap seeds are provisioning inputs, tests and admin samples are separate, and `chart_json`/`natal_data` remain legacy carriers outside the modern natal prompt boundary.

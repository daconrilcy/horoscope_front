<!-- Commentaire global: rapport compagnon CONDAMAD pour l'audit CS-346 des sources astrologiques natales du prompt LLM. -->

# Audit Report - CS-346 Natal Astrology Input Sources

## Domain Closure Status

Status: closed.

This is an audit-only run for `prompt-generation-cartography`. No in-domain implementation finding remains for CS-346. The story-specific deliverable is `04-natal-astrology-input-audit.md` in this folder.

## Prior Audit And Story History Consulted

| Source | Classification | Current closure status | Evidence |
|---|---|---|---|
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800` | prior same-domain audit | surface baseline only; CS-346 narrows to input production | E-002 |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1809` | prior same-domain audit | configuration context only | E-002 |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1822` | prior same-domain audit | provider handoff context only | E-002 |
| `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` | prior story | closed for inventory context | E-002 |
| `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` | prior story | non-domain for astrology source production | E-002 |
| `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` | prior story | non-domain for astrology source production | E-002 |
| `_condamad/stories/regression-guardrails.md` | guardrail registry | RG-002 applies as backend boundary context; exact natal input guardrail remains a registry gap | E-003 |

## Audited Domain Responsibility

The audited domain owns the backend production of `llm_astrology_input_v1` for modern natal LLM execution. It covers source builders, block ownership, role classification, hash policy, evidence policy, runtime branch points, and existing guards. It does not own frontend behavior, API routing changes, provider calls, prompt edits, schema migrations, or runtime fixes.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py::LLMAstrologyInputV1Builder` | used | E-004, E-005, E-010 | Canonical owner assembling `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance`, `exclusions`, and `data_roles`. | Source/test evidence only; no provider call. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py::build_llm_input_hash_material` | used | E-004, E-008, E-010 | Builds the prompt-influencing hash material from `facts`, `signals`, `limits`, and `shaping`. | Hash algorithm delegated to projection helper. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py::LLM_ASTROLOGY_INPUT_DATA_ROLES` | intentional-public-export | E-004, E-009, E-010 | Export is consumed by gateway and architecture tests as the canonical role contract. | External package consumers were not scanned. |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py::StructuredFactsV1Builder` | used | E-005, E-010 | Canonical owner for the `facts` source projection `structured_facts_v1`. | Detailed astrology completeness is outside this audit. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py::AINarrativeInputBuilder` | used | E-006, E-010 | Produces `AINarrativeInputContract`, the source of `signals`. | Source/test evidence only. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py::AINarrativeInputContract` | intentional-public-export | E-006, E-010 | Contract type is imported by builder and `llm_astrology_input_v1.py` to validate signal ownership. | External package consumers were not scanned. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py::ClientInterpretationProjectionV1Builder` | used | E-007, E-010 | Builds `client_interpretation_projection_v1`, used only as shaping input. | It is not the canonical facts owner. |
| `backend/app/domain/astrology/projections/projection_hash.py::compute_projection_hash` | intentional-public-export | E-007, E-008, E-010 | Public helper for stable canonical JSON hash used by projection and LLM input hashes. | Algorithm not changed. |
| `backend/app/services/llm_generation/natal/interpretation_service.py::_build_llm_astrology_input_v1` | used | E-008, E-010 | Runtime branch assembling structured facts, narrative input, client projection, then the LLM input. | Service execution not run end-to-end. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` audit helpers | used | E-008, E-010 | Persist `projection_hash`, `llm_input_hash`, `grounding_status`, and `evidence_refs` from the full object, outside prompt material. | Persistence schema audit is non-domain here. |
| `backend/app/domain/llm/runtime/adapter.py::AIEngineAdapter.generate_natal_interpretation` | used | E-009, E-010 | Passes `llm_astrology_input_v1` through `ExecutionContext.extra_context` to the gateway. | Provider call not executed. |
| `backend/app/domain/llm/runtime/gateway.py::_prompt_visible_llm_astrology_input` | used | E-009, E-010, E-013 | Filters the rich contract to prompt-visible blocks only. | Gateway behavior is CS-345 context. |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | test-only | E-010 | Guards shape, owner routing, role list, hash material, and legacy exclusions. | None. |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py` | test-only | E-011 | Guards `llm_input_hash` stability and prompt-visible invalidation. | None. |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` | test-only | E-011 | Guards evidence refs and grounding status policy. | None. |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test-only | E-012 | Guards gateway prompt payload and local handoff without external provider. | None. |
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | test-only | E-012 | AST guard for role reuse and exclusion of audit-only/legacy blocks. | None. |
| `backend/tests/integration/test_llm_legacy_extinction.py` | test-only | E-013 | Guards modern natal contracts and rejection of `chart_json`/`natal_data` prompt paths. | Requires `--long` because integration tests are deselected by default. |
| `_condamad/stories/regression-guardrails.md::RG-002` | out-of-domain | E-003 | Backend API boundary guard consulted, not modified. | No exact CS-346 guardrail exists. |

## Findings Summary

| Finding | Summary | Closure |
|---|---|---|
| F-001 | Block ownership is traceable from current builders and tests. | Closed; informational. |
| F-002 | Prompt-visible, runtime-only, validation-only, and audit-only roles are separated. | Closed; informational. |
| F-003 | Legacy carriers remain forbidden for the modern natal prompt. | Closed; informational. |
| F-004 | Hash and evidence policies are source-backed and test-backed. | Closed; informational. |

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: `LLM_ASTROLOGY_INPUT_DATA_ROLES` is reused by gateway/tests; no duplicate prompt-visible block list was found in the audited flow.
- No Legacy: `chart_json` and `natal_data` are runtime-only/excluded carriers, with tests proving they do not feed the modern natal prompt.
- Mono-domain: astrology input assembly remains in astrology/domain builders; provider handoff remains in LLM runtime/gateway.
- Dependency direction: service orchestration imports domain builders and adapter; the audited domain does not introduce API or frontend ownership.

## Deferred Non-Domain Concerns

- CS-347: output validation, persistence, observability, and audit table completeness.
- Prompt text/configuration ownership remains CS-344 context.
- Provider handoff remains CS-345 context.
- Guardrail registry enrichment is explicitly out of scope for CS-346.

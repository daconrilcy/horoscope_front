# Audit Report - Calculs Interpretations Vers LLM

See the story-specific audit synthesis in `00-audit.md`. This file mirrors the CONDAMAD standard report contract.

## Audit Scope

- Domain key: `calculs-interpretations-vers-llm`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology runtime calculation, interpretation input and natal LLM execution input surfaces.
- Output folder: `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/`

## Closure Analysis

- Prior same-domain audit folders consulted: none found for this domain.
- Adjacent audit folders consulted: `astro-runtime-surface-exposure/2026-05-23-1919`, `astro-calculation-interpretation-boundary/2026-05-23-2013`, `astro-calculation-graph-readiness/2026-05-23-2000`, `frontend-ux-natal-projections/2026-05-26-0622`, `prompt-generation/2026-04-30-1810`.
- Story keys consulted: CS-217, CS-218, CS-219, CS-220, CS-221, CS-256, CS-285, CS-287, CS-302, CS-320, CS-324.
- Active findings after current evidence: F-001, F-002, F-003, F-004.
- Closed prior findings: none for same domain.
- Guardrails mapped: RG-002 and RG-141..RG-148; RG-047, RG-052 and RG-041 are non-applicable to this backend audit.
- Implementation files in audited domain: none changed.
- Governance/test files in audited domain: only audit artifacts are created.
- Deferred non-domain concerns: prompt rewrite, generator changes, public contract changes, security/auth, CI, frontend, DB and runtime implementation.

## Required Question Answers

- Runtime calculations not injected into LLM: chart-object payloads, graph outputs/provenance, `interpretation_input`, advanced conditions, dominance, fixed-star contacts and typed interpretation inputs.
- Current LLM fields from legacy/public projection: `chart_json`, `natal_data`, `evidence_catalog`.
- Current LLM fields from recent canonical owner: none proven in the scoped path; `astro_context` is transition, not the recent full interpretation owner.
- Difference between surfaces: `chart_json` is public JSON; `natal_data` is the same dict; `astro_context` is astral-point context; `evidence_catalog` is labels from `chart_json`; `structured_facts_v1` is stable factual projection; `client_interpretation_projection_v1` is plan-aware client projection; `AINarrativeInputContract` is internal narrative contract.
- Data classes: structural/internal (`ChartObjectRuntimeData`, graph outputs), pre-interpretative (`ChartInterpretationInputBuilder`, `structured_facts_v1`), narrative (`AINarrativeInputContract`, `astro_context`), public (`chart_json`, `client_interpretation_projection_v1`), debug/internal (graph trace/provenance).
- Source-of-truth owners: `backend/app/domain/astrology/runtime/**` and `backend/app/domain/astrology/interpretation/**`; compatibility/current LLM owners: `backend/app/services/chart/json_builder.py` and `backend/app/services/llm_generation/natal/interpretation_service.py`.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` | used | E-001 | Source story contract. | None. |
| `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md` | used | E-002 | Source brief and mandatory questions. | None. |
| `_condamad/stories/regression-guardrails.md` / RG-141..RG-148 | used | E-003 | Runtime and interpretation owner invariants. | No exact natal LLM input guardrail. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | out-of-domain | E-004 | Adjacent exposure audit. | Context only. |
| `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013` | out-of-domain | E-004 | Adjacent boundary audit. | Context only. |
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` / `ChartObjectRuntimeData` | used | E-005 | Canonical internal object runtime contract. | Not direct current LLM input. |
| `backend/app/domain/astrology/runtime/calculation_graph_runner.py` / `CalculationGraphRunner` | used | E-006 | Runs graph and returns outputs/provenance. | Source inspection only. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` / `natal_chart_v1` | used | E-006 | Declares canonical calculation and projection nodes. | Source inspection only. |
| `backend/app/domain/astrology/runtime/natal_result_assembler.py` / `NatalResultAssembler` | used | E-007 | Assembles historical and recent outputs into `NatalResult`. | Downstream projection separate. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` / `ChartInterpretationInputBuilder` | used | E-008 | Builds pre-interpretative input. | Not wired to current natal LLM path. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` / contracts | used | E-008, E-020 | Typed interpretation input surfaces. | Class list evidenced in E-020. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` / `AINarrativeInputBuilder` | used | E-009 | Builds AI/narrative contract. | Not wired to current natal LLM path. |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` / `structured_facts_v1` | used | E-010 | Stable factual projection. | Not current prompt input. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` / `client_interpretation_projection_v1` | used | E-011 | Public client projection. | UX projection, not direct LLM owner. |
| `backend/app/services/chart/json_builder.py` / `build_chart_json`, `build_enriched_evidence_catalog` | used | E-012, E-013 | Current owner for `chart_json`, `natal_data`, `evidence_catalog`. | Public/historical projection. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `NatalExecutionInput` assembly | used | E-013 | Current gateway input assembly owner. | No behavior changed. |
| `backend/app/domain/llm/runtime/contracts.py` / `NatalExecutionInput` | intentional-public-export | E-014 | LLM runtime contract exported and consumed by service/adapter/tests. | No shape change. |
| `backend/tests/unit/domain/astrology/**` selected tests | test-only | E-019 | Mandatory associated tests cover runtime, graph, interpretation and projection behavior. | Targeted suite execution is recorded in `validation-output.md`. |
| `frontend/src/**` | out-of-domain | E-015, E-017 | Frontend projection display is outside backend audit. | No detailed frontend audit. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: current `chart_json` / `natal_data` duplication is F-002; this audit creates no duplicate implementation.
- No Legacy: legacy/transition surfaces are classified, but no shim, prompt, route, fallback, alias or projection path is added.
- Mono-domain: backend astrology calculation/interpretation to natal LLM input only.
- Dependency direction: future convergence should let LLM services consume domain interpretation contracts without making astrology domain depend on LLM/provider code.

## Exhaustive Active Finding Surface

- F-001: `backend/app/services/llm_generation/natal/interpretation_service.py`; `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`; `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`; `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`; `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`; `backend/app/domain/llm/runtime/contracts.py`.
- F-002: `backend/app/services/llm_generation/natal/interpretation_service.py`; `backend/app/services/chart/json_builder.py`; `backend/app/domain/llm/runtime/contracts.py`.
- F-003: `backend/app/services/chart/json_builder.py`; `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`; `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`.
- F-004: `backend/app/services/llm_generation/natal/interpretation_service.py` and astral-point interpretation context owner.

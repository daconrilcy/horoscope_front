# Audit - Calculs Interpretations Vers LLM

## Scope

- Domain key: `calculs-interpretations-vers-llm`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology runtime calculation surfaces, interpretation inputs and current natal LLM execution input.
- Output folder: `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/`

## Executive Conclusion

The current natal LLM path is still centered on `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`. These are `legacy` or `transition` surfaces built from the public chart JSON path and astral-point context.

Recent canonical owners exist and are richer: `ChartObjectRuntimeData`, `CalculationGraph`, `ChartInterpretationInputBuilder`, `structured_facts_v1`, `client_interpretation_projection_v1` and `AINarrativeInputContract`. Evidence E-016 proves they are not currently wired into the scoped natal LLM execution path.

The audit should therefore feed architecture work, not code changes: converge LLM input ownership toward a narrative contract, while preserving raw runtime internals and public projections.

## Required Questions

1. Quels calculs existent aujourd'hui dans le runtime canonique mais ne sont pas injectes dans l'entree LLM ?
   - `ChartObjectRuntimeData` payloads, graph outputs, `interpretation_input`, advanced conditions, dominance, fixed-star contacts and typed interpretation inputs exist in current runtime/interpretation owners (E-005 to E-011) but are not directly passed to `NatalExecutionInput` (E-013, E-016).
2. Quels champs LLM actuels proviennent d'une projection legacy ou publique historique ?
   - `chart_json` and `natal_data` come from `build_chart_json`; `evidence_catalog` comes from `build_enriched_evidence_catalog(chart_json_dict)` (E-012, E-013).
3. Quels champs LLM actuels proviennent deja d'un owner recent et canonique ?
   - No current `NatalExecutionInput` field is sourced from `structured_facts_v1`, `client_interpretation_projection_v1`, `AINarrativeInputBuilder` or `ChartInterpretationInputBuilder` in the scoped natal path (E-016). `astro_context` is a transition narrative context, not the recent full interpretation owner (E-013).
4. Quelle est la difference entre les surfaces ?
   - `chart_json`: public/historical JSON projection. `natal_data`: same projection as object. `astro_context`: astral-point narrative context JSON. `evidence_catalog`: labels derived from `chart_json`. `structured_facts_v1`: stable factual projection from interpretation input. `client_interpretation_projection_v1`: plan-aware client projection from `structured_facts_v1`. `AINarrativeInputContract`: internal narrative/AI contract from interpretation input.
5. Quelles donnees sont structurelles, pre-interpretatives, narratives, publiques, debug ou internes ?
   - See `02-surface-matrix.md`. `ChartObjectRuntimeData`, graph outputs and `NatalResult` are structural/internal or transition; `ChartInterpretationInputBuilder` and `structured_facts_v1` are pre-interpretative; `AINarrativeInputContract` and `astro_context` are narrative; `chart_json`, `natal_data`, `client_interpretation_projection_v1` are public or public-controlled; graph traces/provenance are debug/internal.
6. Quels owners doivent rester source de verite et lesquels ne doivent servir qu'a la compatibilite ?
   - Source of truth: `backend/app/domain/astrology/runtime/**` for calculations, `backend/app/domain/astrology/interpretation/**` for interpretation input and narrative/factual projections. Compatibility/current LLM input: `backend/app/services/chart/json_builder.py` and current assembly in `backend/app/services/llm_generation/natal/interpretation_service.py`.

## Findings Summary

| ID | Severity | Summary | Evidence | Story candidate |
|---|---|---|---|---|
| F-001 | High | Current natal LLM input bypasses recent interpretation/narrative owners and still uses legacy/transition surfaces. | E-008, E-009, E-010, E-011, E-013, E-016 | yes |
| F-002 | Medium | `chart_json` and `natal_data` duplicate the same public projection in two shapes inside `NatalExecutionInput`. | E-012, E-013, E-014 | yes |
| F-003 | Medium | `evidence_catalog` remains derived from public `chart_json`, not from recent stable fact/narrative owners. | E-010, E-012, E-013 | yes |
| F-004 | Low | `astro_context` is a transition surface whose name is broader than its proven astral-point content. | E-013 | no |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-324-audit-calculs-interpretations-llm/00-story.md` | used | E-001 | Source contract for scope, ACs, output shape and no-app-change rule. | None. |
| `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md` | used | E-002 | Source brief for mandatory questions and source files. | None. |
| `_condamad/stories/regression-guardrails.md` / RG-141..RG-148 | used | E-003 | Existing invariants protect recent runtime owners relevant to this audit. | No exact natal LLM input guardrail. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | out-of-domain | E-004 | Adjacent prior audit on public/internal runtime exposure. | Context only. |
| `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013` | out-of-domain | E-004 | Adjacent prior audit on calculation/interpretation/LLM boundaries. | Context only. |
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` / `ChartObjectRuntimeData` | used | E-005 | Canonical internal object runtime contract. | Not direct current LLM input. |
| `backend/app/domain/astrology/runtime/calculation_graph_runner.py` / `CalculationGraphRunner` | used | E-006 | Executes graph and records outputs/provenance. | Runtime run not executed by audit. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` / `natal_chart_v1` | used | E-006 | Declares canonical calculation and projection nodes. | Source inspection only. |
| `backend/app/domain/astrology/runtime/natal_result_assembler.py` / `NatalResultAssembler` | used | E-007 | Assembles historical and recent runtime outputs into `NatalResult`. | Downstream projection evidenced separately. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` / `ChartInterpretationInputBuilder` | used | E-008 | Builds pre-interpretative input from runtime objects and facts. | Not wired to current natal LLM path. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` / `ChartInterpretationInputRuntimeData` | used | E-008, E-015 | Defines typed interpretation input surfaces consumed by builders. | Detailed class list not repeated here. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` / `AINarrativeInputBuilder` | used | E-009 | Builds `AINarrativeInputContract` from interpretation input. | Not wired to current natal LLM path. |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` / `structured_facts_v1` | used | E-010 | Stable fact projection and possible evidence input. | Not current prompt input. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` / `client_interpretation_projection_v1` | used | E-011 | Public client projection from `structured_facts_v1`. | UX projection, not direct LLM owner. |
| `backend/app/services/chart/json_builder.py` / `build_chart_json` and `build_enriched_evidence_catalog` | used | E-012, E-013 | Current owner for `chart_json`, `natal_data` and `evidence_catalog` used by LLM. | Historical/public projection, not richest canonical input. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `NatalExecutionInput` assembly | used | E-013 | Current gateway input assembly owner. | No behavior changed. |
| `backend/app/domain/llm/runtime/contracts.py` / `NatalExecutionInput` | intentional-public-export | E-014 | LLM runtime contract exported in `__all__` and consumed by adapter/service/tests. | Audit does not change contract shape. |
| `backend/tests/unit/domain/astrology/**` selected tests | test-only | E-015 | Tests prove runtime, graph, interpretation and projection behavior. | Full suite may be expensive; targeted suite planned. |
| `frontend/src/**` | out-of-domain | E-015, E-017 | Frontend projection display is outside backend audit scope. | No frontend files read in depth. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: current `chart_json` / `natal_data` duplication is a material representation risk (F-002). The audit does not create a second runtime path.
- No Legacy: no shim, alias, fallback, prompt or projection path was added. Existing legacy/transition surfaces are classified in `04-legacy-register.md`.
- Mono-domain: findings stay in backend astrology calculation/interpretation to natal LLM input. Frontend, auth, DB, migrations and prompt copy remain out-of-scope.
- Dependency direction: recommended convergence must let LLM services consume domain interpretation contracts; domain astrology must not import provider/gateway code.

## Closure Analysis

- Prior same-domain audit folders consulted: none found for `calculs-interpretations-vers-llm`.
- Adjacent audits consulted: listed in E-004.
- Story keys consulted: CS-217, CS-218, CS-219, CS-220, CS-221, CS-256, CS-285, CS-287, CS-302, CS-320 and CS-324 through story/guardrail scans.
- Active findings after current evidence: F-001, F-002, F-003, F-004.
- Closed prior findings: none for same domain.
- Implementation files in audited domain: none changed.
- Governance/test files in audited domain: only audit artifacts are created.
- Deferred non-domain concerns: prompt rewrite, generator change, public contract change, frontend UI, DB, auth, migrations and runtime code changes.

## Exhaustive Active Finding Surface

- F-001: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`, `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`, `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`, `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`, `backend/app/domain/llm/runtime/contracts.py`.
- F-002: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/services/chart/json_builder.py`, `backend/app/domain/llm/runtime/contracts.py`.
- F-003: `backend/app/services/chart/json_builder.py`, `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`, `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`.
- F-004: `backend/app/services/llm_generation/natal/interpretation_service.py` and astral-point interpretation context owner.

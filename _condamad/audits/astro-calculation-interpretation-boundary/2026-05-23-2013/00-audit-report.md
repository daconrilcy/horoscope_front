# Audit Report - Astro Calculation Interpretation Boundary

## Audit Scope

- Domain key: `astro-calculation-interpretation-boundary`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology calculation, structural scoring, interpretation input, LLM prompt/runtime, and product projection boundary.
- Output folder: `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 records that no prior `astro-calculation-interpretation-boundary` child folder existed.
- Adjacent audit folders consulted: `astro-runtime-surface-exposure/2026-05-23-1919`, `astro-calculation-graph-readiness/2026-05-23-2000`, `prediction/2026-05-03-2214`, and `prompt-generation/2026-04-30-1810`.
- Story keys consulted: `CS-229`, `CS-230`, `CS-231`, `CS-236`, `CS-242`, and `CS-243`.
- Active findings after current evidence: F-001, F-002, F-003 and F-004.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: RG-098 to RG-102, RG-118, RG-141, RG-143, RG-144 to RG-148.
- Implementation files in audited domain: no application file is changed by this audit.
- Governance/test files in audited domain: only the six new audit artifacts are created.
- Deferred non-domain concerns: frontend UI, DB migrations, auth, entitlement, i18n, styling, seed content and new runtime behavior remain outside this audit.

## Boundary Classification Grid

| Élément | Catégorie | Owner | Surface runtime | Surface publique | Risque de confusion | Décision frontière | Preuve |
|---|---|---|---|---|---|---|---|
| longitude Mars | fait astronomique | `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` / SwissEph calculation path | `planet_positions` node and `NatalResult.planet_positions` | public natal chart projection through chart JSON | Low: source is geometric/ephemeris data, but downstream prompts may quote it. | keep as structural internal/public fact | E-006, E-007 |
| Mars maison 10 | fait astrologique structurel | house runtime and chart object payload builders | `houses`, `chart_objects`, house/rulership payloads | public house projection and selected chart facts | Medium: house placement is structural astrology, not interpretation. | keep internal structural fact, project publicly only through stable fields | E-006, E-007, E-012 |
| Mars dominant | scoring structurel | `backend/app/domain/astrology/dominance` | `dominant_planets`, dominance payloads, chart-level result | existing `dominant_planets` public projection | Medium: score can be read as personality text if not labelled as ranking evidence. | keep as structural scoring; require product copy to label it as score/rank | E-006, E-007, E-012 |
| Mars combatif | signal interprétatif | `backend/app/domain/astrology/interpretation/**` | `ChartInterpretationInputRuntimeData`, aspect hints, condition/sign profile facts | none as raw public contract | High: short signal is pre-narrative and can be mistaken for calculated truth. | story-candidate for explicit internal/public/LLM contract split | E-008, E-009, F-001 |
| Vous avez une énergie de conquête | texte | `backend/app/services/llm_generation/**` or deterministic editorial/product layer | LLM structured output or product projection, not calculator output | public narrative fields such as `daily_synthesis` or `narrative` | High: final text must not flow back into calculation or scoring. | keep text in LLM/product projection contract only | E-010, E-011 |
| `developer_prompt` and rendered provider messages | prompt LLM | `backend/app/domain/llm/configuration`, `backend/app/domain/llm/prompting`, `backend/app/domain/llm/runtime/gateway.py` | `LLMExecutionRequest`, rendered developer prompt, provider messages | admin/operator preview surfaces; not public chart fact | High: prompt content can embed chart facts and guidance but is not a domain fact. | keep in contrat LLM; do not expose as structural or public chart contract | E-010, E-015 |
| daily prediction narrative fields | projection produit | `backend/app/services/prediction/public_predictions.py` and public API contracts | assembled prediction dict enriched by gateway narration | `DailyPredictionResponse.daily_synthesis`, time-window `narrative`, `has_llm_narrative` | High: product projection mixes deterministic prediction shape and optional LLM text. | keep as projection produit with explicit source flag and no backflow to calculation | E-011, E-016 |
| `ChartInterpretationInputRuntimeData` | signal interprétatif | `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` | internal input with objects, aspects, dignities, dominance, fixed-star contacts, sign balances and advanced condition facts | none | High if exposed raw: contract is optimized for interpretation, not API UX. | move-to-internal contract plus LLM input contract decision | E-008, E-012, F-001 |

## Boundary Decisions

- Contrat interne: calculated astronomical facts, structural astrological facts and structural scoring stay under `backend/app/domain/astrology/**`; current architecture tests already block many interpretive tokens in structural roots.
- Contrat public: public chart and prediction payloads must be explicit projections, not raw `ChartObjectRuntimeData` or raw `ChartInterpretationInputRuntimeData`.
- Contrat LLM: prompt rendering, provider messages and structured LLM output stay under `backend/app/domain/llm/**` and `backend/app/services/llm_generation/**`.
- The boundary is materially improved after CS-229 to CS-231, but closure is not complete because `ChartInterpretationInput` lacks an explicit public/internal/LLM contract decision, no compact interpretation-readiness projection exists, and narrative-token guards are not yet lexical enough for final user-facing text.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-243-audit-calculation-interpretation-boundary/00-story.md` | used | E-001 | Source contract for scope, AC, categories and no-app-change rule. | None. |
| `_story_briefs/cs-243-audit-calculation-interpretation-boundary-audit.md` | used | E-002 | Source brief for mandatory grid, categories and CS-252 to CS-254 labels. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-098..RG-148 subset | used | E-003 | Existing invariants protect structural, interpretive, scoring, chart-object and prompt boundaries. | No exact calculation-interpretation-boundary guardrail exists. |
| `_condamad/audits/astro-calculation-interpretation-boundary` | used | E-004 | Canonical output root for this audit domain. | No prior child folder existed. |
| `docs/architecture/astrology-runtime-surfaces.md` | used | E-005 | Documents structural runtime, interpretive runtime, public projection and legacy projection. | It is architecture intent plus guard-backed docs, not a full product contract. |
| `backend/app/domain/astrology/natal_calculation.py` / `NatalResult` | used | E-006 | Owns structural natal result fields and internal SkipJsonSchema fields for advanced conditions and chart objects. | Public serializer behavior is evidenced separately. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` and `natal_calculation_nodes.py` | used | E-007 | Shows node outputs for positions, chart objects, dignities, dominance and interpretation input. | Full graph behavior is inherited from CS-242 evidence. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` | used | E-008 | Defines the internal interpretation input contract and its pre-narrative surfaces. | Not a public API contract. |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` | used | E-009 | Builds interpretation input from structural facts without provider calls. | Does not decide future public projection shape. |
| `backend/app/domain/llm/runtime/gateway.py` and `contracts.py` | used | E-010 | Canonical LLM request, prompt rendering, message composition and result validation surfaces. | Large runtime; audit uses targeted proof and integration test. |
| `backend/app/services/prediction/public_predictions.py` and `backend/app/services/api_contracts/public/predictions.py` | used | E-011 | Current product projection and public narrative fields for daily prediction. | Daily prediction is adjacent product projection, not natal calculation core. |
| `backend/tests/architecture/test_astrology_runtime_boundary.py` | test-only | E-012 | Broad AST guard for structural versus interpretive runtime roots and allowlist completeness. | It blocks English/token identifiers, not every possible French final-text phrase. |
| `backend/tests/architecture/test_structural_runtime_boundary.py` | test-only | E-013 | Aspect structural contracts stay free of interpretive aliases. | Aspect-focused. |
| `backend/tests/architecture/test_chart_interpretation_input_boundary.py` | test-only | E-014 | Interpretation input modules do not call calculators/providers and contracts avoid editorial text fields. | It does not classify public/internal/LLM contract names. |
| `backend/app/tests/integration/test_llm_qa_runtime_contracts.py` | test-only | E-015 | Runtime LLM contract test proves prompt, persona and output validation flow. | Uses a QA use case, not every product prompt. |
| `backend/app/tests/unit/test_chart_result_service.py` | test-only | E-016 | Persistence tests prove product/audit payload boundaries and no fabricated backfill. | Persistence-oriented, not a prompt test. |
| `docs/2026-04-20-audit-prompts-backend*.md` | out-of-domain | E-017 | Historical prompt audits were consulted to compare old versus current LLM namespaces. | Older docs cite removed paths. |
| `backend/app/llm_orchestration/**` and `backend/app/prediction/**` | out-of-domain | E-018 | Historical paths are absent in current workspace; current owners are `domain/llm`, `domain/prediction` and `services/prediction`. | Absence scan does not inspect deleted history beyond docs. |
| `frontend/src/**`, `backend/migrations/**`, `docs/db_seeder/**` modification surface | out-of-domain | E-019 | Explicitly forbidden by story and verified through diff discipline. | Existing unrelated worktree changes predate this audit run. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: current code already has distinct owners for structural runtime, interpretation input, LLM runtime and public prediction projection. Findings target missing contract naming rather than duplicate implementation.
- No Legacy: this audit creates no wrapper, alias, fallback, compatibility route or runtime branch. Historical `app.llm_orchestration` and `app.prediction` paths are not reintroduced.
- Mono-domain: findings stay in calculation/interpretation boundary governance. Product decisions about new public UI fields are deferred to candidate stories.
- Dependency direction: structural astrology code does not depend on LLM runtime; LLM and product projections consume structured facts through service/domain contracts.

## Exhaustive Active Finding Surface

- F-001: `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py`, `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`, public API contract docs/tests selected by CS-252. No file is changed by this audit.
- F-002: `backend/app/domain/astrology/interpretation/**`, `backend/app/domain/astrology/runtime/natal_calculation_graph.py`, future interpretation-readiness projection owner selected by CS-253. No file is changed by this audit.
- F-003: structural roots covered by `backend/tests/architecture/test_astrology_runtime_boundary.py`, plus future lexical narrative-token guard selected by CS-254. No file is changed by this audit.
- F-004: docs and prior audit references to removed `backend/app/llm_orchestration` / `backend/app/prediction` paths. No application file is changed by this audit.

## Deferred Non-Domain Context

- Frontend consumption of future public chart facts belongs to product-data and runtime-surface exposure follow-up work.
- Prompt copy quality and editorial tone belong to prompt-generation audits and release QA, not this calculation boundary audit.
- DB seed taxonomy changes belong to reference governance and product-data-needs audits.

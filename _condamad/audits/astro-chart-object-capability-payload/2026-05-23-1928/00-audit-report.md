# Audit Report - Astro Chart Object Capability Payload

## Audit Scope

- Domain key: `astro-chart-object-capability-payload`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology chart-object taxonomy, capabilities, payloads, producers, consumers and projections.
- Output folder: `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928/`

## Closure Analysis

- Prior same-domain audit folders consulted: none before this audit; E-004 records the targeted domain-root inventory and the created current folder.
- Adjacent audit folders consulted: `_condamad/audits/astro-feature-coverage/2026-05-23-1905` and `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919`.
- Story keys consulted: `CS-239-audit-chart-object-capability-payload`, adjacent runtime stories through guardrails RG-144 to RG-148, and the adjacent audit references in E-018 and E-019.
- Active findings after current evidence: F-001, F-002, F-003, F-004 and F-005.
- Observation-only finding: F-006.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: RG-144 through RG-148 protect the current chart-object runtime, aspects, motion/visibility, dignity/dominance and house/rulership invariants.
- Implementation files in audited domain: no file is changed by this audit.
- Governance/test files in audited domain: no existing governance/test file is changed by this audit.
- Deferred non-domain concerns: public API projection, frontend UI, auth/admin debug exposure, DB migrations, runtime calculator implementation and serializer changes remain outside this audit.

## Mandatory Capability Payload Matrix

| Object type | Capabilities | Payloads requis | Payloads optionnels | Calculateurs consommateurs | Calculateurs producteurs | Projection publique | Projection interprétative |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `luminary` | `supports_aspects`, `supports_dignities`, `supports_house_position`, `supports_fixed_star_conjunction`, `supports_interpretation`, `supports_dominance`, `supports_rulership`; `supports_motion` and `supports_visibility` only when source data exists. | `house_position`; `motion` when `supports_motion`; `visibility` when `supports_visibility`; phase-required `dignity`, `dominance`, `rulership` after enrichment. | `fixed_star_conjunctions`, dignity breakdowns, dominance breakdowns, visibility solar fields. | Aspect selector, dignity projector, dominance projector, rulership enricher, fixed-star target selector, interpretation projector. | Planet position node, motion/visibility node, chart-object builder, fixed-star enricher, dignity enricher, dominance enricher, rulership enricher. | Existing legacy projections for positions, dignities, dominance and advanced conditions; raw `chart_objects` excluded. | Included when `supports_interpretation`; payload facts are mapped to interpretation input. |
| `planet` | Same as `luminary`, with ephemeris source and non-luminary classification. | Same as `luminary`. | Same as `luminary`. | Same as `luminary`. | Same as `luminary`. | Existing legacy projections; raw `ChartObjectRuntimeData` excluded. | Included when `supports_interpretation`; fixed-star contacts, dignity, dominance and condition facts can flow to interpretation input. |
| `astral_point` | `supports_house_position` when a house exists, `supports_interpretation`, and `supports_aspects` only when point aspects are enabled. | `house_position` when `supports_house_position`. | none proven beyond base object fields. | Aspect selector when enabled, interpretation selector/projector. | Astral point resolver, chart-object builder. | Existing `astral_points` public projection; raw chart object excluded. | Included when `supports_interpretation` and zodiac position exists. |
| `angle` | `supports_house_position`, `supports_interpretation`; `supports_aspects` is builder-configurable but disabled in the current graph. | `house_position`, `angle`. | none proven. | Interpretation projector; aspect selector only outside current graph configuration. | House runtime, chart-object builder. | Existing house/axis projections; raw angle payload excluded. | Included when `supports_interpretation` and zodiac position exists. |
| `house_cusp` | `supports_house_position`. | `house_position`, `house_cusp`. | none proven. | No active aspect, dignity, dominance or interpretation consumer in current evidence. | House runtime, chart-object builder. | Existing house projection; raw `house_cusp` payload excluded. | Not selected because `supports_interpretation` is false. |
| `fixed_star` | No active capability flags; documentary object with source catalog payload. | `fixed_star` documentary payload. | none; `fixed_star_conjunctions` defaults empty and fixed stars are excluded as targets. | Fixed-star chart-object selector as source objects for conjunctions; public raw exposure is excluded. | Runtime reference fixed-star catalog, chart-object builder. | No raw payload projection; adjacent exposure audit recommends dedicated reduced projection if productized. | Not selected as object because `supports_interpretation` is false; fixed-star contacts can project through target objects. |
| `arabic_part` | No active runtime capability evidence. | none proven. | none proven. | none proven. | none found in application code. | none. | none. |
| `calculated_point` | Enum exists; only test fixture evidence for aspect selector, no active application producer. | none proven. | none proven. | Aspect selector can consume a fixture object if `supports_aspects=True`. | none found in application code. | none. | none. |

## Required Questions

- Toutes les capacités ont-elles une sémantique claire ? Partially. E-005 to E-010 prove operational semantics for aspects, dignities, house position, motion, visibility, dominance, rulership, interpretation and fixed-star conjunction targets. F-001 remains open because the canonical matrix is not a first-class contract.
- Un payload peut-il exister sans capacité correspondante ? Generally no for motion, visibility, house position, dignity, dominance, rulership and fixed-star conjunction contacts because constructors or enrichers reject those states. Documentary `fixed_star`, `angle` and `house_cusp` payloads are type/family payloads without matching `supports_*` flags; this is coherent but should be explicit in CS-246.
- Une capacité peut-elle être vraie sans payload requis ? Constructor-required motion, visibility and house position cannot; phase-required dignity, dominance and rulership can be temporarily true before their enrichment phase and are later validated by phase validators. This phase model is the main subject of F-002.
- Les étoiles fixes sont-elles des objets ou seulement des sources de contacts ? They are both documentary chart objects and source objects for contacts. They are not fixed-star conjunction targets and are not interpretation-selected as objects under current evidence.
- Les angles doivent-ils participer aux aspects ? Current graph says no by passing `include_angles_in_aspects=False`; builder supports a configurable yes. This is an open product/runtime decision in F-004.
- Les cuspides doivent-elles devenir aspectables ? Current evidence says no; house cusps carry house-position and house-cusp payloads only. Any change needs matrix decision first.
- Les lots doivent-ils avoir dignités, aspects, maisons ou dominance ? No repository evidence can decide this. `ARABIC_PART` is declared but inactive; F-003 routes the decision to derived point taxonomy.
- Les noeuds doivent-ils être traités comme planètes, points ou catégorie dédiée ? Current runtime treats nodes as `ASTRAL_POINT` objects. They are non-dignity, non-dominance and non-motion; point-aspect options can include them. F-005 keeps the dedicated-category decision open.

## Capability Semantics

- `supports_aspects`: object can be selected by `AspectChartObjectSelector`; requires a finite longitude at projection time.
- `supports_dignities`: object can become a dignity input; requires longitude, zodiac position and house position before calculation, then a `dignity` payload after enrichment.
- `supports_house_position`: object must carry `house_position` immediately.
- `supports_visibility`: object must carry `visibility` immediately when declared.
- `supports_motion`: object must carry `motion` immediately when declared.
- `supports_interpretation`: object can be selected for interpretation projection; projector requires zodiac position.
- `supports_dominance`: object can become a dominance input; requires longitude, house position and ephemeris source, and can depend on dignity payload when dignity-capable.
- `supports_rulership`: object can receive `rulership` payload from existing house-ruler results.
- `supports_fixed_star_conjunction`: object can receive fixed-star contact payloads and is explicitly separate from being a fixed-star source object.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-239-audit-chart-object-capability-payload/00-story.md` | used | E-001 | Source contract for this audit's required folder, matrix, questions and candidates. | None. |
| `_story_briefs/cs-239-audit-chart-object-capability-payload-audit.md` | used | E-002 | Source brief for domain boundary and validation expectations. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-144..RG-148 | used | E-003 | Existing invariants protect chart-object runtime ownership and capability-driven consumers. | No exact CS-239 guardrail exists. |
| `_condamad/audits/astro-chart-object-capability-payload` | used | E-004 | Canonical output root for this audit domain. | No prior same-domain child folder existed. |
| `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | out-of-domain | E-019 | Adjacent audit used only to classify product feature coverage and lots/nodes/fixed-star context. | Not a capability/payload domain audit. |
| `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | out-of-domain | E-018 | Adjacent audit used only to confirm raw runtime non-exposure. | Not a capability/payload domain audit. |
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | used | E-005 | Canonical contract owner for object types, capabilities, payloads and validators. | No file was modified. |
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | used | E-006, E-016 | Canonical producer of active chart object families and initial payloads. | `ARABIC_PART` and `CALCULATED_POINT` are not actively produced. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | used | E-007 | Declares producer/consumer ordering for chart objects and payload enrichment. | Source inspection only. |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` | used | E-007, E-016 | Node adapters prove current graph disables angle aspects and runs phase validators. | No graph behavior was changed. |
| `backend/app/domain/astrology/calculators/aspect_inputs.py` | used | E-008 | Aspect consumer selects by `supports_aspects` and projects to aspect body runtime data. | Product aspectability policy remains open. |
| `backend/app/domain/astrology/dignities/chart_object_inputs.py` | used | E-009 | Dignity selector, projector and payload enricher consume capability-selected objects. | Phase validator is separate from constructor validation. |
| `backend/app/domain/astrology/dominance/chart_object_inputs.py` | used | E-009 | Dominance selector, projector and payload enricher consume capability-selected objects. | Requires dignity payload when dignity-capable. |
| `backend/app/domain/astrology/builders/chart_object_house_runtime_enricher.py` | used | E-010 | Rulership payload enrichment owner. | Does not decide lots or node taxonomy. |
| `backend/app/domain/astrology/fixed_stars/**` | used | E-011 | Fixed-star selector, calculator and enricher are in-domain consumers/producers for contacts. | Public projection is out of this domain. |
| `backend/app/domain/astrology/interpretation/**` selected chart-object files | used | E-012 | Interpretation projection consumes `supports_interpretation` and mapped payloads. | LLM prompt generation was not audited. |
| `backend/app/services/chart/**` | out-of-domain | E-013 | Inspected only to distinguish public projections from raw runtime payloads. | Service changes are forbidden by this audit. |
| `backend/app/api/**` | out-of-domain | E-013 | Inspected only to confirm no raw chart-object public exposure. | No API changes are in scope. |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | test-only | E-014 | Unit evidence for active object families and payload/capability behavior. | Test file was not modified. |
| `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | test-only | E-014 | Runtime evidence for end-to-end chart object payload enrichment and public exclusion. | Test file was not modified. |
| `backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | test-only | E-017 | Architecture guard for capability-driven consumers and dependency boundaries. | Guard does not encode the full matrix. |
| `backend/tests/integration/astrology/test_natal_public_contract_compatibility.py` | test-only | E-013 | Public contract guard proving raw chart-object surfaces stay internal. | Integration test not part of same-domain implementation. |
| `frontend/src/**` | out-of-domain | E-001, E-022 | Frontend work is explicitly forbidden and no frontend delta exists. | Not inspected for UI behavior. |
| `backend/migrations/**` | out-of-domain | E-001, E-022 | Database migrations are explicitly forbidden and no migration delta exists. | Not inspected beyond no-delta guard. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: current consumers use `ChartObjectCapabilities` selectors instead of duplicating object-type eligibility in aspect, dignity, dominance, rulership, fixed-star and interpretation paths.
- No Legacy: no route, alias, shim, fallback branch, compatibility wrapper or raw public `ChartObjectRuntimeData` exposure was added.
- Mono-domain: findings stay within backend astrology chart-object taxonomy; API, frontend, admin/debug and DB concerns are deferred non-domain context.
- Dependency direction: audited runtime/domain files do not depend on API/public serializers for capability decisions; public projection remains outside this audit.

## Exhaustive Active Finding Surface

- F-001: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`, `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`, `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`, selected consumer files and tests. No app file is to be changed by this audit.
- F-002: `chart_object_runtime_data.py` validators, `natal_calculation_nodes.py` phase validators, dignity/dominance/rulership/fixed-star enrichers and current payload tests. No app file is to be changed by this audit.
- F-003: enum values in `chart_object_runtime_data.py`, absent active producers under `backend/app/**`, adjacent feature context. No app file is to be changed by this audit.
- F-004: builder aspect options, graph node angle option, aspect selector, aspect tests. No app file is to be changed by this audit.
- F-005: astral point builder path, point aspect option, natal result tests and feature-audit context. No app file is to be changed by this audit.
- F-006: fixed-star runtime files and public projection tests. No implementation candidate in this domain.

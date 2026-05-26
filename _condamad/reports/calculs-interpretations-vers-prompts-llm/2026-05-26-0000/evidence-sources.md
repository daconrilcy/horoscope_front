# Evidence Sources

<!-- Commentaire global: ce fichier conserve les sources consultees pour le rapport CS-329 et les conclusions qui en dependent. -->

## Source availability

| Story | Deliverable folder | Required files checked | Status |
|---|---|---|---|
| CS-324 | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/` | audit, evidence, findings, matrices, validation | PASS |
| CS-325 | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/` | audit, sequence, field matrix, branches, validation | PASS |
| CS-326 | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/` | audit, comparison, classification, readiness, validation | PASS |
| CS-327 | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/` | audit, use cases, schema matrix, fallback, validation | PASS |
| CS-328 | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/` | architecture, evidence map, contract, transition, roadmap | PASS |

## Short citations and synthesis anchors

| ID | Source | Short cited point | Used in report |
|---|---|---|---|
| S-324-01 | CS-324 `05-executive-summary.md` | current input is `chart_json`, `natal_data`, `evidence_catalog`, `astro_context` | current state |
| S-324-02 | CS-324 `02-surface-matrix.md` | `chart_json` is legacy and prompt-bound; recent owners are not in current path | legacy and gaps |
| S-324-03 | CS-324 `03-gap-register.md` | `AINarrativeInputContract` exists but is not consumed by natal LLM | target contract |
| S-324-04 | CS-324 `04-legacy-register.md` | `structured_facts_v1` is recent-refonte and unused by current LLM path | data not exploited |
| S-325-01 | CS-325 `05-executive-summary.md` | only `chart_json` is prompt-visible by default in audited path | current injection |
| S-325-02 | CS-325 `02-finding-register.md` | runtime fields can be mistaken for prompt-visible data | guardrails |
| S-325-03 | CS-325 `03-story-candidates.md` | future tests must distinguish prompt-visible/runtime-only fields | future stories |
| S-326-01 | CS-326 `05-executive-summary.md` | `AINarrativeInputContract` is best canonical candidate | target architecture |
| S-326-02 | CS-326 `04-recommendations.md` | keep client projection B2C, audit storage post-generation | exclusions |
| S-326-03 | CS-326 `02-finding-register.md` | `structured_facts_v1` is fact source, B2C projections are shaping | contract blocks |
| S-327-01 | CS-327 `05-executive-summary.md` | active configs still require `chart_json`; no `llm_astrology_input` | schema readiness |
| S-327-02 | CS-327 `03-story-candidates.md` | declare canonical LLM astrology input schema first | roadmap |
| S-328-01 | CS-328 `00-architecture.md` | target flow goes runtime -> interpretation -> contract -> prompt -> audit | architecture |
| S-328-02 | CS-328 `02-target-contract.md` | `llm_astrology_input_v1` wraps `AINarrativeInputContract` | contract shape |
| S-328-03 | CS-328 `04-story-candidates.md` | roadmap P1-P5 sequences contract, evidence, schema, guards, legacy | refactor sequence |

## Contradictions and resolutions

| Topic | Apparent contradiction | Resolution |
|---|---|---|
| Upstream tracker status | CS-324 to CS-328 rows are `ready-to-dev` while deliverable folders exist. | Use existing deliverable folders as runtime source evidence for CS-329; record tracker mismatch as residual governance risk. |
| Prompt visibility | `NatalExecutionInput` carries many fields, but prompt visibility is narrower. | Treat `chart_json` as current prompt-visible carrier and others as runtime/validation unless explicitly rendered. |
| Evidence role | `evidence_catalog` sounds like grounding material. | CS-325 proves validation-only in current path; future `evidence_refs` owner decision is required. |
| Client projection | `client_interpretation_projection_v1` contains narrative-ready material. | Keep it as B2C shaping source, not factual prompt contract, per CS-326/CS-328. |
| Runtime richness | `ChartObjectRuntimeData` is rich and available. | It remains internal; prompts must use derived controlled contracts, never raw runtime objects. |

## Bounded backend rereads

No backend code reread was required during CS-329 correction. The CS-324 to CS-328 deliverables already resolved the current
state, target contract and contradictions needed by the report. No `backend/app`, `backend/tests`, `frontend/src` or migration
file was modified.

## Guardrail mapping

| Guardrail | Evidence |
|---|---|
| RG-002 `refactor-api-v1-routers` | No backend API or application file changed; `git status --short -- backend/app backend/tests frontend/src backend/migrations` validated. |
| RG-041 non-applicable | Entitlement documentation is outside this synthesis report scope; no entitlement docs were edited. |
| Registry gap | No exact synthesis-report guardrail exists; local invariant is no application, prompt, endpoint, frontend, DB or migration change. |

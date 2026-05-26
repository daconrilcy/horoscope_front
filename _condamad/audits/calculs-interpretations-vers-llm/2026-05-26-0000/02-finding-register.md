# Finding Register - Calculs Interpretations Vers LLM

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | calculs-interpretations-vers-llm | E-008, E-009, E-010, E-011, E-013, E-016 | Natal LLM generation can rely on poorer legacy/transition inputs while richer recent interpretation owners remain unused. | Route future natal LLM input through an explicit canonical narrative/factual contract or mark this as a user architecture decision. | yes |
| F-002 | Medium | High | duplicate-responsibility | calculs-interpretations-vers-llm | E-012, E-013, E-014 | `chart_json` and `natal_data` carry the same projection in two shapes, increasing drift risk when one representation evolves. | In a future implementation story, define one canonical LLM factual payload and keep duplicate fields only as compatibility until migrated. | yes |
| F-003 | Medium | High | missing-canonical-owner | calculs-interpretations-vers-llm | E-010, E-012, E-013 | LLM evidence references are tied to public `chart_json`, not to stable facts or narrative readiness owners. | Decide whether `structured_facts_v1` or `AINarrativeInputContract` owns LLM evidence material. | yes |
| F-004 | Low | Medium | missing-canonical-owner | calculs-interpretations-vers-llm | E-013 | `astro_context` name suggests broad astrology context but evidence shows a narrower astral-point context. | Do not change now; clarify ownership/name during LLM input convergence. | no |

## Finding Details

### F-001 - Current natal LLM input bypasses recent interpretation owners

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: calculs-interpretations-vers-llm
- Evidence: E-008, E-009, E-010, E-011, E-013, E-016
- Expected rule: LLM natal input should be based on a canonical interpretation/narrative owner when such owners exist, without exposing raw runtime internals.
- Actual state: `NatalExecutionInput` is assembled from `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`; recent owners are not called in the scoped LLM path.
- Impact: Natal LLM generation can rely on poorer legacy/transition inputs while richer recent interpretation owners remain unused.
- Recommended action: Route future natal LLM input through an explicit canonical narrative/factual contract or mark this as a user architecture decision.
- Story candidate: yes
- Suggested archetype: `service-boundary-refactor`
- Closure decision: `phased-with-map`; SC-001 selects the canonical owner and defines the complete migration surface.

### F-002 - `chart_json` and `natal_data` duplicate one projection

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: calculs-interpretations-vers-llm
- Evidence: E-012, E-013, E-014
- Expected rule: one factual LLM input surface should own chart facts, with compatibility fields explicitly bounded.
- Actual state: `chart_json` is `json.dumps(chart_json_dict)` and `natal_data` is the same `chart_json_dict`.
- Impact: `chart_json` and `natal_data` carry the same projection in two shapes, increasing drift risk when one representation evolves.
- Recommended action: In a future implementation story, define one canonical LLM factual payload and keep duplicate fields only as compatibility until migrated.
- Story candidate: yes
- Suggested archetype: `duplicate-rule-removal`
- Closure decision: `full-closure` if SC-002 is implemented after SC-001 or explicitly scoped to compatibility mapping.

### F-003 - Evidence catalog is tied to legacy public projection

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: calculs-interpretations-vers-llm
- Evidence: E-010, E-012, E-013
- Expected rule: LLM evidence material should map to the canonical factual/narrative source used for prompt input.
- Actual state: `build_enriched_evidence_catalog` derives labels from `chart_json`, while `structured_facts_v1` has stable fact and hash material not injected in the current LLM path.
- Impact: LLM evidence references are tied to public `chart_json`, not to stable facts or narrative readiness owners.
- Recommended action: Decide whether `structured_facts_v1` or `AINarrativeInputContract` owns LLM evidence material.
- Story candidate: yes
- Suggested archetype: `contract-shape-audit`
- Closure decision: `phased-with-map`; should follow canonical input-owner decision.

### F-004 - `astro_context` is a narrow transition context

- Severity: Low
- Confidence: Medium
- Category: missing-canonical-owner
- Domain: calculs-interpretations-vers-llm
- Evidence: E-013
- Expected rule: context names should match proven scope to avoid accidental broad ownership.
- Actual state: `astro_context` is built from astral-point interpretation context only in the inspected path.
- Impact: `astro_context` name suggests broad astrology context but evidence shows a narrower astral-point context.
- Recommended action: Do not change now; clarify ownership/name during LLM input convergence.
- Story candidate: no
- Suggested archetype: `needs-user-decision`
- Closure decision: no direct candidate because it is secondary to F-001.

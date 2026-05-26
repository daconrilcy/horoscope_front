# Finding Register - Pipeline Prompt LLM Natal

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | pipeline-prompt-llm-natal | E-006, E-008, E-013, E-019 | Natal LLM generation can remain based on a public/legacy projection while richer recent facts exist outside the prompt path. | Choose and wire one canonical narrative/factual LLM input owner, or record a user decision that public `chart_json` remains intentional. | yes |
| F-002 | Medium | High | runtime-contract-drift | pipeline-prompt-llm-natal | E-008, E-009, E-010, E-011 | Auditors and implementers can mistake runtime-carried fields for prompt-visible data. | Add a future guard or contract test that distinguishes prompt-visible fields from runtime-only fields. | yes |
| F-003 | Medium | High | duplicate-responsibility | pipeline-prompt-llm-natal | E-008, E-011, E-017 | Evidence validation can be mistaken for generation grounding, causing prompt changes to miss the real constraint path. | Define whether `evidence_catalog` remains validation-only or must be included in a future canonical prompt input contract. | yes |
| F-004 | Medium | Medium | legacy-surface | pipeline-prompt-llm-natal | E-003, E-005, E-006, E-020 | Historical `/users`, `free_short`, schema compatibility and fallback surfaces make branch behavior harder to reason about. | Classify each compatibility surface as intentional or removable before any implementation refactor. | yes |

## Finding Details

### F-001 - Current prompt path bypasses recent canonical interpretation owners

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: pipeline-prompt-llm-natal
- Evidence: E-006, E-008, E-013, E-019
- Expected rule: natal LLM prompt input should have one explicit owner for factual/narrative chart material, with recent canonical facts used deliberately or rejected by decision.
- Actual state: the scoped path assembles `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`; negative scan evidence shows no `structured_facts_v1`, `AINarrativeInput`, `ChartInterpretationInputBuilder` or `ChartObjectRuntimeData` in the path.
- Impact: Natal LLM generation can remain based on a public/legacy projection while richer recent facts exist outside the prompt path.
- Recommended action: Choose and wire one canonical narrative/factual LLM input owner, or record a user decision that public `chart_json` remains intentional.
- Story candidate: yes
- Suggested archetype: service-boundary-refactor

### F-002 - Runtime-carried fields are not prompt-visible by default

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: pipeline-prompt-llm-natal
- Evidence: E-008, E-009, E-010, E-011
- Expected rule: audit and future stories must distinguish data entering `LLMGateway` from data visible in the user message.
- Actual state: `build_user_payload` appends question/context and `Technical Data: {chart_json}` only when `chart_json_in_prompt` is false; other runtime fields do not become visible through this function.
- Impact: Auditors and implementers can mistake runtime-carried fields for prompt-visible data.
- Recommended action: Add a future guard or contract test that distinguishes prompt-visible fields from runtime-only fields.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-003 - Evidence catalog is validation material, not prompt grounding

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: pipeline-prompt-llm-natal
- Evidence: E-008, E-011, E-017
- Expected rule: evidence constraints must have a clear owner and stage: prompt input, output validation, or audit trail.
- Actual state: `evidence_catalog` is passed as execution flags and consumed by `validate_output`; no evidence shows it is injected into the user message.
- Impact: Evidence validation can be mistaken for generation grounding, causing prompt changes to miss the real constraint path.
- Recommended action: Define whether `evidence_catalog` remains validation-only or must be included in a future canonical prompt input contract.
- Story candidate: yes
- Suggested archetype: api-contract-change

### F-004 - Compatibility branches remain active in natal LLM path

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: pipeline-prompt-llm-natal
- Evidence: E-003, E-005, E-006, E-020
- Expected rule: compatibility routes, variants and fallback/schema branches must be explicitly classified before refactor work.
- Actual state: `/users` uses `free_short`, `free_short` maps to `natal_long_free`, complete output accepts v3/v3_error/v2/v1 compatibility, and prompt fallback guardrails remain relevant.
- Impact: Historical `/users`, `free_short`, schema compatibility and fallback surfaces make branch behavior harder to reason about.
- Recommended action: Classify each compatibility surface as intentional or removable before any implementation refactor.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal


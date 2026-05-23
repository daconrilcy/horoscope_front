# Finding Register - Astro Calculation Interpretation Boundary

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | astrology interpretation contract | E-008, E-009, E-014 | `ChartInterpretationInputRuntimeData` is a well-structured internal/pre-LLM contract, but the repository does not yet name which subshape is internal only, public-projection eligible, or LLM-contract stable. | Define an explicit `ChartInterpretationInput` internal/public/LLM contract split before exposing or reusing it outside interpretation services. | yes |
| F-002 | Medium | High | missing-canonical-owner | interpretation readiness | E-006, E-007, E-008, E-011 | Structural facts and interpretive signals exist, but there is no compact `interpretation-readiness` projection that tells downstream products which facts are safe to narrate, display, or withhold. | Add a deterministic readiness projection from structural facts with explicit owner, no LLM dependency, and no public raw-runtime exposure. | yes |
| F-003 | Medium | High | missing-guard | structural runtime narrative protection | E-012, E-013, E-014 | Existing architecture guards block many token names and provider dependencies, but they do not explicitly guard final-user narrative phrases such as `Vous avez...` or other localized text from entering structural runtime files. | Harden structural-runtime guards with lexical narrative-token checks and a no-wildcard allowlist for legitimate docs/tests only. | yes |
| F-004 | Low | Medium | legacy-surface | documentation and historical path references | E-017, E-018 | Older docs and prior audits still cite removed `backend/app/llm_orchestration` and `backend/app/prediction` paths, which can mislead future boundary audits if treated as current runtime evidence. | Keep historical docs as context, but future stories should cite current owners and mark old paths as historical-only. | no |

## Finding Details

### F-001 - ChartInterpretationInput contract ownership is not explicit enough

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: astrology interpretation contract
- Evidence: E-008, E-009, E-014
- Expected rule: `ChartInterpretationInputRuntimeData` must be clearly routed as internal contract, public contract candidate, or LLM input contract.
- Actual state: the contract is internal and fact-oriented, and guards prevent provider/calculator drift, but no source-backed decision separates internal-only fields from future public projections and LLM-stable fields.
- Impact: `ChartInterpretationInputRuntimeData` is a well-structured internal/pre-LLM contract, but the repository does not yet name which subshape is internal only, public-projection eligible, or LLM-contract stable.
- Recommended action: Define an explicit `ChartInterpretationInput` internal/public/LLM contract split before exposing or reusing it outside interpretation services.
- Story candidate: yes
- Suggested archetype: contract-shape
- Closure decision: closure-ready through CS-252.

### F-002 - Interpretation readiness projection is missing

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: interpretation readiness
- Evidence: E-006, E-007, E-008, E-011
- Expected rule: downstream product surfaces should consume a bounded projection that states what is interpretation-ready without recomputing or exposing raw runtime.
- Actual state: `interpretation_input` exists and daily prediction public projection exists, but no compact readiness owner bridges structural facts to product/LLM decisions.
- Impact: Structural facts and interpretive signals exist, but there is no compact `interpretation-readiness` projection that tells downstream products which facts are safe to narrate, display, or withhold.
- Recommended action: Add a deterministic readiness projection from structural facts with explicit owner, no LLM dependency, and no public raw-runtime exposure.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor
- Closure decision: closure-ready through CS-253.

### F-003 - Narrative-token guard is not lexical enough

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: structural runtime narrative protection
- Evidence: E-012, E-013, E-014
- Expected rule: structural runtime must reject final-user narrative text, not only known English identifier tokens such as `narrative`, `prompt` or `llm`.
- Actual state: current guards are valuable and broad, but a final phrase like `Vous avez une énergie de conquête` is not itself a watched token.
- Impact: Existing architecture guards block many token names and provider dependencies, but they do not explicitly guard final-user narrative phrases such as `Vous avez...` or other localized text from entering structural runtime files.
- Recommended action: Harden structural-runtime guards with lexical narrative-token checks and a no-wildcard allowlist for legitimate docs/tests only.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
- Closure decision: closure-ready through CS-254.

### F-004 - Historical namespace references need current-owner caveats

- Severity: Low
- Confidence: Medium
- Category: legacy-surface
- Domain: documentation and historical path references
- Evidence: E-017, E-018
- Expected rule: current boundary audits should not treat removed legacy namespaces as active runtime owners.
- Actual state: older prompt and prediction audits cite removed paths, while current filesystem and later docs prove those roots are gone.
- Impact: Older docs and prior audits still cite removed `backend/app/llm_orchestration` and `backend/app/prediction` paths, which can mislead future boundary audits if treated as current runtime evidence.
- Recommended action: Keep historical docs as context, but future stories should cite current owners and mark old paths as historical-only.
- Story candidate: no
- Suggested archetype: documentation-hygiene
- Closure decision: non-domain documentation hygiene.

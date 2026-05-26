# Finding Register - Configuration Prompts Placeholders Input Schema

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | backend-domain/llm-configuration | E-007, E-008, E-019, E-020 | Natal configuration cannot validate a modern structured astrology input because active schemas still require `chart_json` and no `llm_astrology_input` contract is declared in the scoped LLM path. | Create a future architecture/story candidate to declare a canonical structured input schema and map natal use cases to it. | yes |
| F-002 | Medium | High | legacy-surface | backend-domain/llm-runtime | E-012, E-013, E-016 | Runtime validation can satisfy `chart_json` from `natal_data` or parsed `chart_json`, preserving a legacy carrier and blurring data ownership. | Converge validation payload ownership after the target input contract is chosen; avoid adding another alias/fallback carrier. | yes |
| F-003 | Medium | High | missing-canonical-owner | backend-domain/llm-prompting | E-014, E-017, E-019, E-023 | Prompt rendering supports flat placeholders but no explicit multi-block astrology contract for facts, signals, limits and proofs. | Define structured block ownership in configuration/contract before prompt rewrites. | yes |
| F-004 | Medium | Medium | legacy-surface | backend-domain/llm-configuration | E-007, E-008, E-021, E-022 | Natal contracts and thematic modules keep fallback targets toward `natal_interpretation_short`; supported output fallback is blocked, but input-schema readiness still depends on legacy `chart_json`. | Treat this as legacy fallback context for the same contract convergence candidate; no separate code story until architecture is decided. | no |

## F-001 Detail

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: backend-domain/llm-configuration
- Evidence: E-007, E-008, E-019, E-020
- Expected rule: Active natal use cases should be able to declare and validate the target astrology input contract, or explicitly classify missing support.
- Actual state: Current natal contracts require `chart_json`; scoped LLM sources contain no `llm_astrology_input` or equivalent facts/signals/limits/proofs contract.
- Impact: Natal configuration cannot validate a modern structured astrology input because active schemas still require `chart_json` and no `llm_astrology_input` contract is declared in the scoped LLM path.
- Recommended action: Create a future architecture/story candidate to declare a canonical structured input schema and map natal use cases to it.
- Story candidate: yes
- Suggested archetype: contract-shape-audit follow-up / architecture-transition

## F-002 Detail

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: backend-domain/llm-runtime
- Evidence: E-012, E-013, E-016
- Expected rule: Input validation should validate the declared canonical input shape without silently substituting legacy carriers.
- Actual state: When `chart_json` is declared, gateway validation payload can use `natal_data`, dict `chart_json`, or parsed string `chart_json`.
- Impact: Runtime validation can satisfy `chart_json` from `natal_data` or parsed `chart_json`, preserving a legacy carrier and blurring data ownership.
- Recommended action: Converge validation payload ownership after the target input contract is chosen; avoid adding another alias/fallback carrier.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

## F-003 Detail

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-domain/llm-prompting
- Evidence: E-014, E-017, E-019, E-023
- Expected rule: Prompt configuration should identify the owner and validation mechanism for multiple structured astrology blocks.
- Actual state: `PromptRenderer` can render flat placeholders and context-quality blocks, while assembly preview only mocks `chart_json` and `natal_data` for natal.
- Impact: Prompt rendering supports flat placeholders but no explicit multi-block astrology contract for facts, signals, limits and proofs.
- Recommended action: Define structured block ownership in configuration/contract before prompt rewrites.
- Story candidate: yes
- Suggested archetype: prompt-placeholder-contract-convergence

## F-004 Detail

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: backend-domain/llm-configuration
- Evidence: E-007, E-008, E-021, E-022
- Expected rule: Legacy fallback should not be the mechanism that makes modern injection appear compatible.
- Actual state: Natal use cases have fallback targets toward `natal_interpretation_short`; runtime output fallback is blocked for supported features, but config readiness still falls back to `chart_json` contracts.
- Impact: Natal contracts and thematic modules keep fallback targets toward `natal_interpretation_short`; supported output fallback is blocked, but input-schema readiness still depends on legacy `chart_json`.
- Recommended action: Treat this as legacy fallback context for the same contract convergence candidate; no separate code story until architecture is decided.
- Story candidate: no
- Suggested archetype: legacy-context

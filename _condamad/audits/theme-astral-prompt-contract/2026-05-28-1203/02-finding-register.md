# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | security-risk | theme-astral-prompt-contract | E-004, E-005 | Commercial plan labels are visible in the provider payload and prompt-visible user content. | Replace prompt-visible `plan` with backend-owned delivery/feature profile fields in CS-363. | yes |
| F-002 | High | High | duplicate-responsibility | theme-astral-prompt-contract | E-004, E-006 | The same astrology input data appears in developer prompt material and user message payload. | Define one canonical provider data carrier in CS-363/CS-366. | yes |
| F-003 | Medium | High | runtime-contract-drift | theme-astral-prompt-contract | E-004, E-005 | The broad instability claim is partly wrong: keys are stable while message envelope and quantities diverge. | Preserve plan variability but formalize stable key/message policy. | yes |
| F-004 | Medium | High | boundary-violation | theme-astral-prompt-contract | E-005, E-007 | Backend-only audit/runtime families are represented in the provider payload artifact via exclusion list and mixed metadata. | Move exclusion registry and calculation metadata out of provider payload shape; split birth context. | yes |
| F-005 | Medium | High | runtime-contract-drift | theme-astral-prompt-contract | E-008 | `basic` provider prompt material contains premium-oriented instructions. | Add basic-vs-premium prompt guard and replace commercial wording with delivery profiles. | yes |

## F-001 Commercial plan is prompt/provider visible

- Severity: High
- Confidence: High
- Category: security-risk
- Domain: theme-astral-prompt-contract
- Evidence: E-004, E-005
- Expected rule: The model should receive delivery needs, not commercial package labels.
- Actual state: Each provider payload has top-level `plan`, and each parsed user payload has `shaping.plan` with `free`, `basic`, or `premium`.
- Impact: Commercial plan labels are visible in the provider payload and prompt-visible user content.
- Recommended action: Replace prompt-visible `plan` with backend-owned delivery/feature profile fields in CS-363.
- Story candidate: yes
- Suggested archetype: contract-shape-audit / provider-payload-builder-convergence.
- Closure mode: closure-ready through CS-363 architecture decision followed by CS-366 implementation.

## F-002 Developer/user duplicate the same input carrier

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: theme-astral-prompt-contract
- Evidence: E-004, E-006
- Expected rule: One canonical provider-visible carrier should own the chart facts and interpretation input.
- Actual state: The rendered developer prompt embeds the `llm_astrology_input_v1` data and the user message sends `llm_astrology_input_v1:` again.
- Impact: The same astrology input data appears in developer prompt material and user message payload.
- Recommended action: Define one canonical provider data carrier in CS-363/CS-366.
- Story candidate: yes
- Suggested archetype: provider-payload-builder-convergence.
- Closure mode: closure-ready after target contract and provider builder.

## F-003 Structure claim needs precise split between keys and quantities

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: theme-astral-prompt-contract
- Evidence: E-004, E-005
- Expected rule: Audit conclusions must distinguish key-shape drift from allowed value/cardinality variability.
- Actual state: Top-level and nested key families are stable, but message count and quantities differ strongly by plan.
- Impact: The broad instability claim is partly wrong: keys are stable while message envelope and quantities diverge.
- Recommended action: Preserve plan variability but formalize stable key/message policy.
- Story candidate: yes
- Suggested archetype: contract-shape-audit.
- Closure mode: closure-ready in architecture contract.

## F-004 Backend-only metadata is mixed into provider artifact shape

- Severity: Medium
- Confidence: High
- Category: boundary-violation
- Domain: theme-astral-prompt-contract
- Evidence: E-005, E-007
- Expected rule: Runtime, audit, hash, provenance, provider response, trace/debug and calculation metadata should remain backend-only unless explicitly needed by the model.
- Actual state: Audit/runtime exclusion entries are present in top-level payload artifacts; `source_metadata` is prompt-visible and includes calculation metadata.
- Impact: Backend-only audit/runtime families are represented in the provider payload artifact via exclusion list and mixed metadata.
- Recommended action: Move exclusion registry and calculation metadata out of provider payload shape; split birth context.
- Story candidate: yes
- Suggested archetype: provider-payload-builder-convergence / boundary-hardening.
- Closure mode: closure-ready through CS-363/CS-366.

## F-005 Basic prompt contains premium-oriented instructions

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: theme-astral-prompt-contract
- Evidence: E-008
- Expected rule: Basic plan prompt text should not include premium-only wording or density obligations.
- Actual state: Current basic prompt material contains premium-oriented language inherited from prompt seeds/provider output.
- Impact: `basic` provider prompt material contains premium-oriented instructions.
- Recommended action: Add basic-vs-premium prompt guard and replace commercial wording with delivery profiles.
- Story candidate: yes
- Suggested archetype: prompt-contract-guard-hardening.
- Closure mode: closure-ready through CS-363/CS-366 guard policy.

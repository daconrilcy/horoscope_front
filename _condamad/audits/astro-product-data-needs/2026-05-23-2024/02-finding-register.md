# Finding Register - Astro Product Data Needs

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | astro-product-data-needs | E-004, E-008, E-009, E-010, E-019 | Expert UI already renders several technical blocks from the public payload while adjacent audits classify raw runtime surfaces as internal; without an explicit expert contract, future fields can leak calculator internals by availability. | Define a dedicated expert natal chart public data contract that selects stable fields and excludes raw runtime owners. | yes |
| F-002 | High | High | missing-canonical-owner | astro-product-data-needs | E-006, E-007, E-008, E-013, E-015 | Beginner, public-user and AI interpretation needs are mixed across simple chart data, LLM interpretation, evidence IDs and entitlement states; the repo lacks one beginner summary projection owner. | Define a beginner natal summary projection with translated labels, compact evidence, masking rules and explicit no-raw-runtime scope. | yes |
| F-003 | Medium | High | missing-canonical-owner | astro-product-data-needs | E-004, E-007, E-009, E-012, E-016, E-017 | Fixed-star conjunctions exist in runtime/interpretation paths but are not a stable frontend display section in the natal client contract, creating product value without a public projection. | Add a dedicated fixed-star section projection candidate with strict field selection and translation requirements. | yes |
| F-004 | Medium | High | needs-user-decision | astro-product-data-needs | E-007, E-008, E-009, E-014, E-018 | Debug astrologique and interface astrologue needs overlap expert/public payload, persistence audit rows and potential operator diagnostics; repository evidence does not prove a protected debug product surface. | needs-user-decision | needs-user-decision |
| F-005 | Low | High | missing-guard | astro-product-data-needs | E-001, E-002, E-003, E-020, E-021 | No exact guardrail currently prevents product-data audits from becoming implementation changes or exposing raw internal astrology data by convenience, although this audit/review did verify no current forbidden app-code delta. | Keep this audit as evidence for future story-writer guard requirements; do not update application code in CS-244. | no |

## F-001 Expert Public Contract Is Not Explicit Enough

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-product-data-needs
- Evidence: E-004, E-008, E-009, E-010, E-019
- Expected rule: Expert screens must consume a stable public projection, not raw calculator/runtime objects or every field that happens to be serializable.
- Actual state: `NatalExpertPanel` renders public JSON blocks for dignities, advanced conditions, traditional conditions, condition profiles/signals, dominance and interpretation adapter, while `NatalResult` still contains explicitly internal raw runtime fields excluded from schema.
- Impact: Expert UI already renders several technical blocks from the public payload while adjacent audits classify raw runtime surfaces as internal; without an explicit expert contract, future fields can leak calculator internals by availability.
- Recommended action: Define a dedicated expert natal chart public data contract that selects stable fields and excludes raw runtime owners.
- Story candidate: yes
- Suggested archetype: contract-shape-audit-followup

## F-002 Beginner Summary Projection Has No Canonical Owner

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-product-data-needs
- Evidence: E-006, E-007, E-008, E-013, E-015
- Expected rule: Beginner and public-user screens need a compact, translated, stable summary projection that hides calculation complexity and separates evidence IDs from final text.
- Actual state: The simple screen consumes raw public chart fields and the interpretation flow uses LLM outputs/evidence, but no dedicated beginner summary projection is evidenced.
- Impact: Beginner, public-user and AI interpretation needs are mixed across simple chart data, LLM interpretation, evidence IDs and entitlement states; the repo lacks one beginner summary projection owner.
- Recommended action: Define a beginner natal summary projection with translated labels, compact evidence, masking rules and explicit no-raw-runtime scope.
- Story candidate: yes
- Suggested archetype: product-projection-contract

## F-003 Fixed-Star Display Projection Is Missing

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-product-data-needs
- Evidence: E-004, E-007, E-009, E-012, E-016, E-017
- Expected rule: A fixed-star product section needs a dedicated public shape with star name, target object, orb, significance fields and translation policy, separate from internal conjunction runtime.
- Actual state: Runtime and interpretation data for fixed-star contacts exists, but audited frontend natal client types do not expose a fixed-star section projection.
- Impact: Fixed-star conjunctions exist in runtime/interpretation paths but are not a stable frontend display section in the natal client contract, creating product value without a public projection.
- Recommended action: Add a dedicated fixed-star section projection candidate with strict field selection and translation requirements.
- Story candidate: yes
- Suggested archetype: product-projection-contract

## F-004 Debug And Astrologer Surface Needs A Product Decision

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: astro-product-data-needs
- Evidence: E-007, E-008, E-009, E-014, E-018
- Expected rule: Debug astrologique and interface astrologue data must have an explicit audience, authorization and masking decision before implementation.
- Actual state: Expert public payload, persisted audit/scoring evidence and PDF/interpretation data exist, but no protected debug or astrologer-specific natal diagnostic screen contract is evidenced.
- Impact: Debug astrologique and interface astrologue needs overlap expert/public payload, persistence audit rows and potential operator diagnostics; repository evidence does not prove a protected debug product surface.
- Recommended action: needs-user-decision
- Story candidate: needs-user-decision
- Suggested archetype: product-decision

## F-005 Product Data Audit Guardrail Gap

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: astro-product-data-needs
- Evidence: E-001, E-002, E-003, E-020, E-021
- Expected rule: Audit stories of form `cs-xxx-audit-*` stay documentation-only and guard against app-code deltas.
- Actual state: CS-244 includes a local no-app-delta rule and E-021 proves no current forbidden app-code delta, but the global guardrail registry has no exact product-data-needs invariant.
- Impact: No exact guardrail currently prevents product-data audits from becoming implementation changes or exposing raw internal astrology data by convenience, although this audit/review did verify no current forbidden app-code delta.
- Recommended action: Keep this audit as evidence for future story-writer guard requirements; do not update application code in CS-244.
- Story candidate: no
- Suggested archetype: guardrail-candidate

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | astrology-disclaimer-projection-policy | E-001, E-002, E-004, E-005, E-011 | B2C projection stories can only reference a story promise, not a durable policy or inventory, so plan attachment and text ownership remain non-auditable. | Create the canonical policy and evidence artifacts as a documentation-only story, or explicitly block dependent builders until it exists. | yes |
| F-002 | High | High | boundary-violation | astrology-disclaimer-projection-policy | E-006, E-007, E-009, E-012 | Guidance responses can preserve LLM-authored disclaimer text, contradicting the story rule that disclaimers are application-controlled. | Record this as a CS-284 policy gap and defer runtime guidance convergence to a separate service-boundary story after the canonical policy owner exists. | no |
| F-003 | Medium | High | missing-canonical-owner | astrology-disclaimer-projection-policy | E-001, E-002, E-008, E-010, E-011 | Degraded and missing birth time modes exist, but their client-visible disclaimer attachment is not mapped to B2C projection plans. | Extend the CS-284 policy to map degraded/no-time states to static disclaimer references or record a product gap with owner and next action. | yes |
| F-004 | Info | High | runtime-contract-drift | astrology-disclaimer-projection-policy | E-013, E-014, E-015 | No disclaimer-policy route or OpenAPI exposure is currently present; this preserves the story's API-neutral boundary. | Keep API neutrality as a validation guard for future CS-284 implementation. | no |

## F-001 Missing Canonical Policy And Inventory

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: astrology-disclaimer-projection-policy
- Evidence: E-001, E-002, E-004, E-005, E-011
- Expected rule: `astrology_disclaimer_projection_policy` must exist as the canonical backend-domain policy and must inventory backend, frontend, docs, usage classes, B2C plan attachment, LLM boundary, degraded/no-time coverage, and text-delta justification.
- Actual state: The policy document and CS-284 evidence artifacts are absent. Projection docs mention B2C plans and disclaimers only generically and do not name the CS-284 policy owner.
- Impact: B2C projection stories can only reference a story promise, not a durable policy or inventory, so plan attachment and text ownership remain non-auditable.
- Recommended action: Create the canonical policy and evidence artifacts as a documentation-only story, or explicitly block dependent builders until it exists.
- Story candidate: yes
- Suggested archetype: contract-shape-audit follow-up / documentation-policy-convergence

## F-002 Guidance Disclaimer Boundary Allows LLM Authorship

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: astrology-disclaimer-projection-policy
- Evidence: E-006, E-007, E-009, E-012
- Expected rule: Disclaimer text should be application-controlled and must not be authored, invented, rewritten, or mutated by LLM output.
- Actual state: `guidance_service.py` reads `disclaimer` and `disclaimers` from structured LLM output before applying a fallback; unit tests include LLM-provided disclaimer values.
- Impact: Guidance responses can preserve LLM-authored disclaimer text, contradicting the story rule that disclaimers are application-controlled.
- Recommended action: Record this as a CS-284 policy gap and defer runtime guidance convergence to a separate service-boundary story after the canonical policy owner exists.
- Story candidate: no
- Suggested archetype: service-boundary-refactor

## F-003 Degraded And Missing Birth Time Coverage Is Unmapped

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astrology-disclaimer-projection-policy
- Evidence: E-001, E-002, E-008, E-010, E-011
- Expected rule: Degraded mode and missing birth time must have explicit disclaimer coverage or a documented product gap with owner and next action.
- Actual state: `no_time`, `no_location`, and `no_location_no_time` modes exist and are persisted in natal responses, but no CS-284 policy maps these states to static disclaimer references per free/basic/premium projection plan.
- Impact: Degraded and missing birth time modes exist, but their client-visible disclaimer attachment is not mapped to B2C projection plans.
- Recommended action: Extend the CS-284 policy to map degraded/no-time states to static disclaimer references or record a product gap with owner and next action.
- Story candidate: yes
- Suggested archetype: contract-shape-audit follow-up / documentation-policy-convergence

## F-004 API Neutrality Currently Holds

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: astrology-disclaimer-projection-policy
- Evidence: E-013, E-014, E-015
- Expected rule: CS-284 must not add a public API route, OpenAPI schema, DB migration, or frontend surface.
- Actual state: Runtime OpenAPI and route scans show no `astrology_disclaimer_projection_policy` or `disclaimer-policy` route, and the architecture neutrality test passes.
- Impact: No disclaimer-policy route or OpenAPI exposure is currently present; this preserves the story's API-neutral boundary.
- Recommended action: Keep API neutrality as a validation guard for future CS-284 implementation.
- Story candidate: no
- Suggested archetype: runtime-contract-preservation

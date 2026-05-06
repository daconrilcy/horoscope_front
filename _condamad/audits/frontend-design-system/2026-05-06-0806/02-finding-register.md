<!-- Registre des findings pour l'audit frontend design-system. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006 | Current guardrails are executable and green. | Keep `RG-044` to `RG-050` mandatory for future frontend style stories. | no |
| F-002 | Medium | High | legacy-surface | frontend-design-system | E-009, E-010 | Compatibility and migration token namespaces remain active beside canonical tokens. | Converge aliases by namespace and update consumers/tests with before-after scans. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-design-system | E-011 | Local literals still compete with semantic tokens across broad CSS surfaces. | Migrate hardcoded values by coherent cluster and update token docs/guards when new tokens become durable. | yes |
| F-004 | Medium | Medium | needs-user-decision | frontend-design-system | E-012, E-013, E-014 | Admin prompts no longer has legacy selectors, but still exposes a runtime product concept named `legacy`. | Decide whether to rename the product surface or formally classify it as product-approved vocabulary. | yes |
| F-005 | Info | High | legacy-surface | frontend-design-system | E-015, E-016, E-017 | CSS fallback and inline-style debt is controlled and exact. | Keep existing allowlists exact; no cleanup story required for the two dynamic fallbacks. | no |
| F-006 | Low | High | observability-gap | frontend-performance | E-006 | Main JS chunk remains oversized despite green build. | Track separately in a frontend performance audit/story. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006
- Expected rule: frontend design-system changes remain protected by deterministic tests and lint/build checks.
- Actual state: focused guard tests, admin prompt tests, lint and build pass.
- Impact: Current guardrails are executable and green.
- Recommended action: Keep `RG-044` to `RG-050` mandatory for future frontend style stories.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-009, E-010
- Expected rule: canonical tokens own stable visual decisions; compatibility namespaces shrink over time.
- Actual state: compatibility/migration namespaces still have source declarations and consumers across app, admin, prediction, landing and tests.
- Impact: Compatibility and migration token namespaces remain active beside canonical tokens.
- Recommended action: Converge aliases by namespace and update consumers/tests with before-after scans.
- Story candidate: yes
- Suggested archetype: namespace-convergence

### F-003

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-011
- Expected rule: repeated visual decisions use semantic tokens or documented local semantic extensions.
- Actual state: many CSS files still contain literal colors, typography, spacing, radius and shadow values.
- Impact: Local literals still compete with semantic tokens across broad CSS surfaces.
- Recommended action: Migrate hardcoded values by coherent cluster and update token docs/guards when new tokens become durable.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-004

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: frontend-design-system
- Evidence: E-012, E-013, E-014
- Expected rule: removed legacy selectors should not leave ambiguous product/runtime ownership behind without a decision.
- Actual state: class selectors are canonicalized to archive/rollback, but state names, tab name, i18n copy, ARIA labels and tests still use `legacy`.
- Impact: Admin prompts no longer has legacy selectors, but still exposes a runtime product concept named `legacy`.
- Recommended action: Decide whether to rename the product surface or formally classify it as product-approved vocabulary.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-005

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-015, E-016, E-017
- Expected rule: fallbacks and inline styles are forbidden unless exact dynamic exceptions.
- Actual state: two fallback exceptions and five inline-style exceptions are exact and guarded.
- Impact: CSS fallback and inline-style debt is controlled and exact.
- Recommended action: Keep existing allowlists exact; no cleanup story required for the two dynamic fallbacks.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-006

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-006
- Expected rule: design-system cleanup should not hide a build performance warning.
- Actual state: build passes with Vite chunk-size warning.
- Impact: Main JS chunk remains oversized despite green build.
- Recommended action: Track separately in a frontend performance audit/story.
- Story candidate: no
- Suggested archetype: observability-audit

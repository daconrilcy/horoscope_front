<!-- Registre des constats de l'audit frontend design-system apres refactors CS-087 a CS-089. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-002, E-004, E-009 | Positive invariant: the frontend design-system guard suite remains active and passing after the refactors. | Keep `RG-044` through `RG-063` mandatory for any future frontend design-system story. | no |
| F-002 | Info | High | legacy-surface | frontend-design-system | E-006, E-007, E-009 | No active No Legacy, inline-style, or CSS fallback regression was found in the audited design-system scope. | Preserve exact allowlists and avoid broad compatibility exceptions in future changes. | no |
| F-003 | Info | High | duplicate-responsibility | frontend-design-system | E-003, E-004, E-005, E-008, E-009 | The previous exhaustive implementation list from `2026-05-07-2236` is now closed by targeted guards for `CS-087`, `CS-088`, and `CS-089`. | No application file modification is required for this audit. | no |
| F-004 | Low | High | observability-gap | frontend-performance | E-011, E-012 | Production build passes but the main JS chunk remains above Vite's warning threshold, which can hide future performance drift if not tracked separately. | Track code splitting or chunk budget in a separate frontend performance audit/story if product prioritizes it. | no |

## Finding Details

### F-001 - Design-system guard suite remains active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-002, E-004, E-009.
- Expected rule: frontend design-system refactors must be protected by deterministic guards.
- Actual state: guardrails `RG-044` through `RG-063` are present and the targeted guard suite passes.
- Impact: Positive invariant: the frontend design-system guard suite remains active and passing after the refactors.
- Recommended action: Keep `RG-044` through `RG-063` mandatory for any future frontend design-system story.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - No active inline-style, fallback, or No Legacy regression found

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-006, E-007, E-009.
- Expected rule: no unclassified inline style, CSS fallback, shim, alias, compatibility, or migration-only surface should remain in active design-system scope.
- Actual state: inline styles are exact dynamic exceptions; CSS fallbacks are limited to `--usage-progress`; No Legacy guards pass.
- Impact: No active No Legacy, inline-style, or CSS fallback regression was found in the audited design-system scope.
- Recommended action: Preserve exact allowlists and avoid broad compatibility exceptions in future changes.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-003 - Previous implementation list is closed

- Severity: Info
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-003, E-004, E-005, E-008, E-009.
- Expected rule: previously identified residual files should either be migrated or still listed as files to modify.
- Actual state: `App.css`, Help subscriptions, and premium shared surfaces now have story evidence and guards through `CS-087`, `CS-088`, and `CS-089`.
- Impact: The previous exhaustive implementation list from `2026-05-07-2236` is now closed by targeted guards for `CS-087`, `CS-088`, and `CS-089`.
- Recommended action: No application file modification is required for this audit.
- Story candidate: no
- Suggested archetype: design-system-token-convergence

### F-004 - Build still reports a bundle-size warning

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-011, E-012.
- Expected rule: build should pass and performance warnings should be classified.
- Actual state: build passes, but Vite reports a main JS chunk above `500 kB`.
- Impact: Production build passes but the main JS chunk remains above Vite's warning threshold, which can hide future performance drift if not tracked separately.
- Recommended action: Track code splitting or chunk budget in a separate frontend performance audit/story if product prioritizes it.
- Story candidate: no
- Suggested archetype: observability-audit

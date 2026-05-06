<!-- Registre des constats de l'audit frontend design-system apres refactors. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-002, E-003, E-005, E-006, E-007, E-008 | The current frontend design-system guard suite is executable and green after the latest refactors. | Keep `RG-044` to `RG-055` mandatory for future frontend style and compatibility stories. | no |
| F-002 | Medium | High | duplicate-responsibility | frontend-design-system | E-010 | 101 non-test application files still contain hardcoded visual or typography values, so local declarations continue to compete with token ownership. | Continue bounded hardcoded-value migrations by coherent product clusters, with before/after inventories and focused tests. | yes |
| F-003 | Medium | Medium | legacy-surface | frontend-compatibility | E-009 | Five frontend runtime/i18n files still expose explicit legacy or backward-compatibility branches without a shared compatibility registry and exit decision. | Classify each compatibility path as product-approved, removable, or time-boxed; remove stale paths and add exact guard coverage for kept ones. | yes |
| F-004 | Low | High | observability-gap | frontend-performance | E-004 | Build passes but the main JS chunk remains oversized, which can mask performance drift behind otherwise green design-system checks. | Track code splitting in a separate frontend performance story; keep it outside the design-system cleanup stories unless a touched cluster affects bundling. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-002, E-003, E-005, E-006, E-007, E-008
- Expected rule: design-system ownership, No Legacy guards, page-scoped token boundaries, inline-style exceptions, fallback exceptions and admin route removals must remain executable.
- Actual state: focused frontend guards, lint, token scans, fallback scans, inline-style scans and legacy admin route scans pass.
- Impact: The current frontend design-system guard suite is executable and green after the latest refactors.
- Recommended action: Keep `RG-044` to `RG-055` mandatory for future frontend style and compatibility stories.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-010
- Expected rule: semantic tokens and typography roles should own repeated visual decisions; page/component CSS should not keep broad local literal ownership unless intentionally scoped.
- Actual state: 101 non-test application files outside `src/styles/**` still match hardcoded visual or typography literals.
- Impact: 101 non-test application files still contain hardcoded visual or typography values, so local declarations continue to compete with token ownership.
- Recommended action: Continue bounded hardcoded-value migrations by coherent product clusters, with before/after inventories and focused tests.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: frontend-compatibility
- Evidence: E-009
- Expected rule: active compatibility branches should have an owner, canonical replacement and exit condition, or be explicitly approved product vocabulary.
- Actual state: five runtime/i18n files still contain explicit legacy or backward-compatibility wording or branches.
- Impact: Five frontend runtime/i18n files still expose explicit legacy or backward-compatibility branches without a shared compatibility registry and exit decision.
- Recommended action: Classify each compatibility path as product-approved, removable, or time-boxed; remove stale paths and add exact guard coverage for kept ones.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-004

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-004
- Expected rule: build output should remain visible during audit so large bundle drift is not hidden by green functional guards.
- Actual state: build passes with Vite's chunk-size warning for `assets/index-B8KurGJa.js` at 1,371.35 kB.
- Impact: Build passes but the main JS chunk remains oversized, which can mask performance drift behind otherwise green design-system checks.
- Recommended action: Track code splitting in a separate frontend performance story; keep it outside the design-system cleanup stories unless a touched cluster affects bundling.
- Story candidate: no
- Suggested archetype: observability-audit

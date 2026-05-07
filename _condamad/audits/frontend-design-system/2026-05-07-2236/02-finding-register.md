<!-- Registre des constats de l'audit frontend design-system apres refactors CS-080 a CS-086. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-004, E-005, E-006, E-007, E-009 | The implemented design-system guard suite is active and passing after refactors. | Keep these commands mandatory for every frontend design-system story. | no |
| F-002 | High | High | duplicate-responsibility | frontend-design-system | E-008, E-011, E-012 | `App.css` remains a broad local owner of visual and typography values, with 561 scan hits outside a fully closed exact guard. | Create a bounded App shell/catalogue/dashboard visual-token convergence story. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-design-system | E-004, E-008, E-012 | `HelpPage.css` still contains a large subscriptions/help marketing sub-surface with local hardcoded values after the earlier Help guard. | Create a focused Help subscriptions visual-token convergence story. | yes |
| F-004 | Medium | High | missing-canonical-owner | frontend-design-system | E-008, E-011, E-012 | shared background/glass and daily premium CSS still split visual decisions across local literals and premium/page tokens. | Create a shared premium surfaces convergence story covering the exact four files. | yes |
| F-005 | Info | High | legacy-surface | frontend-design-system | E-002, E-004, E-005, E-009, E-010 | No new active CSS No Legacy regression was found in the design-system scope. | Preserve `RG-044` through `RG-060`; do not reopen compatibility aliases. | no |
| F-006 | Low | High | observability-gap | frontend-performance | E-007 | Production build still emits a main-bundle size warning, outside design-system ownership. | Track in a separate frontend performance audit/story if prioritized. | no |

## Finding Details

### F-001 - Design-system guard suite remains active

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-004, E-005, E-006, E-007, E-009.
- Expected rule: design-system constraints must be executable after refactors.
- Actual state: targeted guard tests, lint, and build pass.
- Impact: The implemented design-system guard suite is active and passing after refactors.
- Recommended action: Keep these commands mandatory for every frontend design-system story.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002 - `App.css` remains a broad local visual/typography owner

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-008, E-011, E-012.
- Expected rule: repeated visual and typography decisions should be owned by tokens, typography roles, or explicitly documented page/component namespaces with exact anti-return guards.
- Actual state: `frontend/src/App.css` still has 561 hardcoded visual/type scan hits. The registry classifies `--app-*`, but the current `CS-082` guard only covers selected App values and leaves broader App sections unclosed.
- Impact: `App.css` remains a broad local owner of visual and typography values, with 561 scan hits outside a fully closed exact guard.
- Recommended action: Create a bounded App shell/catalogue/dashboard visual-token convergence story.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-003 - `HelpPage.css` subscription surface remains locally hardcoded

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-004, E-008, E-012.
- Expected rule: Help page visual decisions should be covered by `--help-*` semantic tokens or global tokens with an exact anti-return guard.
- Actual state: `frontend/src/pages/HelpPage.css` still has 300 hardcoded visual/type scan hits. Existing guard logic explicitly protects the earlier Help section and stops before the subscriptions section.
- Impact: `HelpPage.css` still contains a large subscriptions/help marketing sub-surface with local hardcoded values after the earlier Help guard.
- Recommended action: Create a focused Help subscriptions visual-token convergence story.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-004 - Shared premium background/glass decisions still lack a single owner

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-008, E-011, E-012.
- Expected rule: shared background/glass/premium surface values should be owned by global or premium semantic tokens and guarded against local literal return.
- Actual state: local literals remain in `frontend/src/styles/backgrounds.css`, `frontend/src/styles/glass.css`, `frontend/src/pages/DailyHoroscopePage.css`, and `frontend/src/components/prediction/DailyAdviceCard.css`.
- Impact: shared background/glass and daily premium CSS still split visual decisions across local literals and premium/page tokens.
- Recommended action: Create a shared premium surfaces convergence story covering the exact four files.
- Story candidate: yes
- Suggested archetype: design-system-token-convergence

### F-005 - No new CSS No Legacy regression found

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-002, E-004, E-005, E-009, E-010.
- Expected rule: removed compatibility, legacy, alias, shim, and migration-only CSS surfaces must not return.
- Actual state: CSS-focused guards pass. Vocabulary scan hits outside CSS are runtime/product vocabulary and outside this bounded CSS design-system audit.
- Impact: No new active CSS No Legacy regression was found in the design-system scope.
- Recommended action: Preserve `RG-044` through `RG-060`; do not reopen compatibility aliases.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-006 - Build still reports a bundle-size warning

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-007.
- Expected rule: build warnings should be tracked in the correct domain.
- Actual state: build passes, but Vite warns that the main JS chunk is larger than 500 kB after minification.
- Impact: Production build still emits a main-bundle size warning, outside design-system ownership.
- Recommended action: Track in a separate frontend performance audit/story if prioritized.
- Story candidate: no
- Suggested archetype: observability-audit

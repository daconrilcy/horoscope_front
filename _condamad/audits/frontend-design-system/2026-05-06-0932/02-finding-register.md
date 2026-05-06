<!-- Registre des findings pour l'audit frontend design-system. -->

# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Info | High | missing-guard | frontend-design-system | E-001, E-002, E-003, E-004, E-005, E-006, E-018 | The current frontend design-system guard suite is executable and green after the refactors. | Keep `RG-044` to `RG-050` mandatory for every future frontend style story. | no |
| F-002 | Info | High | legacy-surface | frontend-design-system | E-009, E-010 | CSS fallback debt is reduced to two exact dynamic bridges and no longer needs a cleanup story by itself. | Keep the fallback registry and TS allowlist exact; only revisit if `--usage-progress` ownership changes. | no |
| F-003 | Info | High | legacy-surface | frontend-design-system | E-011, E-012 | Inline style debt is reduced to five exact dynamic/style-prop exceptions and is guarded. | Keep the inline-style allowlist exact; future removals should move only non-runtime styling to CSS. | no |
| F-004 | Medium | High | duplicate-responsibility | frontend-design-system | E-014 | Local hardcoded colors, spacing, radius, shadow, and typography values still compete with semantic token ownership across broad application CSS/TSX surfaces. | Continue bounded hardcoded-value migration by coherent product clusters with before/after inventories and focused visual tests. | yes |
| F-005 | Medium | High | legacy-surface | frontend-design-system | E-015, E-016 | `.astrologer-card-alias` remains an active alias-named CSS surface without registry classification, so alias debt can survive the legacy-style guard. | Rename the class to canonical vocabulary or register it with owner, target, and exit condition; strengthen the guard to classify alias-named selectors too. | yes |
| F-006 | Medium | Medium | needs-user-decision | frontend-design-system | E-017 | Consultation i18n still exposes user-visible `(Legacy)` labels outside the admin prompts refactor scope; this may be product-approved compatibility wording or stale vocabulary. | Ask for a product decision, then either rename the labels/tests or classify them as approved compatibility copy. | yes |
| F-007 | Low | High | observability-gap | frontend-performance | E-008 | Build passes but the main JS chunk remains oversized, which can hide performance regression behind otherwise green design-system validation. | Track in a separate frontend performance audit/story with bundle analysis and code-splitting scope. | no |

## Finding Details

### F-001

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-018
- Expected rule: design-system governance is protected by executable guardrails and future stories cite `RG-044` to `RG-050`.
- Actual state: targeted guard tests and admin prompts regression tests pass after the refactors.
- Impact: The current frontend design-system guard suite is executable and green after the refactors.
- Recommended action: Keep `RG-044` to `RG-050` mandatory for every future frontend style story.
- Story candidate: no
- Suggested archetype: test-guard-coverage-audit

### F-002

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-009, E-010
- Expected rule: CSS fallbacks are absent unless exact runtime exceptions are classified in both registry and executable allowlist.
- Actual state: only `--usage-progress` remains as two dynamic fallback bridges, and both are classified.
- Impact: CSS fallback debt is reduced to two exact dynamic bridges and no longer needs a cleanup story by itself.
- Recommended action: Keep the fallback registry and TS allowlist exact; only revisit if `--usage-progress` ownership changes.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-003

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-011, E-012
- Expected rule: TSX inline styles are absent unless exact runtime geometry, CSS custom property, or style-prop bridge exceptions are classified.
- Actual state: five inline style hits remain and match `INLINE_STYLE_EXCEPTIONS`.
- Impact: Inline style debt is reduced to five exact dynamic/style-prop exceptions and is guarded.
- Recommended action: Keep the inline-style allowlist exact; future removals should move only non-runtime styling to CSS.
- Story candidate: no
- Suggested archetype: legacy-surface-audit

### F-004

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-014
- Expected rule: repeated visual decisions should use semantic tokens or documented local semantic extensions.
- Actual state: 106 application files outside token-owner CSS files still contain hardcoded visual or typography values.
- Impact: Local hardcoded colors, spacing, radius, shadow, and typography values still compete with semantic token ownership across broad application CSS/TSX surfaces.
- Recommended action: Continue bounded hardcoded-value migration by coherent product clusters with before/after inventories and focused visual tests.
- Story candidate: yes
- Suggested archetype: duplicate-rule-removal

### F-005

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-015, E-016
- Expected rule: legacy, compatibility, and alias style surfaces must be removed or explicitly classified with owner, canonical target, and exit condition.
- Actual state: `.astrologer-card-alias` exists in `App.css` and is consumed by `AstrologerCard.tsx`, while `legacy-style-surface-registry.md` has no entries.
- Impact: `.astrologer-card-alias` remains an active alias-named CSS surface without registry classification, so alias debt can survive the legacy-style guard.
- Recommended action: Rename the class to canonical vocabulary or register it with owner, target, and exit condition; strengthen the guard to classify alias-named selectors too.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-006

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: frontend-design-system
- Evidence: E-017
- Expected rule: user-visible `legacy` vocabulary is either removed after migration or explicitly product-approved.
- Actual state: `frontend/src/i18n/consultations.ts` still contains `(Legacy)` labels for consultation choices outside the admin prompts scope.
- Impact: Consultation i18n still exposes user-visible `(Legacy)` labels outside the admin prompts refactor scope; this may be product-approved compatibility wording or stale vocabulary.
- Recommended action: Ask for a product decision, then either rename the labels/tests or classify them as approved compatibility copy.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-007

- Severity: Low
- Confidence: High
- Category: observability-gap
- Domain: frontend-performance
- Evidence: E-008
- Expected rule: design-system validation should surface build-performance warnings separately from style-governance status.
- Actual state: `npm run build` passes but Vite warns that the main chunk is larger than 500 kB after minification.
- Impact: Build passes but the main JS chunk remains oversized, which can hide performance regression behind otherwise green design-system validation.
- Recommended action: Track in a separate frontend performance audit/story with bundle analysis and code-splitting scope.
- Story candidate: no
- Suggested archetype: observability-audit

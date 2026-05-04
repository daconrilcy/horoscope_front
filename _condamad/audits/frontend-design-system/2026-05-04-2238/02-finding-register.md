# Finding Register - frontend-design-system

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | frontend-design-system | E-002, E-010, E-012 | Multiple token families act as design authorities, so new UI can choose different source truths for the same semantic decisions. | Define one canonical token contract under `frontend/src/styles/design-tokens.css`, classify `theme.css`, `premium-theme.css`, `settings`, `landing`, and legacy aliases as canonical, compatibility, or migration-only, then add an enforcement guard. | yes |
| F-002 | High | High | duplicate-responsibility | frontend-design-system | E-003, E-008, E-009 | Repeated white glass, purple accent, status, shadow, spacing, and radius values duplicate token responsibilities across product surfaces. | Consolidate repeated values into semantic tokens for surface, border, elevation, interactive, status, spacing, radius, and typography scales; migrate by surface priority. | yes |
| F-003 | Medium | High | duplicate-responsibility | frontend-design-system | E-005, E-008 | Typography hierarchy is not enforced: font sizes, weights, line heights, and letter spacing are repeated directly with mixed px and rem scales. | Create semantic text tokens or utility classes for page title, section title, card title, body, metadata, label, eyebrow, and button text; migrate repeated literal declarations. | yes |
| F-004 | Medium | High | missing-guard | frontend-design-system | E-006, E-011 | Inline styles bypass the CSS-only project rule and make chart/aesthetic values harder to theme or audit. | Classify inline styles into allowed dynamic exceptions and forbidden static styling; add a test or lint scan that fails on new non-allowlisted static inline styles. | yes |
| F-005 | Medium | High | missing-guard | frontend-design-system | E-007, E-011 | Token fallback values can silently become alternate tokens and keep stale approximations alive after central tokens change. | Replace generic fallback usage with required canonical tokens or documented compatibility aliases; add a guard for disallowed fallbacks in app CSS. | yes |
| F-006 | Medium | Medium | legacy-surface | frontend-design-system | E-009, E-012 | Legacy class names and compatibility aliases remain active in large CSS files, obscuring current ownership and increasing migration risk. | Inventory active legacy CSS surfaces and either rename, remove, or mark them as migration-only with exact allowed selectors. | yes |
| F-007 | Low | High | missing-test-coverage | frontend-design-system | E-011 | Existing token tests validate selected values but not architectural drift in design-token usage. | Add static tests for hardcoded colors, spacing, radius, typography, token fallbacks, and inline style policy after the first migration allowlist is defined. | yes |

## F-001 - Canonical token ownership is unclear

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-design-system
- Evidence: E-002, E-010, E-012 show `design-tokens.css`, `theme.css`, `premium-theme.css`, page-scoped `--settings-*`, `--landing-*`, aliases such as `--text-1`, and local aliases such as `--text-main` all acting as token authorities.
- Expected rule: One canonical source defines design decisions; compatibility layers only map old names to canonical tokens and are guarded.
- Actual state: Several token namespaces coexist without documented status or enforcement.
- Impact: Multiple token families act as design authorities, so new UI can choose different source truths for the same semantic decisions.
- Recommended action: Define one canonical token contract under `frontend/src/styles/design-tokens.css`, classify `theme.css`, `premium-theme.css`, `settings`, `landing`, and legacy aliases as canonical, compatibility, or migration-only, then add an enforcement guard.
- Story candidate: yes
- Suggested archetype: design-token-ownership-convergence

## F-002 - Repeated hardcoded values duplicate token responsibilities

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-003, E-008, E-009 show 1696 color occurrences outside token source files and repeated values such as white glass alphas, purple accent alphas, pill radii, and repeated gaps.
- Expected rule: Repeated design values are represented by semantic tokens or controlled utilities.
- Actual state: Repeated approximate values are embedded across large CSS files and component/page styles.
- Impact: Repeated white glass, purple accent, status, shadow, spacing, and radius values duplicate token responsibilities across product surfaces.
- Recommended action: Consolidate repeated values into semantic tokens for surface, border, elevation, interactive, status, spacing, radius, and typography scales; migrate by surface priority.
- Story candidate: yes
- Suggested archetype: hardcoded-design-value-convergence

## F-003 - Typography hierarchy is not centralized

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-design-system
- Evidence: E-005, E-008 show 1393 non-tokenized typography declarations, including repeated weights 700 and 600, many px font sizes, rem sizes, line heights, and letter spacing.
- Expected rule: Text hierarchy uses named roles rather than local numeric decisions.
- Actual state: Pages and components choose type sizes and weights directly.
- Impact: Typography hierarchy is not enforced: font sizes, weights, line heights, and letter spacing are repeated directly with mixed px and rem scales.
- Recommended action: Create semantic text tokens or utility classes for page title, section title, card title, body, metadata, label, eyebrow, and button text; migrate repeated literal declarations.
- Story candidate: yes
- Suggested archetype: typography-scale-convergence

## F-004 - Static inline styles bypass the stylesheet rule

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-006, E-011 show 90 `style` attributes, including static layout and typography examples in `SettingsLayout.tsx`, `AstrologerCard.tsx`, `DeleteAccountModal.tsx`, `TurningPointsList.tsx`, `PrivacyPolicyPage.tsx`, `AccountSettings.tsx`, and `NotFoundPage.tsx`.
- Expected rule: Static styling lives in CSS files; inline styles are reserved for explicit dynamic CSS variables or calculated geometry.
- Actual state: Static CSS declarations are mixed into TSX.
- Impact: Inline styles bypass the CSS-only project rule and make chart/aesthetic values harder to theme or audit.
- Recommended action: Classify inline styles into allowed dynamic exceptions and forbidden static styling; add a test or lint scan that fails on new non-allowlisted static inline styles.
- Story candidate: yes
- Suggested archetype: inline-style-policy-guard

## F-005 - CSS variable fallbacks preserve stale approximations

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-design-system
- Evidence: E-007, E-011 show 329 fallback usages, including fallback values for colors, radii, spacing, shadows, and undefined or page-specific tokens.
- Expected rule: Fallbacks are rare, documented compatibility exceptions.
- Actual state: Fallbacks are widespread and can behave as alternate source values.
- Impact: Token fallback values can silently become alternate tokens and keep stale approximations alive after central tokens change.
- Recommended action: Replace generic fallback usage with required canonical tokens or documented compatibility aliases; add a guard for disallowed fallbacks in app CSS.
- Story candidate: yes
- Suggested archetype: token-fallback-hardening

## F-006 - Legacy and compatibility style surfaces remain active

- Severity: Medium
- Confidence: Medium
- Category: legacy-surface
- Domain: frontend-design-system
- Evidence: E-009, E-012 show very large CSS files and active legacy names such as `chat-layout-legacy`, `conversation-item-legacy`, compatibility aliases in `theme.css`, and local aliases in `DailyHoroscopePage.css`.
- Expected rule: Legacy style surfaces are removed or exactly classified with canonical replacements.
- Actual state: Legacy names and compatibility aliases are still active and not tied to a migration registry.
- Impact: Legacy class names and compatibility aliases remain active in large CSS files, obscuring current ownership and increasing migration risk.
- Recommended action: Inventory active legacy CSS surfaces and either rename, remove, or mark them as migration-only with exact allowed selectors.
- Story candidate: yes
- Suggested archetype: legacy-style-surface-classification

## F-007 - Design-system drift is not guarded

- Severity: Low
- Confidence: High
- Category: missing-test-coverage
- Domain: frontend-design-system
- Evidence: E-011 shows `theme-tokens.test.ts` validates selected token values but does not ban new hardcoded colors, spacing, radii, typography, fallbacks, or static inline styles.
- Expected rule: A repeatable guard prevents new drift after cleanup.
- Actual state: Token value tests exist, but usage-discipline tests are missing.
- Impact: Existing token tests validate selected values but not architectural drift in design-token usage.
- Recommended action: Add static tests for hardcoded colors, spacing, radius, typography, token fallbacks, and inline style policy after the first migration allowlist is defined.
- Story candidate: yes
- Suggested archetype: design-system-regression-guard

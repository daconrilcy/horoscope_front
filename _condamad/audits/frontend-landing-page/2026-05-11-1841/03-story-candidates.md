# Story Candidates - frontend-landing-page - 2026-05-11-1841

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Simplifier la composition visuelle du hero landing | frontend-visual-simplification | frontend-landing-page | none |
| SC-002 | F-002 | Clarifier le contrat visuel landing light/dark et menu mobile | design-system-convergence | frontend-landing-page | none |
| SC-003 | F-003 | Ajouter une garde anti-complexite visuelle landing | test-guard-hardening | frontend-landing-page | none |

## SC-001 - Simplifier la composition visuelle du hero landing

- Candidate ID: SC-001
- Source finding: F-001
- Source finding ID: F-001
- Suggested story title: Simplifier la composition visuelle du hero landing
- Suggested archetype: frontend-visual-simplification
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, RG-083, RG-084, RG-085, RG-086, RG-087
- Draft objective: reduce hero preview CSS complexity while preserving the current marketing message, CTAs, analytics events and route ownership.
- Closure intent: full-closure
- Must include:
  - Reduce always-running hero motion to at most one named CSS animation family, or remove it.
  - Remove unused active-state variables such as shadow variants that no current selector consumes after simplification.
  - Keep `HeroSection.tsx` free of timers and inline styles.
  - Preserve `hero_cta_click`, `secondary_cta_click`, accessibility labels and responsive layout.
  - Avoid new dependencies, canvas, WebGL or image-only decorative replacements.
- Expected Files To Modify:
  - `frontend/src/pages/landing/sections/HeroSection.tsx`
  - `frontend/src/pages/landing/LandingPage.css`
  - `frontend/src/tests/LandingPage.test.tsx` only if DOM expectations change.
  - `frontend/src/tests/visual-smoke.test.tsx` for hero complexity expectations.
  - `frontend/src/tests/design-system-guards.test.ts` only if owner declarations move.
- Required before/after evidence:
  - Screenshot set matching this audit's `screenshots/*top.png`.
  - Count of `@keyframes`, `animation:` and runtime animated hero descendants before/after.
  - `rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" src/pages/landing`.
  - `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`.
  - `npm run lint`.
- Validation hints:
  - Record Playwright `scrollWidth === clientWidth` at 390px and 1440px.
  - Compare screenshots in light and dark; hero preview should read as one product signal, not a stack of competing cards.
- Blockers / user decision: none.
- Allowlist / No Legacy policy:
  - No wildcard allowlist.
  - Any retained animation must be named explicitly in a guard or story artifact.
- Stop condition:
  - Hero CSS no longer has broad residual animation/filter complexity; any retained motion is named, counted and guarded.
- Expected file/surface classification changes:
  - `LandingPage.css` remains `used`, with narrower hero owner responsibilities.
  - No file should move to `delete-candidate` unless its import/usage scan is zero and the story records a replacement.

## SC-002 - Clarifier le contrat visuel landing light/dark et menu mobile

- Candidate ID: SC-002
- Source finding: F-002
- Source finding ID: F-002
- Suggested story title: Clarifier le contrat visuel landing light/dark et menu mobile
- Suggested archetype: design-system-convergence
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, RG-083, RG-084, RG-085, RG-086, RG-087
- Draft objective: make the landing light and dark themes feel like paired variants of the same interface, with a quieter mobile menu and fewer competing translucent/glow effects.
- Closure intent: full-closure
- Must include:
  - Define a small visual role set for landing cards and mobile menu: primary surface, secondary surface, border, text, muted text, CTA.
  - Remove or drastically reduce the large blurred glow visible behind the mobile menu in both themes.
  - Keep global background ownership unchanged: no `app-bg--landing`, no page-level background variant.
  - Keep dark starfield dark-only.
  - Do not add inline styles.
- Expected Files To Modify:
  - `frontend/src/layouts/LandingLayout.css`
  - `frontend/src/pages/landing/LandingPage.css` only for hero/card role consumption.
  - `frontend/src/pages/landing/sections/LandingNavbar.css`
  - Section CSS files only when they consume a role being renamed or narrowed:
    - `frontend/src/pages/landing/sections/FaqSection.css`
    - `frontend/src/pages/landing/sections/PricingSection.css`
    - `frontend/src/pages/landing/sections/ProblemSection.css`
    - `frontend/src/pages/landing/sections/SocialProofSection.css`
    - `frontend/src/pages/landing/sections/SolutionSection.css`
    - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`
- Required before/after evidence:
  - Screenshot set: desktop light/dark top and mid, mobile light/dark top, mobile menu light/dark.
  - Runtime metrics: `scrollWidth === clientWidth`, `.landing-layout .landing-page` present, `app-bg--landing=false`.
  - Spot contrast for hero title/body, menu links, CTA, and section card copy in both themes.
  - Scan `rg -n "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css`.
  - `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`.
  - `npm run lint`.
- Validation hints:
  - Current `screenshots/mobile-light-menu.png` and `mobile-dark-menu.png` are the clearest before artifacts for the mobile menu issue.
  - The target state should reduce visual noise without flattening all surfaces into the same tone.
- Blockers / user decision: none.
- Allowlist / No Legacy policy:
  - No wildcard owner group or broad folder exception.
  - New `--landing-*` group names must be added to the finite owner map only if they define a durable semantic role.
- Stop condition:
  - Light/dark screenshots show the same hierarchy; mobile menu has no dominating unowned blur/glow; no new background mount is introduced.
- Expected file/surface classification changes:
  - CSS files remain `used`.
  - Any removed variable is proven by source diff and guard update; no compatibility alias remains.

## SC-003 - Ajouter une garde anti-complexite visuelle landing

- Candidate ID: SC-003
- Source finding: F-003
- Source finding ID: F-003
- Suggested story title: Ajouter une garde anti-complexite visuelle landing
- Suggested archetype: test-guard-hardening
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, RG-083, RG-084, RG-085, RG-086, RG-087
- Draft objective: prevent reintroduction of unbounded landing CSS motion/filter complexity after simplification.
- Closure intent: full-closure
- Must include:
  - Add exact checks for landing `@keyframes`, `animation:` declarations and always-on `backdrop-filter` usage.
  - Classify any retained exceptions by selector and reason.
  - Keep existing finite owner group guard.
  - Do not create broad path-level allowlists.
- Expected Files To Modify:
  - `frontend/src/tests/design-system-guards.test.ts` or a focused `frontend/src/tests/landing-visual-complexity.test.ts`.
  - Optional exact allowlist file only if it contains selector-level entries and exit conditions.
  - No application CSS file is required unless SC-001/SC-002 is combined.
- Required before/after evidence:
  - Failing/then passing guard evidence if implemented after simplification.
  - `npm run test -- design-system visual-smoke LandingPage`.
  - Source scan showing exact allowed animation/filter selectors.
- Validation hints:
  - Guard should fail on a new unclassified `@keyframes` or infinite `animation:` in `frontend/src/pages/landing/**/*.css`.
  - Guard should not ban hover/focus transitions globally.
- Blockers / user decision: none.
- Allowlist / No Legacy policy:
  - Selector-level exact allowlist only.
  - No wildcard animation or filter allowance.
- Stop condition:
  - Current or simplified landing motion/filter budget is executable and fails on unclassified growth.
- Expected file/surface classification changes:
  - New test file, if created, is `test-only`.

## Deferred Non-Domain Context

- None. All active findings are inside the landing frontend domain.

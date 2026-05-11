# Story Candidates - frontend-landing-page

| Candidate ID | Source finding ID | Suggested story title | Suggested archetype | Primary domain | Blockers / user decision |
|---|---|---|---|---|---|
| SC-001 | F-001 | Refactoriser l'ownership CSS landing | design-system-convergence | frontend-landing-page | none |
| SC-002 | F-002 | Aligner les themes visuels landing light/dark | design-system-convergence | frontend-landing-page | SC-001 owner map should land first, or SC-002 must include it. |
| SC-003 | F-003 | Simplifier le hero preview de la landing | runtime-simplification | frontend-landing-page | none |
| SC-004 | F-004 | Extraire le proprietaire SEO/head de la landing | ownership-routing-refactor | frontend-landing-page | none |

## SC-001 - Refactoriser l'ownership CSS landing

- Source finding: F-001
- Suggested story title: Refactoriser l'ownership CSS landing
- Suggested archetype: design-system-convergence
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, frontend design-system guardrails, RG-083, RG-084, RG-086, RG-087
- Draft objective: turn the current dense landing namespace into a finite visual model with grouped surface, type, nav, hero, mobile and section composition owners.
- Must include: keep `RootLayout` and `LandingLayout` route ownership unchanged; no `app-bg--landing`; no page-level background variant; no inline styles; reduce `LandingLayout.css` ownership to grouped landing primitives; preserve copy and route behavior; leave final light/dark tuning to SC-002 unless it is a direct consequence of the owner split.
- Validation hints: scan count of `--landing-*` declarations before/after; `npm run test -- design-system visual-smoke AppBgStyles page-architecture`; `npm run lint`; before/after screenshots.
- Blockers: none
- Closure intent: full-closure.
- Exhaustive Files To Modify:
  - `frontend/src/layouts/LandingLayout.css`
  - `frontend/src/pages/landing/LandingPage.css`
  - `frontend/src/pages/landing/sections/FaqSection.css`
  - `frontend/src/pages/landing/sections/LandingFooter.css`
  - `frontend/src/pages/landing/sections/LandingNavbar.css`
  - `frontend/src/pages/landing/sections/PricingSection.css`
  - `frontend/src/pages/landing/sections/ProblemSection.css`
  - `frontend/src/pages/landing/sections/SocialProofSection.css`
  - `frontend/src/pages/landing/sections/SolutionSection.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/tests/design-system-guards.test.ts` only if the guard needs a stricter finite map.
  - `frontend/src/tests/visual-smoke.test.tsx` only for updated visual ownership expectations.
- Required before/after evidence:
  - Before and after screenshots for desktop/mobile, light/dark, first viewport and mid-page.
  - Scan count of `--landing-*` declarations before/after with a documented target map.
  - `npm run test -- design-system visual-smoke AppBgStyles page-architecture`.
  - `npm run lint`.
- Stop condition: no broad residual category remains; any retained landing variable group is named by owner and consumed by at least one audited section. Remaining color/elevation tuning is explicitly routed to SC-002, not rediscovered as a follow-up ownership issue.

## SC-002 - Aligner les themes visuels landing light/dark

- Source finding: F-002
- Suggested story title: Aligner les themes visuels landing light/dark
- Suggested archetype: design-system-convergence
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, RG-083, RG-084, RG-086, RG-087
- Draft objective: make light and dark modes two variants of the same landing hierarchy with paired surface, text, border and elevation tokens.
- Must include: preserve route/background ownership; keep starfield dark-only; tune light/dark card separation from the same semantic roles created or confirmed by SC-001; produce desktop/mobile screenshots for first viewport, mid-page and mobile menu; include spot contrast checks for primary text, muted text, CTA text and card text in both themes.
- Validation hints: Playwright screenshots before/after; computed contrast spot checks or documented manual contrast values for key text/surface pairs; `npm run test -- design-system visual-smoke AppBgStyles`; no horizontal overflow at 390px and 1440px; `npm run lint`.
- Blockers: SC-001 owner map should land first, or this story must include the owner map before tuning theme values.
- Closure intent: full-closure.
- Exhaustive Files To Modify:
  - `frontend/src/layouts/LandingLayout.css`
  - `frontend/src/tests/visual-smoke.test.tsx` only if the accepted visual contract becomes stricter.
  - Section CSS files only if SC-001 proves a section is consuming the wrong semantic role; no broad section rewrite is authorized by this candidate.
- Required before/after evidence:
  - Screenshots matching this audit's `screenshots/*.png` set.
  - Runtime metrics proving no horizontal overflow.
  - Guard tests and lint.
- Stop condition: desktop and mobile light/dark screenshots show the same hierarchy, key text/surface pairs have documented contrast, and no new page-level background or inline style is introduced.

## SC-003 - Simplifier le hero preview de la landing

- Source finding: F-003.
- Suggested story title: Simplifier le hero preview de la landing
- Suggested archetype: runtime-simplification
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, accessibility/reduced-motion guardrails
- Draft objective: remove or strictly gate the 80ms React interval in `HeroSection`.
- Must include: keep the hero preview visually useful without a continuously running React state loop, or disable the loop when `prefers-reduced-motion` is active; avoid canvas/WebGL/new dependencies; preserve analytics on CTA clicks.
- Validation hints: scan for `window.setInterval` in `frontend/src/pages/landing`; first-viewport screenshots in light/dark; `npm run test -- LandingPage visual-smoke`; `npm run lint`.
- Blockers: none
- Closure intent: full-closure.
- Exhaustive Files To Modify:
  - `frontend/src/pages/landing/sections/HeroSection.tsx`
  - `frontend/src/pages/landing/LandingPage.css` if CSS-only animation replaces React state.
  - `frontend/src/tests/visual-smoke.test.tsx` or a focused hero test if behavior is guarded.
- Required before/after evidence:
  - Targeted scan for `window.setInterval` in `frontend/src/pages/landing`.
  - First-viewport screenshots in light/dark.
  - `npm run test -- LandingPage visual-smoke`.
  - `npm run lint`.
- Stop condition: no active unguarded interval remains in landing decorative UI.

## SC-004 - Extraire le proprietaire SEO/head de la landing

- Source finding: F-004.
- Suggested story title: Extraire le proprietaire SEO/head de la landing
- Suggested archetype: ownership-routing-refactor
- Primary domain: frontend-landing-page
- Required contracts: No Legacy / DRY, route/page ownership
- Draft objective: make `LandingPage` a content composition route and move head/JSON-LD mutation to a small canonical owner.
- Must include: remove story-era `AC*` comments from runtime code; ensure meta description, OG tags, canonical and JSON-LD are added/updated and cleaned deterministically; do not add a head-management dependency unless justified.
- Validation hints: source scan for `document.` in `LandingPage.tsx`; test proving head tags are set and cleaned; `npm run test -- LandingPage`; `npm run lint`.
- Blockers: none
- Closure intent: full-closure.
- Exhaustive Files To Modify:
  - `frontend/src/pages/landing/LandingPage.tsx`
  - Optional new file under `frontend/src/pages/landing/` or `frontend/src/utils/` for a small head helper, if the implementation proves it reduces complexity.
  - Focused tests under `frontend/src/tests/` for head behavior.
- Required before/after evidence:
  - Source scan for `document.` in `LandingPage.tsx`.
  - Test proving head tags are set and cleaned.
  - `npm run test -- LandingPage`.
  - `npm run lint`.
- Stop condition: `LandingPage.tsx` no longer owns raw document head mutation logic; no compatibility wrapper or fallback remains.

## Deferred Non-Domain Context

- None. The findings are in the audited landing domain.

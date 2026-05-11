# Audit Report - frontend-landing-page - 2026-05-11-1841

## Scope

- Domain key: `frontend-landing-page`.
- Target: public landing route `/`, `LandingLayout`, `LandingRedirect`, `LandingPage`, `LandingHead`, landing section components, landing CSS, visual runtime screenshots and landing guard tests.
- Archetype used: bounded frontend No Legacy / DRY, visual ownership and test-guard coverage audit.
- Mode: read-only for application code. Only audit artifacts and screenshots were written under this folder.

## Domain Closure Status

`open`: no High/Critical issue remains, and the previous four landing remediation stories are closed under current evidence. The domain remains open only for bounded follow-up improvements: simplify the hero visual construction, clarify the light/dark/mobile-menu visual contract and add a visual-complexity guard.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-landing-page/2026-05-11-1706`
- `_condamad/stories/CS-139-refactoriser-ownership-css-landing`
- `_condamad/stories/CS-140-aligner-themes-visuels-landing-light-dark`
- `_condamad/stories/CS-141-simplifier-hero-preview-landing`
- `_condamad/stories/CS-142-extraire-proprietaire-seo-head-landing`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`

Prior finding classification:

| Prior finding / story | Current status | Evidence | Notes |
|---|---|---|---|
| 2026-05-11-1706 F-001 / CS-139 CSS ownership too broad | superseded | E-003, E-008, E-017 | Owner map exists and is guarded; residual complexity is now tracked by narrower hero/theme findings F-001/F-002 in this audit. |
| 2026-05-11-1706 F-002 / CS-140 light/dark divergence | active with narrower scope | E-003, E-015, E-016 | Contrast/overflow evidence exists, but visual screenshots still show noisy light/dark treatment and mobile menu glow. |
| 2026-05-11-1706 F-003 / CS-141 hero JS timer | closed | E-003, E-007, E-010, E-013 | No JS timer remains in landing. Residual CSS motion is a new narrower concern. |
| 2026-05-11-1706 F-004 / CS-142 SEO/head owner | closed | E-003, E-005, E-006, E-011, E-013 | Raw head mutation moved out of `LandingPage.tsx` into `LandingHead.tsx` and is tested. |

## Applicable Guardrails

- RG-083: dark mode surfaces must not regress to unclassified light surfaces.
- RG-084: global background remains canonical through `--premium-app-bg`.
- RG-085: dark astral background remains the single dark global background.
- RG-086: landing must not recreate a dedicated `app-bg--landing` background mount.
- RG-087: global background remains viewport-fixed.

## Findings Summary

- F-001 Medium: hero presentation remains over-complex after JS timer removal.
- F-002 Medium: light/dark visual style is classified but still visually noisy.
- F-003 Low: no guard bounds visual-complexity regression.
- F-004 Info: prior critical landing regressions are closed.

## Visual Audit Notes

Current screenshots are stored under `screenshots/`.

- Desktop light top: clean composition, but large pale gradients and glass surfaces blend together; the hero preview has many simultaneous panels.
- Desktop dark top: hierarchy is stronger and text contrast is good, but the preview still feels like a full mini-dashboard rather than one product signal.
- Desktop mid light/dark: no overflow, but the sticky nav partly dominates the top of the captured mid viewport and section cards continue the same translucent-card vocabulary.
- Mobile light/dark top: no horizontal overflow; first viewport is readable but long and dominated by stacked pills/buttons before the product preview appears.
- Mobile menu light/dark: the menu works, but the large blurred glow behind the links and CTA area is the clearest rough visual artifact.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/app/routes.tsx` `/` landing branch | used | E-004, E-018 | Route tree mounts the landing branch through `LandingLayout` and `LandingRedirect`. | Source/guard evidence only; route table was not dumped separately. |
| `frontend/src/app/guards/LandingRedirect.tsx` | used | E-004, E-018 | Lazy-loads `LandingPage` and handles token redirect for `/`. | `Suspense fallback={null}` is outside visual findings. |
| `frontend/src/layouts/LandingLayout.tsx` | used | E-004, E-018 | Owns landing wrapper, skip link, navbar, main outlet and footer. | None. |
| `frontend/src/layouts/LandingLayout.css` | used | E-008, E-017 | Owns canonical landing layout/theme groups. | Per-variable liveness is not fully proven; group-level ownership is guarded. |
| `frontend/src/pages/landing/LandingPage.tsx` | used | E-005, E-011 | Composes landing sections and analytics view event; no raw document head ownership remains. | None. |
| `frontend/src/pages/landing/LandingHead.tsx` | used | E-006, E-011, E-013 | Route-local owner for SEO/head side effects and cleanup. | DOM-effect owner is intentionally route-local, not shared app infrastructure. |
| `frontend/src/pages/landing/LandingPage.css` | used | E-008, E-009, E-016 | Active hero/page CSS owner; source of residual hero complexity. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/HeroSection.tsx` | used | E-007, E-010, E-013 | Active hero section; CTA analytics preserved and no JS timer. | CSS motion remains in `LandingPage.css`. |
| `frontend/src/pages/landing/sections/SocialProofSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | Runtime screenshot does not isolate by component name. |
| `frontend/src/pages/landing/sections/SocialProofSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/TestimonialsSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/TestimonialsSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/ProblemSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/ProblemSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/SolutionSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/SolutionSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/PricingSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/PricingSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/FaqSection.tsx` | used | E-004, E-005 | Imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/FaqSection.css` | used | E-008 | Active section stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/LandingNavbar.tsx` | used | E-004, E-015, E-018 | Active landing navigation, language menu and mobile menu owner. | Visual issue concerns CSS treatment, not TSX ownership. |
| `frontend/src/pages/landing/sections/LandingNavbar.css` | used | E-008, E-009, E-016 | Active navigation/mobile menu stylesheet; source of menu glow/noise. | Per-selector liveness not fully proven. |
| `frontend/src/pages/landing/sections/LandingFooter.tsx` | used | E-004 | Rendered by `LandingLayout`. | None. |
| `frontend/src/pages/landing/sections/LandingFooter.css` | used | E-008 | Active footer stylesheet. | Per-selector liveness not fully proven. |
| `frontend/src/tests/LandingPage.test.tsx` | test-only | E-013 | Focused DOM tests for composition, CTA analytics and SEO/head behavior. | None. |
| `frontend/src/tests/visual-smoke.test.tsx` | test-only | E-013 | Guards landing token-backed CSS and zero JS timer. | Does not currently bound CSS animation/filter volume. |
| `frontend/src/tests/design-system-guards.test.ts` | test-only | E-013, E-017 | Guards finite landing owner groups and design-system constraints. | Complexity budget is not yet guarded. |
| `frontend/src/tests/AppBgStyles.test.ts` | test-only | E-013 | Guards global background and `app-bg--landing` absence. | None. |
| `frontend/src/tests/page-architecture-guards.test.ts` | test-only | E-013, E-018 | Guards route/layout ownership. | None. |
| `frontend/src/tests/page-architecture-allowlist.ts` | test-only | E-018 | Classifies landing page/section ownership. | None. |
| `frontend/src/tests/component-usage-guards.test.ts` | test-only | E-018 | Classifies component usage exceptions relevant to landing. | None. |

## No Legacy / DRY / Boundary Notes

- No active `app-bg--landing` background variant was found.
- No inline style hit was found in the audited landing/layout surface.
- No JS timer remains in `frontend/src/pages/landing`.
- Raw `document.` usage is confined to `LandingHead.tsx`; `LandingPage.tsx` is no longer the head owner.
- DRY concern is now visual responsibility density, not duplicate files.
- Boundary concern is low: route/page/head owners are explicit and guarded.

## Closure Analysis

Active implementation findings:

- F-001: full surface is `HeroSection.tsx`, `LandingPage.css`, focused tests/visual-smoke/design-system guard updates.
- F-002: full surface is landing theme CSS and mobile menu CSS, plus visual-smoke/design-system guard updates.
- F-003: full surface is test/guard files; no application file is required unless combined with F-001/F-002.

Closed findings:

- Prior F-003 JS timer is closed by E-007, E-010 and E-013.
- Prior F-004 SEO/head owner is closed by E-005, E-006, E-011 and E-013.
- Background/layout invariants are closed by E-012, E-013, E-015 and E-018.

Deferred non-domain concerns:

- None.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`: PASS, 132 tests.
- `npm run lint`: PASS.
- Runtime screenshot capture: PASS at `http://127.0.0.1:5173/`.
- No separate audit validation script was required; validation evidence is recorded in `01-evidence-log.md`.

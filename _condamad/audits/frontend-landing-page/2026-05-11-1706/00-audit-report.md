# Audit Report - frontend-landing-page

## Scope

- Domain key: `frontend-landing-page`.
- Target: public landing route `/`, `LandingLayout`, `LandingRedirect`, `LandingPage`, landing section components, landing CSS and visual runtime screenshots.
- Archetype used: bounded frontend No Legacy / DRY and visual ownership audit.
- Mode: read-only for application code. Only audit artifacts and screenshots were written under this folder.

## Domain Closure Status

`open`: implementation stories remain for the audited domain. The route/layout/background invariants are closed and guarded, but the landing visual construction and a few page-level responsibilities need refactor stories.

## Prior Audit And Story History Consulted

- `_condamad/audits/frontend-layouts/2026-05-08-1405`
- `_condamad/audits/frontend-layouts/2026-05-08-2026`
- `_condamad/audits/frontend-layouts/2026-05-08-2227`
- `_condamad/audits/frontend-design-system/2026-05-07-1730`
- `_condamad/audits/frontend-app-css-standardization/2026-05-09-1753`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`

Prior finding classification:

| Prior finding / story | Current status | Evidence | Notes |
|---|---|---|---|
| Landing layout bypass from frontend-layouts 2026-05-08-1405 F-002 / CS-104 | closed | E-002, E-003, E-010 | `/` is mounted under `LandingLayout`; guard tests pass. |
| Landing literal/token cluster from CS-085 | closed-with-residual-complexity | E-002, E-005, E-006, E-010 | Literals are centralized and guarded, but the owner block is now too broad for precise refactor work. |
| Global background landing variant removal RG-084/RG-086/RG-087 | closed | E-001, E-003, E-010 | No `app-bg--landing`; root canonical background is preserved. |

## Applicable Guardrails

- RG-083: dark mode surfaces must not regress to unclassified light surfaces.
- RG-084: global background remains canonical through `--premium-app-bg`.
- RG-086: landing must not recreate a dedicated background mount.
- RG-087: global background remains viewport-fixed.

## Findings Summary

- F-001 High: landing visual ownership is too broad.
- F-002 Medium: light and dark visual systems diverge.
- F-003 Medium: hero live preview uses unnecessary runtime state.
- F-004 Medium: page-level SEO/head mutation lacks a small canonical owner.
- F-005 Info: layout/background/design-system guards remain green.

## Visual Audit Notes

The captured first viewport confirms a polished but overloaded composition:

- Desktop light: the hero has strong brand recognition, but many surfaces are pale glass on a pale background, making hierarchy depend heavily on purple accents.
- Desktop dark: the starfield becomes a dominant visual layer, while cards and panels are more transparent and less differentiated.
- Mid-page light/dark: section cards preserve layout, but dark mode loses local surface separation and light mode looks washed out.
- Mobile: no horizontal overflow, but the first viewport is long and dense; the hero visual is pushed below the fold, and the top stack uses many pill/card surfaces.
- Mobile menu: the menu is usable in both themes, but it is another isolated surface vocabulary that contributes to the large token owner.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `frontend/src/app/routes.tsx` `/` landing branch | used | E-003, E-010 | Runtime route owner nests landing under `LandingLayout`. | Full router runtime table not separately dumped; source and tests were used. |
| `frontend/src/app/guards/LandingRedirect.tsx` | used | E-003, E-007, E-010 | Decides auth-token redirect and lazy-loads landing. | None. |
| `frontend/src/layouts/LandingLayout.tsx` | used | E-003, E-010 | Owns wrapper, skip link, navbar, main and footer. | None. |
| `frontend/src/layouts/LandingLayout.css` | used | E-004, E-005, E-006, E-010 | Landing semantic style owner; active but over-broad. | Precise unused-variable detection was not run; classification is runtime/source use, not per-variable liveness. |
| `frontend/src/pages/landing/LandingPage.tsx` | used | E-004, E-007, E-010 | Composes all landing sections and owns current head mutations. | None. |
| `frontend/src/pages/landing/LandingPage.css` | used | E-004, E-006, E-010 | Owns hero and page-level landing CSS. | None. |
| `frontend/src/pages/landing/sections/HeroSection.tsx` | used | E-004, E-007, E-008, E-013 | First viewport hero section imported and rendered by `LandingPage`. | None. |
| `frontend/src/pages/landing/sections/SocialProofSection.tsx` | used | E-004, E-008, E-013 | Imported and rendered by `LandingPage` as social proof section. | None. |
| `frontend/src/pages/landing/sections/SocialProofSection.css` | used | E-004, E-006, E-008 | Styles social proof cards. | None. |
| `frontend/src/pages/landing/sections/TestimonialsSection.tsx` | used | E-004, E-002, E-013 | Reattached by prior product/layout decision and imported/rendered by `LandingPage`. | Runtime screenshot does not isolate this section by name, but import/render evidence proves ownership. |
| `frontend/src/pages/landing/sections/TestimonialsSection.css` | used | E-004, E-006 | Styles testimonial/case surfaces. | None. |
| `frontend/src/pages/landing/sections/ProblemSection.tsx` | used | E-004, E-008, E-013 | Imported and rendered by `LandingPage`; visible in mid-page screenshot as problem/comparison section. | None. |
| `frontend/src/pages/landing/sections/ProblemSection.css` | used | E-004, E-006, E-008 | Styles problem/comparison cards. | None. |
| `frontend/src/pages/landing/sections/SolutionSection.tsx` | used | E-004, E-013 | Imported and rendered by `LandingPage` as solution/how-it-works section. | Runtime screenshots are supplementary; import/render evidence is the classification basis. |
| `frontend/src/pages/landing/sections/SolutionSection.css` | used | E-004, E-006 | Styles solution cards. | None. |
| `frontend/src/pages/landing/sections/PricingSection.tsx` | used | E-004, E-013 | Imported and rendered by `LandingPage` as pricing section. | Runtime screenshots are supplementary; import/render evidence is the classification basis. |
| `frontend/src/pages/landing/sections/PricingSection.css` | used | E-004, E-006 | Styles pricing cards and CTA. | None. |
| `frontend/src/pages/landing/sections/FaqSection.tsx` | used | E-004, E-013 | Imported and rendered by `LandingPage` as FAQ section. | None. |
| `frontend/src/pages/landing/sections/FaqSection.css` | used | E-004, E-006 | Styles FAQ accordion. | None. |
| `frontend/src/pages/landing/sections/LandingNavbar.tsx` | used | E-004, E-007, E-008 | Owns landing navigation, language dropdown and mobile menu state. | None. |
| `frontend/src/pages/landing/sections/LandingNavbar.css` | used | E-004, E-006, E-008 | Styles desktop and mobile navigation. | None. |
| `frontend/src/pages/landing/sections/LandingFooter.tsx` | used | E-004 | Owned by `LandingLayout`. | None. |
| `frontend/src/pages/landing/sections/LandingFooter.css` | used | E-004, E-006 | Styles footer. | None. |
| `frontend/src/tests/AppBgStyles.test.ts` | test-only | E-010 | Guard test for background invariants. | Out of implementation scope except guard updates. |
| `frontend/src/tests/design-system-guards.test.ts` | test-only | E-010 | Guard test for token/design-system invariants. | Out of implementation scope except stricter landing map updates. |
| `frontend/src/tests/page-architecture-guards.test.ts` | test-only | E-010 | Guard test for layout ownership. | Out of implementation scope. |
| `frontend/src/tests/visual-smoke.test.tsx` | test-only | E-010 | Guard test for visual-smoke expectations. | Out of implementation scope except expected snapshots/ownership checks. |

## No Legacy / DRY / Boundary Notes

- No active landing layout bypass was found.
- No dedicated `app-bg--landing` background variant was found.
- No inline style hit was found in the audited landing source scan.
- The main DRY issue is not duplicated files; it is duplicated visual decision ownership hidden behind one large token namespace.
- The main boundary issue is page/section components owning infrastructure-like side effects (`document.*`) and decorative runtime loops.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture`: PASS.
- `npm run lint`: PASS.
- Vite local runtime: PASS at `http://127.0.0.1:5173/`.

## Open Implementation Surface

- SC-001 closes F-001.
- SC-002 closes F-002.
- SC-003 closes F-003.
- SC-004 closes F-004.

# CS-146 - Final evidence

Status: DONE

## Resume

La landing corrige les defauts responsive et accessibilite critiques sans changer le fond global, le SEO/head, les routes, le pricing ou le backend.

## Files changed

- `frontend/src/pages/landing/sections/LandingNavbar.tsx`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/tests/LandingPage.test.tsx`
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-before.md`
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/landing-responsive-a11y-after.md`
- `_condamad/stories/CS-146-corriger-responsive-accessibilite-landing/generated/**`
- `_condamad/stories/story-status.md`

## AC validation

- AC1 PASS: `768x1024` et `390x844` n'ont plus de scroll horizontal.
- AC2 PASS: focus initial, trap Tab/Shift+Tab, Escape, scroll lock et restauration focus testes.
- AC3 PASS: `#social-proof` mobile est a `y=1524.234375`, sous le seuil `y=1560`.
- AC4 PASS: H1 unique avec nom accessible `Votre guide astrologique personnel - Toujours disponible`.
- AC5 PASS: interdits landing absents ou hits existants classes par `RG-088`.
- AC6 PASS: lint et tests cibles OK.

## Commands run

- `npm run test -- LandingPage` - PASS
- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS
- `npm run lint` - PASS
- `git diff --check` - PASS
- `rg -n "app-bg--landing|style=" src/pages/landing src/layouts` - PASS, zero hit
- `rg -n -- "--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts` - PASS, zero hit
- `rg -n "\bfetch\(|axios\." src` - PASS_WITH_CLASSIFICATION, hit attendu dans `src/api/client.ts`
- `rg -n "\bany\b" src/pages/landing src/tests/LandingPage.test.tsx` - PASS, zero hit
- `rg -n "style=\{\{" src/pages/landing src/layouts` - PASS, zero hit
- `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css` - PASS_WITH_CLASSIFICATION, hits existants gardes par `design-system-guards.test.ts`
- Verification Playwright runtime reviewer sur `http://127.0.0.1:5176/` - PASS, desktop/tablette/mobile sans overflow, H1 accessible OK, `#social-proof` mobile `y=1524.234375`, focus confine et Escape restaure le bouton.

## Not run

- `npm run test:e2e` - NOT_RUN: la story demandait le test runtime local cible; les mesures Playwright ad hoc et tests Vitest couvrent le flux modifie. Risque residuel: les specs E2E globales hors landing n'ont pas ete rejouees.

## Guardrails

- `RG-083` PASS
- `RG-084` PASS
- `RG-085` PASS
- `RG-086` PASS
- `RG-087` PASS
- `RG-088` PASS

## Risks

- Le menu desktop reste volontairement masque jusqu'a `1023px`; c'est le changement de comportement attendu pour supprimer l'overflow tablette.
- `npm run test:e2e` global non rejoue; risque residuel limite car le flux modifie est couvert par tests cibles et verification navigateur runtime.

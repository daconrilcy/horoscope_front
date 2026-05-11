# Preuve after CS-141 - hero preview landing

## Changement

- `HeroSection.tsx` n'importe plus `useEffect`, `useMemo` ni `useState`.
- La boucle `window.setInterval` est supprimee.
- Le preview affiche les textes complets et conserve les etats actifs via classes CSS.
- Les cycles decoratifs restants sont CSS-only dans `LandingPage.css`, sous `@media (prefers-reduced-motion: no-preference)`.

## Guards

- `frontend/src/tests/visual-smoke.test.tsx` verifie zero timer dans `HeroSection.tsx`.
- Le meme test verifie la presence de `track("hero_cta_click"` et `track("secondary_cta_click"`.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS, 131 tests.
- `npm run lint` - PASS.
- `rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" src/pages/landing` - PASS, zero-hit.
- `rg -n "hero_cta_click|secondary_cta_click|prefers-reduced-motion" src/pages/landing src/tests` - PASS.

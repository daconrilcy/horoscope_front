# Baseline CS-141 - hero preview landing

Baseline capturee avant patch.

- Fichier initial: `frontend/src/pages/landing/sections/HeroSection.tsx`.
- Scan initial: `rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" frontend\src\pages\landing`.
- Hit initial: `HeroSection.tsx` executait `window.setInterval(updateLiveState, 80)`.
- CTA initiaux: `hero_cta_click` et `secondary_cta_click` presents dans `HeroSection.tsx`.
- CSS initial: `LandingPage.css` contenait deja `@media (prefers-reduced-motion: reduce)`.

## Risque initial

Le hero utilisait une boucle React decorative permanente pour une information marketing qui peut etre statique ou CSS-only.

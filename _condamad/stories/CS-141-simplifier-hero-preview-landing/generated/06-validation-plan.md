# Validation plan CS-141

- `npm run test -- LandingPage visual-smoke`
- `npm run lint`
- `rg -n "window\.setInterval|setInterval\(|requestAnimationFrame|setTimeout\(" src/pages/landing`
- `rg -n "hero_cta_click|secondary_cta_click|prefers-reduced-motion" src/pages/landing src/tests`
- `rg -n "style=|canvas|WebGL|three" src/pages/landing package.json`

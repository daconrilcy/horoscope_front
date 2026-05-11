# Landing Conversion After

Preuve capturée le 2026-05-11 sur `http://127.0.0.1:5173/` via Vite local et Playwright Chromium headless après implémentation.

## Runtime Measurements

| Viewport | `.hero-section` | `.hero-ctas` | `.hero-proof-strip` | `.hero-visual` | `.hero-device` | `#social-proof` | `#pricing` | `#faq` | Overflow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `390x844` | `y=98 h=1354 bottom=1452` | `y=586 h=125 bottom=711` | `y=723 h=93 bottom=816` | `y=818 h=600 bottom=1418` | `y=833 h=570 bottom=1403` | `y=1452 h=943 bottom=2395` | `y=4787 h=2049 bottom=6837` | `y=6837 h=1444 bottom=8281` | `0` |
| `768x1024` | `y=98 h=1418 bottom=1516` | `y=716 h=65 bottom=781` | `y=801 h=47 bottom=848` | `y=941 h=523 bottom=1464` | `y=962 h=481 bottom=1443` | `y=1516 h=795 bottom=2311` | `y=4254 h=2000 bottom=6253` | `y=6253 h=1115 bottom=7369` | `0` |
| `1440x1000` | `y=94 h=896 bottom=990` | `y=790 h=65 bottom=855` | `display=none` | `y=225 h=619 bottom=844` | `y=246 h=577 bottom=823` | `y=990 h=497 bottom=1487` | `y=2705 h=890 bottom=3595` | `y=3595 h=1166 bottom=4761` | `0` |

## Before / After Diff

- Mobile `390x844`: `.hero-device` passe de `y=901` à `y=833`, donc le shell produit démarre dans le premier viewport.
- Mobile CTA primaire: `.hero-ctas` reste visible, `bottom=711`.
- Preuve compacte: `.hero-proof-strip` visible dans le premier viewport, `y=723 bottom=816`.
- `#social-proof` commence plus tôt (`1524` -> `1452`) sans duplication de la section complète.
- Desktop `1440x1000`: le strip compact reste masque pour ne pas allonger le hero; `#social-proof` reste visible en limite de premier viewport (`y=990`).
- Aucun overflow horizontal sur les trois viewports.

## Captures Persistantes

- Mobile after: `landing-mobile-after.png`
- Tablet after: `landing-tablet-after.png`
- Desktop after: `landing-desktop-after.png`

## Pricing / FAQ

- Liens pricing after: `/register?plan=free`, `/register?plan=basic`, `/register?plan=premium`.
- Source pricing conservée: `getActivePlans()` dans `PricingSection.tsx`.
- Event conservé: `pricing_plan_select`.
- CTA final FAQ conservé: `/register`.
- Hover pricing limité à `@media (min-width: 1024px) and (prefers-reduced-motion: no-preference)`.

## Filter / Motion Inventory

Commande:

```powershell
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
```

Hits after classifiés:

- `src/pages/landing/sections/LandingNavbar.css:99`: `.landing-navbar__shell` `backdrop-filter: blur(14px)`; raison: lisibilité du header sticky; condition de sortie: surface opaque sans effet glass.
- `src/pages/landing/sections/LandingNavbar.css:291`: `.landing-navbar__mobile-menu` `backdrop-filter: blur(6px)`; raison: séparation du menu mobile; condition de sortie: panneau mobile pleine page opaque.
- `src/pages/landing/sections/TestimonialsSection.css:14`: `animation: none !important`; exception accessibilité reduced-motion permanente, ignorée par le guard actif.

Filtres supprimés:

- `.landing-navbar__lang`
- `.landing-navbar__lang-dropdown`
- `.social-proof__container`
- `.testimonial-card` standard et WebKit

## Commands

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS, `5` files, `140` tests.
- `npm run test:e2e -- landing-conversion-cs147.spec.ts` - PASS, `2` tests Playwright.
- `npm run lint` - PASS.
- `npm run test` - PASS, `115` files, `1243` tests passed, `8` skipped.
- `rg -n "app-bg--landing|style=" src/pages/landing src/layouts` - PASS, zero hit.
- `rg -n "Cormorant|Petit Formal|Brush Script|font-family:\s*\"" src -g "*.css" -g "*.scss"` - PASS, zero hit.

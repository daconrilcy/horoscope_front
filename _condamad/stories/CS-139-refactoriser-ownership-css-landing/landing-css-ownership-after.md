# Preuve after CS-139 - ownership CSS landing

## Allowed Owner Map

| Groupe `--landing-*` | Owner canonique | Consommateur audite |
|---|---|---|
| `page`, `surface`, `accent`, `shadow`, `radius`, `type`, `cta`, `soft`, `compact` | `frontend/src/layouts/LandingLayout.css` | Layout et sections landing |
| `hero`, `live` | `frontend/src/pages/landing/LandingPage.css` | `HeroSection.tsx` |
| `navbar`, `language`, `mobile`, `overlay` | `frontend/src/pages/landing/sections/LandingNavbar.css` | `LandingNavbar.tsx` |
| `footer`, `text` | `frontend/src/pages/landing/sections/LandingFooter.css` | `LandingFooter.tsx` |
| `icon`, `problem` | `frontend/src/pages/landing/sections/ProblemSection.css` | `ProblemSection.tsx` |
| `rating` | `frontend/src/pages/landing/sections/TestimonialsSection.css` | `TestimonialsSection.tsx` |

## Guards

- `frontend/src/tests/design-system-guards.test.ts` ajoute `LANDING_OWNER_GROUPS` et bloque les groupes non classes.
- Groupes interdits: `misc`, `common`, `temp`, `shared`, `base`, `general`, `global`.
- `app-bg--landing` reste zero-hit.
- `style=` reste zero-hit sur `src/pages/landing src/layouts`.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS, 131 tests.
- `npm run lint` - PASS.
- `rg -n "app-bg--landing|style=|--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts` - PASS, zero-hit.
- Captures after: `.codex-artifacts/landing-cs139-142/*.png`.

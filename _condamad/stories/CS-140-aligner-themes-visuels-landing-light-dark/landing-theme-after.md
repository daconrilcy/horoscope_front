# Preuve after CS-140 - theme landing light/dark

## Contrast spot

Ratios calcules avec la formule WCAG relative luminance. Les fonds transparents
runtime sont mesures contre les fonds theme representatifs du premier viewport
car le fond global est peint par couches CSS.

| Spot | Theme | Foreground | Background | Ratio |
|---|---|---|---|---:|
| Texte principal hero | light | `rgb(42,35,56)` | `rgb(251,247,255)` | 14.22 |
| Texte muted hero | light | `rgb(70,63,85)` | `rgb(251,247,255)` | 9.44 |
| CTA secondaire | light | `rgb(42,35,56)` | `rgb(255,255,255)` | 15.04 |
| Titre carte summary | light | `rgb(42,35,56)` | `rgb(246,240,255)` | 13.49 |
| Texte principal hero | dark | `rgb(244,238,252)` | `rgb(18,24,50)` | 15.37 |
| Texte muted hero | dark | `rgb(210,202,226)` | `rgb(18,24,50)` | 11.05 |
| CTA secondaire | dark | `rgb(244,238,252)` | `rgb(42,33,67)` | 13.23 |
| Titre carte summary | dark | `rgb(244,238,252)` | `rgb(18,24,50)` | 15.37 |

## Captures after

- Desktop light top/mid: `.codex-artifacts/landing-cs139-142/desktop-light-top.png`, `desktop-light-mid.png`.
- Desktop dark top/mid: `.codex-artifacts/landing-cs139-142/desktop-dark-top.png`, `desktop-dark-mid.png`.
- Mobile light/dark top: `.codex-artifacts/landing-cs139-142/mobile-light-top.png`, `mobile-dark-top.png`.
- Mobile menu light/dark: `.codex-artifacts/landing-cs139-142/mobile-light-menu.png`, `mobile-dark-menu.png`.

## Metrics Playwright

- `desktop-light-top`: `clientWidth=1440`, `scrollWidth=1440`, landing presente, `app-bg--landing=false`.
- `desktop-dark-top`: `clientWidth=1440`, `scrollWidth=1440`, landing presente, `app-bg--landing=false`.
- `desktop-light-mid`: `clientWidth=1440`, `scrollWidth=1440`, landing presente, `app-bg--landing=false`.
- `desktop-dark-mid`: `clientWidth=1440`, `scrollWidth=1440`, landing presente, `app-bg--landing=false`.
- `mobile-light-top`: `clientWidth=390`, `scrollWidth=390`, landing presente, `app-bg--landing=false`.
- `mobile-dark-top`: `clientWidth=390`, `scrollWidth=390`, landing presente, `app-bg--landing=false`.
- `mobile-light-menu`: `clientWidth=390`, `scrollWidth=390`, menu ouvert, `app-bg--landing=false`.
- `mobile-dark-menu`: `clientWidth=390`, `scrollWidth=390`, menu ouvert, `app-bg--landing=false`.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS, 131 tests.
- `npm run lint` - PASS.
- `rg -n "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css` - PASS, zero-hit.
